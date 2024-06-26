from django import forms
from .models import Ingredient, Menu, Order, OrderItem
from django.forms import inlineformset_factory

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name']

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'price', 'category', 'ingredients', 'description', 'image']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table', 'status']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)
        
class PaymentForm(forms.Form):
    amount_paid = forms.DecimalField(max_digits=10, decimal_places=2)
    payment_method = forms.CharField(max_length=50)
