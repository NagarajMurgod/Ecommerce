from django.db import models
from common.models import TimestampModel
import uuid
from django.contrib.auth import get_user_model

User=get_user_model()


class Tag(TimestampModel):
    title = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return f"#{self.title}"
    
    def clean(self):
        self.title = self.title.lower()
        super().clean()
    
    def save(self, *args,**kwargs):
        self.full_clean()
        return super().save(*args,**kwargs)
  

class Product(TimestampModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product/product_images', null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)
    tags = models.ManyToManyField(Tag, through='ProductTag', related_name="products")
    

class ProductTag(TimestampModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product_id', 'tag_id'], name='unique_product_tag'
            )
        ]