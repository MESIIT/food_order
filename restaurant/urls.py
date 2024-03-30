from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('ingredient/<int:pk>/', views.ingredient, name='ingredient'),
    path('menu/', views.menu, name='menu'),
    path('add_ingredient/', views.add_ingredient, name='add_ingredient'),
    path('prepareFood/', views.prepare_food, name='prepare_food'),
    path('addtocart/', views.add_to_cart, name='add_to_cart'),
    path('viewcart/', views.view_cart, name='view_cart'),
    path('transaction_detail/', views.transaction_detail, name='transaction_detail'),
    path('manage_menu/', views.manage_menu, name='manage_menu'),
    path('view_orders/', views.view_orders, name='view_orders'),
    path('add_menu_item/', views.add_menu_item, name='add_menu_item'),
    path('create_order/', views.create_order, name='create_order'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('update_order/', views.update_order, name='add_menu_item'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('order_list/', views.order_list, name='order_list'),
    path('create_bill/<int:order_id>/', views.create_bill, name='create_bill'),
    path('viewbill/', views.view_bills, name='view_bills'),
    path('order/<int:order_id>/payment/', views.payment_view, name='payment'),
    path('payment_success/', views.payment_success, name='payment_success'),

]