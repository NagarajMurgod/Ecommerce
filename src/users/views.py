from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import AddtoCartSerializer,CartSerializer
from product.models import Product
from rest_framework.response import Response
from rest_framework import status
from users.models import Cart,CartItem
from django.db.models import F
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from common.helpers import validation_error_handler

class AddtoCartView(APIView):
    serializer_class = AddtoCartSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)4
        if serializer.is_valid() is False:
            return Response({
                "status" : "error",
                "message":validation_error_handler(serializer.errors),
                "paylod" : serializer.errors,
            },status = status.HTTP_400_BAD_REQUEST)

        validated_data = serializer._validated_data

        product_uuid = validated_data['product_uuid']
        product = Product.objects.filter(uuid=product_uuid).first()

        if product is None:
            return Response({
                "status" : "error",
                "message" : "product not founds",
                "payload": {}
            },status=status.HTTP_400_BAD_REQUEST)
        
        cart,_ = Cart.objects.get_or_create(user=request.user)
        exisiting_cart_item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()
        
        if exisiting_cart_item is not None:
            exisiting_cart_item.quantity = F('quantity') + 1 
            exisiting_cart_item.save()
        
        else:
            cart_product = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=1
            )
        
        return Response(
            {
                "status" : "success",
                "message" : "successfuly added the product to cart"
            },
            status=status.HTTP_200_OK
        )

class DisplayCartView(RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        cart = Cart.objects.filter(user=self.request.user).prefetch_related("items__product").first()
        return cart