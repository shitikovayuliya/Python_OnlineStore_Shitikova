from django.urls import path
from . import views

# URL-шаблоны для модуля store
# Группировка: каталог, категории, заказы, корзина

urlpatterns = [
    # Каталог товаров
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Категории
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),

    # Заказы (требуют авторизации)
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),

    # Корзина (требуют авторизации)
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
]




