from django.urls import path
from . import views
from .views_separated import search_view, shopping_cart_details, product_view, checkout_view, orders_view, place_order, \
    admin_manage_orders
from .views_separated.cancel_order import cancel_order
from .views_separated.product_view import product_info

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", search_view.search, name="search"),
    path("cart/details/", shopping_cart_details.cart_details, name="cart_details"),
    path("products/<int:product_id>/", product_view.product_info, name="product"),
    path("checkout/", checkout_view.checkout, name="checkout"),
    path("checkout/place_order/", place_order.place_order, name="place_order"),
    path("orders/", orders_view.user_orders_view, name="orders"),
    path("cancel-order/", cancel_order, name='cancel_order'),
    path("admin_manage_orders/", admin_manage_orders.manage_orders, name='manage_orders'),
]
