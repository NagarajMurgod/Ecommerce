from django.urls import path,include
from product.views import UploadProductImageView,ListCreateProducView

urlpatterns = [
    path('products/image_upload/', UploadProductImageView.as_view(), name='product-img-upload'),
    path('products/',ListCreateProducView.as_view(), name="list-create-product" )
    
]
