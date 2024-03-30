from django.contrib import admin
from .models import Category, Table, Ingredient, Menu, Order, OrderItem, IngredientQuantity, Transaction, Payment, KitchenOrder

admin.site.register(Category)
admin.site.register(Table)
admin.site.register(Ingredient)
admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(IngredientQuantity)
admin.site.register(Transaction)
admin.site.register(Payment)
admin.site.register(KitchenOrder)
