import random
from django.shortcuts import render
from store.models import Product


def home(request):
    selected_category = request.GET.get("category")
    categories = Product.objects.values_list("category", flat=True).distinct()

    # Filtered products if a category is selected
    category_products = None
    if selected_category:
        category_products = Product.objects.filter(category=selected_category)

    # Grab 20 random products
    all_products = list(Product.objects.all())
    random_products = random.sample(all_products, min(20, len(all_products)))

    return render(request, "home.html", {
        "user_name": request.user.username,
        "categories": categories,
        "selected_category": selected_category,
        "category_products": category_products,
        "random_products": random_products,
    })
