from django.http import JsonResponse
from django.views.decorators.http import require_POST

from store.models import Product


@require_POST
def cart_details(request):
    import json
    ids = json.loads(request.body.decode("utf-8")).get("ids", [])
    products = Product.objects.filter(id__in=ids).values("id", "name", "price")
    return JsonResponse(list(products), safe=False)