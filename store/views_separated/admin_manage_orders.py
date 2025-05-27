import random
from datetime import timedelta, date
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from store.models import Order


@staff_member_required
def manage_orders(request):
    orders = Order.objects.all().select_related('customer__user')

    # Search filters
    order_id = request.GET.get('order_id')
    user_id = request.GET.get('user_id')
    status_filter = request.GET.get('status')  # recent, canceled, waiting_approval, etc.

    if order_id:
        orders = orders.filter(id=order_id)
    if user_id:
        orders = orders.filter(customer__user__id=user_id)

    # Status filters
    if status_filter == 'canceled':
        orders = orders.filter(is_canceled=True)
    elif status_filter == 'waiting_approval':
        orders = orders.filter(is_approved=False, is_canceled=False)
    elif status_filter == 'recent':
        from django.utils.timezone import now
        week_ago = now() - timedelta(days=7)
        orders = orders.filter(order_date__gte=week_ago)
    elif status_filter == 'not_canceled':
        orders = orders.filter(is_canceled=False)

    # Approve or Cancel order via AJAX POST
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        action = request.POST.get('action')
        oid = request.POST.get('order_id')
        order = get_object_or_404(Order, id=oid)

        if action == 'approve':
            if order.is_canceled:
                return JsonResponse({'success': False, 'error': 'Order already canceled'})
            if order.is_approved:
                return JsonResponse({'success': False, 'error': 'Order already approved'})

            order.is_approved = True
            order.save()
            return JsonResponse({'success': True})

        elif action == 'cancel':
            if order.is_canceled:
                return JsonResponse({'success': False, 'error': 'Order already canceled'})
            order.is_canceled = True
            order.is_approved = False  # Can't approve canceled
            order.save()
            return JsonResponse({'success': True})

        elif action == 'add_tracking':
            tracking_code = request.POST.get('tracking_code', '').strip()
            if not tracking_code:
                return JsonResponse({'success': False, 'error': 'Tracking code cannot be empty'})

            if order.is_canceled:
                return JsonResponse({'success': False, 'error': 'Cannot add tracking to canceled order'})

            order.tracking_code = tracking_code
            today = date.today()
            order.shipped_date = today
            order.estimated_shipping_date = today + timedelta(days=random.choice([2, 3]))
            order.is_shipped = True
            order.save()
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid action'})

    context = {
        'orders': orders.order_by('-order_date')[:50],  # limit to 50 to avoid overload
        'order_id': order_id or '',
        'user_id': user_id or '',
        'status_filter': status_filter or '',
    }
    return render(request, 'admin_manage_orders.html', context)
