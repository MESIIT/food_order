from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import User
from django.http import request

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
    ingredient = models.CharField(max_length=250, default='onion')
    description = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to='uploads/menu/')

    def __str__(self):
        return self.name

class IngredientQuantity(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)  # Renamed from food_item
    quantity = models.IntegerField()
    UNIT_CHOICES = [
        ('gram', 'Gram'),
        ('kilogram', 'Kilogram'),
        ('milliliter', 'Milliliter'),
        ('liter', 'Liter'),
    ]
    unit_of_measurement = models.CharField(max_length=50, choices=UNIT_CHOICES, default='gram')
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE, default=1)
    waiter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_waiter': True}, default=1)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def calculate_bill(self):
        total = 0
        order_items = self.orderitem_set.all()  # Assuming related name is 'orderitem_set'
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

        super().save(*args, **kwargs)  # Call the original save method after updating ingredient quantity

    def __str__(self):
        return f"{self.transaction_type} - {self.quantity} {self.ingredient.unit_of_measurement} - {self.timestamp}"

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class Bill(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Example field definition
    # Other fields in your Bill model
    payment_timestamp = models.DateTimeField(default=timezone.now)

    def calculate_bill(self):
        total = 0
        # Retrieve all items associated with the bill
        items = self.billitem_set.all()  # Assuming related name is 'billitem_set'
        # Iterate over each item and sum up the prices
        for item in items:
            total += item.price * item.quantity
        return total

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment for Order {self.order.id} - Amount Paid: {self.amount_paid}, Method: {self.payment_method}"