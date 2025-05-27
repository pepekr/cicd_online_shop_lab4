from django.shortcuts import render

from store.models import Product


def product_info(request, product_id):
    product = Product.objects.get(id=product_id)
    images = product.images.all()  # queryset of ProductImage
    context = {
        'product': product,
        'images': [img.image.url for img in images],  # list of image URLs for template
    }
    return render(request, "product.html", context)