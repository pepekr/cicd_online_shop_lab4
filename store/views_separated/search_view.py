from django.shortcuts import render
from store.models import Product


def search(request):
    from django.db.models import Q
    query = request.GET.get('name', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category = request.GET.get('category')

    q_object = Q()
    if query:
        sep_query = query.split()
        q_object |= Q(name__icontains=query)
        for word in sep_query:
            q_object |= Q(name__icontains=word)

    if min_price:
        q_object &= Q(price__gte=min_price)
    if max_price:
        q_object &= Q(price__lte=max_price)
    if category:
        q_object &= Q(category__iexact=category)

    products = Product.objects.filter(q_object).distinct()

    categories = Product.objects.values_list('category', flat=True).distinct()

    return render(request, "search.html", {
        "products": products,
        "categories": categories,
    })