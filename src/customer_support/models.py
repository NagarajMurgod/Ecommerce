from django.db import models
from authentication.models import User

class CustomerSupportManager(models.Manager):
    def get_queryset(self,*args,**kwargs):
        return  super().get_queryset(*args,**kwargs).filter(is_customer_support_user=True)

class CustomerSupportUser(User):
    class Meta:
        proxy = True

    @property
    def showAdditional(self):
        return self.customer_support_additional


class CustomerSupportUserAdditional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='customer_support_additional')
