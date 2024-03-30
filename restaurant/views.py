from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from .forms import IngredientForm, MenuForm
from django.contrib import messages
from restaurant.models import *
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, Payment
from .forms import OrderForm, OrderItemFormSet, PaymentForm

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
            return redirect('ingredient_list')  
    else:
        form = IngredientForm()
    return render(request, 'add_ingredient.html', {'form': form})

def menu(request):
    menus = Menu.objects.all()
    context = {'menus': menus}
    return render(request, 'menu.html', context)

def prepare_food(request, food_item_id):
    if request.method == 'POST':
        food_item = Menu.objects.get(pk=food_item_id)
        for ingredient_quantity in food_item.ingredientquantity_set.all():
            if ingredient_quantity.ingredient.quantity < ingredient_quantity.quantity:
                return HttpResponse("Not enough stock for ingredient: {}".format(ingredient_quantity.ingredient.name))
        for ingredient_quantity in food_item.ingredientquantity_set.all():
            ingredient_quantity.ingredient.quantity -= ingredient_quantity.quantity
            ingredient_quantity.ingredient.save()
            Transaction.objects.create(
                ingredient=ingredient_quantity.ingredient,
                quantity=ingredient_quantity.quantity,
                transaction_type='OUT'
            )
        return HttpResponse("Food prepared successfully!")
    else:
        food_item = Menu.objects.get(pk=food_item_id)
        context = {'food_item': food_item}
        return render(request, 'prepare_food.html', context)
    
def transaction_detail(request):
    transactions = Transaction.objects.all()
    context = {'transactions': transactions}
    return render(request, 'transaction_detail.html', context)

def check_ingredient_availability(self):
        for ingredient_quantity in self.ingredientquantity_set.all():
            if ingredient_quantity.ingredient.quantity < ingredient_quantity.quantity:
                return False
        return True

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

def kitchen_order_detail(request, kitchen_order_id):
    kitchen_order = get_object_or_404(KitchenOrder, pk=kitchen_order_id)
    menu_items = kitchen_order.get_menu_items()

    if request.method == 'POST':
        kitchen_order.prepare_food()

    return render(request, 'kitchen_order_detail.html', {'kitchen_order': kitchen_order, 'menu_items': menu_items})

def payment_details(request, payment_id):
    payment = Payment.objects.get(pk=payment_id)
    order_details, total_amount = payment.get_order_details()
    return render(request, 'payment_details.html', {'order_details': order_details, 'total_amount': total_amount})

def payment_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    total_amount = order.calculate_bill()
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data['amount_paid']
            payment_method = form.cleaned_data['payment_method']           
            if amount_paid >= total_amount:
                try:
                    payment = Payment.objects.get(order=order)
                    payment.amount_paid = amount_paid
                    payment.payment_method = payment_method
                    payment.save()
                except Payment.DoesNotExist:
                    payment = Payment.objects.create(order=order, amount_paid=amount_paid, payment_method=payment_method)
                
                # Update order status here, assuming there's a field 'status' in Order model
                order.status = 'Paid'
                order.save()
                
                return redirect('payment_success')
            else:
                form.add_error('amount_paid', 'Amount paid must be greater than or equal to the total amount.')
    else:
        form = PaymentForm()
    
    return render(request, 'payment.html', {'form': form, 'order': order, 'total_amount': total_amount})

def payment_success(request):
    return render(request, 'payment_success.html')

def order_report(request, table_id=None):
    if table_id:
        orders = Order.objects.filter(table_id=table_id)
    else:
        orders = Order.objects.all()
    return render(request, 'order_report.html', {'orders': orders})