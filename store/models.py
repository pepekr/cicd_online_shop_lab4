from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=10)

    # You can drop email/password fields unless you plan to use them separately
    # email = models.EmailField()
    # password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} ({self.user.email})"

    @staticmethod
    def get_customer_by_user(user):
        try:
            return Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return None


class Product(models.Model):
    name = models.CharField(max_length=60)
    price = models.IntegerField(default=0)
    category = models.CharField(null=True, max_length=60)
    description = models.CharField(
        max_length=1000, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/products/')

    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products():
        return Product.objects.all()

    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.get_all_products()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/products/')


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cod', 'Cash on Delivery'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now)
    estimated_shipping_date = models.DateField(null=True, blank=True)
    shipped_date = models.DateField(null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
    is_shipped = models.BooleanField(default=False)
    is_payment = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    is_approved = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    tracking_code = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically set is_payment based on payment_method
        if self.payment_method in ['credit_card', 'paypal']:
            self.is_payment = True
        else:
            self.is_payment = False
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order_time = models.IntegerField()

    def get_total_price(self):
        return self.quantity * self.price_at_order_time

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Order #{self.order.id}"


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Shipping for Order #{self.order.id}"
