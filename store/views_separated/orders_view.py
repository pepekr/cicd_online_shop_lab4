from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from store.models import Order, Customer


@login_required
def user_orders_view(request):
    customer = Customer.get_customer_by_user(request.user)
    if not customer:
        return render(request, 'user_orders.html', {'orders': []})

    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    return render(request, 'user_orders.html', {'orders': orders})
