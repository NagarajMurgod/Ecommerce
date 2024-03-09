from django.db import models
from common.models import TimestampModel
from django.contrib.auth import get_user_model
import uuid
from orders.choices import OrderStatusChoice
from product.models import Product

User = get_user_model()


class Order(TimestampModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status =models.CharField(choices=OrderStatusChoice.CHOICE_LIST, max_length=16)


class OrderItem(TimestampModel):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='orders')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    price = models.DecimalField(max_digits=10,decimal_places=2)