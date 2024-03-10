from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from common.permissions import IsSuperUser #custome permsission class
from rest_framework.parsers import MultiPartParser
import os
import uuid
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer,CreateProductSerializer
from .models import Product
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.views.decorators.cache import cache_page

class UploadProductImageView(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        img = request.data["image"]
        img_name = os.path.splitext(img.name)[0]
        img_extension = os.path.splitext(img.name)[-1]
        save_path = "media/posts/post_images/"
        # print(img, img_name, img_extension)

        
        if not os.path.exists(save_path):
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        image_name = img_name + str(uuid.uuid4())
        img_save_path = "%s/%s%s" % (save_path, image_name, img_extension)
        response_url = "posts/post_images/"+image_name+img_extension
        with open(img_save_path, "wb+") as f:
            for chunk in img.chunks():
                f.write(chunk)
            
        return Response({
            "path" : response_url
        },status=status.HTTP_200_OK)


class ListCreateProducView(ListCreateAPIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["name", "tags__title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    page_size = 2
    pagination_class = PageNumberPagination

    def list(self, request, *args,**kwargs):
        self.pagination_class.page_size = self.page_size
        return super().list(request,*args,**kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateProductSerializer
        
        return ProductSerializer
    
    def get_queryset(self):
        return Product.objects.filter().prefetch_related("tags")
    
    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data, context={
            "request":request
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        print(headers)
        return Response({
            "payload" : serializer.data,
            "message" : "successfuly created "
        },status=status.HTTP_201_CREATED,headers=headers)