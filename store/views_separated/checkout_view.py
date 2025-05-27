import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from store.models import Customer, Product, Order, OrderItem, ShippingAddress


def checkout(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        cart = json_data.get('cart', [])  # expecting list of {id, quantity}

        product_ids = [item['id'] for item in cart]
        products = Product.objects.filter(id__in=product_ids)

        product_map = {p.id: p for p in products}

        cart_items = []
        for item in cart:
            product = product_map.get(item['id'])
            if product:
                cart_items.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': item['quantity'],
                    'subtotal': product.price * item['quantity'],
                })
        print("Checking out cart items in checkout", cart_items)
        request.session['cart_items'] = cart_items
        request.session['total'] = sum(item['subtotal'] for item in cart_items)

        return redirect('/checkout/')  # reload page with cart info

    else:
        cart_items = request.session.get('cart_items', [])
        total = request.session.get('total', 0)

        initial_data = {}

        if request.user.is_authenticated:
            # Basic user info
            initial_data['full_name'] = request.user.get_full_name()
            initial_data['email'] = request.user.email

            # Try to get Customer and Shipping info
            customer = Customer.get_customer_by_user(request.user)
            if customer:
                initial_data['phone'] = customer.phone

                # Look for last order and its shipping info
                order = Order.objects.filter(customer=customer).order_by('-order_date').first()
                shipping = order.shipping_address if order and hasattr(order, 'shipping_address') else None

                if shipping:
                    initial_data.update({
                        'address': shipping.address,
                        'city': shipping.city,
                        'postal_code': shipping.postal_code,
                    })

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total': total,
            'initial_data': initial_data,
        })
