from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from store.models import Order, Customer


@require_POST
@login_required
def cancel_order(request):
    order_id = request.POST.get('order_id')
    if not order_id:
        return JsonResponse({'error': 'Order ID missing.'}, status=400)

    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found.'}, status=404)

    try:
        order = Order.objects.get(id=order_id, customer=customer)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found or unauthorized.'}, status=404)

    if order.is_canceled:
        return JsonResponse({'error': 'Order already canceled.'}, status=400)

    if order.is_shipped:
        return JsonResponse({'error': 'Cannot cancel shipped orders.'}, status=400)

    order.is_canceled = True
    order.save()

    return JsonResponse({'success': True, 'message': 'Order canceled.'})
