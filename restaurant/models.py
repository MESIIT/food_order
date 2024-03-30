from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

class Table(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'tables'

class Ingredient(models.Model):
    name = models.CharField(max_length = 100)
    price = models.DecimalField(default=0, decimal_places = 2, max_digits = 6)
    quantity = models.DecimalField(default=0, decimal_places = 2, max_digits = 6)

    UNIT_CHOICES = [
        ('gram', 'Gram'),
        ('kilogram', 'Kilogram'),
        ('milliliter', 'Milliliter'),
        ('liter', 'Liter'),
    ]
    unit_of_measurement = models.CharField(max_length=50, choices=UNIT_CHOICES, default='gram')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'ingredients'

class Menu(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # ingredient = models.CharField(max_length=250, default='onion')
    ingredients = models.ManyToManyField(Ingredient)
    description = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to='uploads/menu/')

    def __str__(self):
        return self.name

class IngredientQuantity(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    UNIT_CHOICES = [
        ('gram', 'Gram'),
        ('kilogram', 'Kilogram'),
        ('milliliter', 'Milliliter'),
        ('liter', 'Liter'),
    ]
    unit_of_measurement = models.CharField(max_length=50, choices=UNIT_CHOICES, default='gram')

class Transaction(models.Model):
    TRANSACTION_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    UNIT_CHOICES = [
        ('gram', 'Gram'),
        ('kilogram', 'Kilogram'),
        ('milliliter', 'Milliliter'),
        ('liter', 'Liter'),
    ]
    unit_of_measurement = models.CharField(max_length=50, choices=UNIT_CHOICES, default ='gram')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.transaction_type == 'IN':
            self.ingredient.quantity += self.quantity
        elif self.transaction_type == 'OUT':
            self.ingredient.quantity -= self.quantity
        self.ingredient.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.quantity} {self.ingredient.unit_of_measurement} - {self.timestamp}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('received', 'Received'),
        ('food_prepared', 'Food Prepared'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE, default=1)
    waiter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_waiter': True}, default=1)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    def calculate_bill(self):
        total = 0
        order_items = self.orderitem_set.all()
        for order_item in order_items:
            total += order_item.menu_item.price * order_item.quantity
        return total

    def __str__(self):
        return f"Order {self.id} - Table {self.table}, Waiter: {self.waiter.username}, Status: {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    def subtotal(self):
        return self.menu_item.price * self.quantity
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class KitchenOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status_choices = [
        ('received', 'Received'),
        ('food_prepared', 'Food Prepared'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='received')

    def prepare_food(self):
        if self.status == 'received':
            self.status = 'food_prepared'
            self.order.status = 'Food Prepared'
            self.order.save()
            self._decrease_ingredient_stock() 
            self.save()

    def _decrease_ingredient_stock(self):
        for item in self.order.orderitem_set.all():
            for ingredient in item.menu_item.ingredients.all():
                ingredient.stock -= item.quantity
                ingredient.save()

    def get_menu_items(self):
        return self.order.orderitem_set.all()

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    UNIT_CHOICES = [
        ('cash', 'Cash'),
        ('visa', 'Visa'),
        ('telebirr', 'Telebirr'),
        ('mobilebank', 'Mobile_Bank'),
    ]
    payment_method = models.CharField(max_length=50, choices=UNIT_CHOICES)
    payment_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment for Order {self.order.id} - Amount Paid: {self.amount_paid}, Method: {self.payment_method}"

    def get_order_details(self):
        order_items = self.order.orderitem_set.all()
        order_details = []
        total_amount = 0
        
        for item in order_items:
            item_total = item.subtotal()
            total_amount += item_total
            order_details.append({
                'menu_item': item.menu_item.name,
                'quantity': item.quantity,
                'price_per_item': item.menu_item.price,
                'subtotal': item_total
            })
        
        return order_details, total_amount