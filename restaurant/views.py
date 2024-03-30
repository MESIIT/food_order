from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
# from .models import Category, Order, Menu, Bill, Ingredient, IngredientQuantity,Transaction, Cart, CartItem, menu_item
from datetime import datetime, timedelta
import json, ast
from django.conf import settings
from .forms import IngredientForm, MenuForm
from django.contrib import messages
from restaurant.models import *
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet, BillForm, PaymentForm

User = settings.AUTH_USER_MODEL

def index(request):
    return HttpResponse("restaurant.html")

def category_summary(request):
    category = Category.objects.all()
    return render(request, 'category_summary.html', {'category': Category})	

def category(request):
    foo = foo.replace('-', ' ') 
    try:
        category = category.objects.get(name=foo)
        menu = menu.objects.filter(category=category)
        return render(request, 'category.html', {'menu':menu, 'category':category})
    except:
        messages.success(request, ("That Category Doesn't Exist..."))
        return redirect('restaurant')

def ingredient(request, pk):
    ingredient_obj = get_object_or_404(Ingredient, id=pk)
    return render(request, 'ingredient.html', {'ingredient': ingredient_obj})

def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ingredient_list')  # Redirect to a page showing all ingredients
    else:
        form = IngredientForm()
    return render(request, 'add_ingredient.html', {'form': form})

def menu(request):
    menus = Menu.objects.all()
    context = {'menus': menus}
    return render(request, 'menu.html', context)

def prepare_food(request, food_item_id):
    if request.method == 'POST':
        # Get the food item
        food_item = Menu.objects.get(pk=food_item_id)
        
        # Check if there are enough ingredients in stock
        for ingredient_quantity in food_item.ingredientquantity_set.all():
            if ingredient_quantity.ingredient.quantity < ingredient_quantity.quantity:
                return HttpResponse("Not enough stock for ingredient: {}".format(ingredient_quantity.ingredient.name))
        
        # Deduct ingredients from stock
        for ingredient_quantity in food_item.ingredientquantity_set.all():
            ingredient_quantity.ingredient.quantity -= ingredient_quantity.quantity
            ingredient_quantity.ingredient.save()
            # Create a transaction for the stock out
            Transaction.objects.create(
                ingredient=ingredient_quantity.ingredient,
                quantity=ingredient_quantity.quantity,
                transaction_type='OUT'
            )
        
        # Food preparation successful
        return HttpResponse("Food prepared successfully!")
    else:
        # Render a form to prepare the food
        food_item = Menu.objects.get(pk=food_item_id)
        context = {'food_item': food_item}
        return render(request, 'prepare_food.html', context)
    
def transaction_detail(request):
    transactions = Transaction.objects.all()  # Retrieve all transactions
    context = {'transactions': transactions}
    return render(request, 'transaction_detail.html', context)

def add_to_cart(request, menu_item_id):
    try:
        menu_item = Menu.objects.get(pk=menu_item_id)
    except Menu.DoesNotExist:
        messages.error(request, "Menu item not found.")
        return redirect('menu')
    
    # Retrieve the ingredient quantities associated with the menu item
    ingredient_quantities = IngredientQuantity.objects.filter(menu_item=menu_item)

    # Check availability of each ingredient
    for ingredient_quantity in ingredient_quantities:
        if ingredient_quantity.ingredient.quantity < ingredient_quantity.quantity:
            # Ingredient not available in sufficient quantity
            messages.error(request, f"Not enough {ingredient_quantity.ingredient.name} in stock.")
            return redirect('menu')
    
    # All ingredients are available, add the menu item to the cart
    cart, created = Cart.objects.get_or_create(user=request.user)  # Assuming you have a user attribute in Cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('menu')

def check_ingredient_availability(self):
        # Iterate over each ingredient quantity of the menu item
        for ingredient_quantity in self.ingredientquantity_set.all():
            if ingredient_quantity.ingredient.quantity < ingredient_quantity.quantity:
                return False  # Ingredient is out of stock
        return True  # All ingredients are in stock

def view_cart(request):
    cart_items = CartItem.objects.all()
    total_price = sum(item.total_price() for item in cart_items)
    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'view_cart.html', context)

def manage_menu(request):
    menu_items = Menu.objects.all().order_by('category__name')
    grouped_menu_items = {}

    for item in menu_items:
        category_name = item.category.name
        if category_name not in grouped_menu_items:
            grouped_menu_items[category_name] = []
        grouped_menu_items[category_name].append(item)

    context = {'grouped_menu_items': grouped_menu_items}
    return render(request, 'manage_menu.html', context)

def view_orders(request):
    orders = Order.objects.all().order_by('table__number')
    grouped_orders = {}

    for order in orders:
        table_number = order.table.number
        if table_number not in grouped_orders:
            grouped_orders[table_number] = []
        grouped_orders[table_number].append(order)

    context = {'grouped_orders': grouped_orders}
    return render(request, 'view_orders.html', context)

def add_menu_item(request):
    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_menu')
    else:
        form = MenuForm()

    return render(request, 'add_menu_item.html', {'form': form})

@login_required
def create_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            order = order_form.save(commit=False)
            order.waiter = request.user
            order.save()

            for form in formset:
                if form.cleaned_data:
                    menu_item = form.cleaned_data['menu_item']
                    quantity = form.cleaned_data['quantity']
                    OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)

            return redirect('order_detail', order_id=order.id)
    else:
        order_form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'create_order.html', {'order_form': order_form, 'formset': formset})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if order_form.is_valid() and formset.is_valid():
            order_form.save()
            formset.save()
            return redirect('order_detail', order_id=order.id)
    else:
        order_form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)
    return render(request, 'update_order.html', {'order_form': order_form, 'formset': formset, 'order': order})

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        return redirect('order_list')
    return render(request, 'delete_order.html', {'order': order})

@login_required
def order_list(request):
    orders = Order.objects.filter(waiter=request.user)
    return render(request, 'order_list.html', {'orders': orders})

def create_bill(request, order_id):
    order = Order.objects.get(pk=order_id)
    
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            total_amount = order.calculate_bill() 
            bill = Bill.objects.create(order=order, total_amount=total_amount)
            return redirect('bill_detail', bill_id=bill.id)
    else:
        form = BillForm()
    
    return render(request, 'create_bill.html', {'form': form, 'order': order})

def generate_bill(request):
    t_number = request.GET.get('table')

    order_for_table = Order.objects.filter(table=t_number, bill_clear=False)
    total_bill = 0
    now = datetime.now()
    now_ist = now + timedelta(hours=5, minutes=30)

    bill_items = []
    c_name = ''
    c_phone = ''
    for o in order_for_table:
        total_bill += int(o.price)
        o.bill_clear = True
        o.save()

        bill_items.append({
            'order_items': o.items_json,
        })
        c_name = o.name
        c_phone = o.phone

    order_dict = {}
    for item in bill_items:
        for key, value in item.items():
            order_items = json.loads(value)
            for pr_key, pr_value in order_items.items():
                order_dict[pr_value[1].lower()] = [
                    pr_value[0], (pr_value[2] * pr_value[0])
                ]
    new_bill = Bill(order_items=order_dict,
                    name=c_name,
                    bill_total=total_bill,
                    phone=c_phone,
                    bill_time=now_ist)
    new_bill.save()
    context = {}
    context = {
        'order_dict': order_dict,
        'bill_total': total_bill,
        'name': c_name,
        'phone': c_phone,
        'inv_id': new_bill.id,
    }
    return render(request, 'generate_bill.html', context)

def view_bills(request):
    if request.user.is_anonymous:
        messages.error(request, 'You Must be an admin user to view this!')
        return redirect('')
    all_bills = Bill.objects.all().order_by('-bill_time')
    for b in all_bills:
        b.order_items = ast.literal_eval(b.order_items)
    context = {'bills': all_bills}
    return render(request, 'bills.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Payment
from .forms import PaymentForm

def payment_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    total_amount = order.calculate_bill()  # Calculate total amount for the order

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data['amount_paid']
            payment_method = form.cleaned_data['payment_method']
            
            # Perform additional validation if necessary
            if amount_paid >= total_amount:
                try:
                    payment = Payment.objects.get(order=order)
                    payment.amount_paid = amount_paid
                    payment.payment_method = payment_method
                    payment.save()
                except Payment.DoesNotExist:
                    payment = Payment.objects.create(order=order, amount_paid=amount_paid, payment_method=payment_method)
                # Perform any additional actions after payment creation
                return redirect('payment_success')  # Redirect to payment success page
            else:
                form.add_error('amount_paid', 'Amount paid must be greater than or equal to the total amount.')
    else:
        form = PaymentForm()
    return render(request, 'payment.html', {'form': form, 'order': order, 'total_amount': total_amount})

def payment_success(request):
    return render(request, 'payment_success.html')