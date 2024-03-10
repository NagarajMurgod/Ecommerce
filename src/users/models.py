from django.db import models
from common.models import TimestampModel
from django.contrib.auth import get_user_model
from product.models import Product

User = get_user_model()

class Cart(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')


class CartItem(TimestampModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product_id', 'cart_id'],
                name = 'unique-cart-product'
            )
        ]