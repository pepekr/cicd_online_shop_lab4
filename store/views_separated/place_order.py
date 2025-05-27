import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Customer, Product, Order, OrderItem, ShippingAddress


@require_POST
def place_order(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    full_name = data.get('full_name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    city = data.get('city')
    postal_code = data.get('postal_code')
    payment_method = data.get('payment_method')

    if not all([full_name, email, address, city, postal_code, payment_method]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    is_authenticated = request.user.is_authenticated

    if is_authenticated:
        # Logged-in user
        user = request.user
        if user.email.lower() != email.lower():
            return JsonResponse({'error': 'You cannot use a different email while logged in.'}, status=400)

        customer, _ = Customer.objects.get_or_create(user=user)

        if phone and customer.phone != phone:
            customer.phone = phone
            customer.save()

        is_approved = False
    else:
        # Guest user
        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({'error': 'This email is already in use. Please log in.'}, status=400)

        first_name = full_name.split(' ')[0]
        last_name = ' '.join(full_name.split(' ')[1:]) if len(full_name.split(' ')) > 1 else ''

        user = User.objects.create_user(
            username=email,
            email=email,
            password=User.objects.make_random_password(),
            first_name=first_name,
            last_name=last_name,
        )
        customer = Customer.objects.create(user=user, phone=phone or '')
        is_approved = False  # Guests always need approval

    # Create the order
    order = Order.objects.create(
        customer=customer,
        payment_method=payment_method,
        is_approved=is_approved,
        is_payment=True,

    )

    ShippingAddress.objects.create(
        order=order,
        full_name=full_name,
        phone=phone or '',
        address=address,
        city=city,
        postal_code=postal_code,
    )

    cart_items = request.session.get('cart_items', [])
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return JsonResponse({'error': 'Your cart is empty.'}, status=400)

    product_ids = [item['id'] for item in cart_items]
    products = Product.objects.filter(id__in=product_ids)
    product_map = {p.id: p for p in products}

    for item in cart_items:
        product = product_map.get(item['id'])
        if product and item['quantity'] > 0:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price_at_order_time=product.price
            )

    # Clear cart
    request.session['cart_items'] = []
    request.session['total'] = 0

    messages.success(request, "Order placed successfully!")
    return JsonResponse({'message': 'Order placed successfully!'}, status=200)