from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('ingredient/<int:pk>/', views.ingredient, name='ingredient'),
    path('menu/', views.menu, name='menu'),
    path('add_ingredient/', views.add_ingredient, name='add_ingredient'),
    path('prepareFood/', views.prepare_food, name='prepare_food'),
    path('transaction_detail/', views.transaction_detail, name='transaction_detail'),
    path('manage_menu/', views.manage_menu, name='manage_menu'),
    path('view_orders/', views.view_orders, name='view_orders'),
    path('add_menu_item/', views.add_menu_item, name='add_menu_item'),
    path('create_order/', views.create_order, name='create_order'),

    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

    path('update_order/', views.update_order, name='add_menu_item'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('order_list/', views.order_list, name='order_list'),
    
    path('order/<int:order_id>/payment/', views.payment_view, name='payment'),
    path('kitchen_order/<int:kitchen_order_id>/', views.kitchen_order_detail, name='kitchen_order_detail'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_detail/<int:payment_id>/', views.payment_details, name='payment_detail'),
    path('order_report/', views.order_report, name='order_report'),
    path('order_report/<int:table_id>/', views.order_report, name='order_report_by_table'),


]