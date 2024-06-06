from rest_framework.decorators import api_view
from rest_framework.response import Response
from computer_store.serializers import UserSerializer, ProductSerializer, ProductSearchSerializer
from rest_framework import status, generics
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.shortcuts import get_object_or_404

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

import requests
from django.http import JsonResponse

from computer_store.models import ProductModel

from computer_store.constants.general import GeneralConstants, ProductConstants, AdminConstants

from computer_store.helper import AdminHelper, DBHelper

from datetime import date

class AdminProducts(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    admin_helper = AdminHelper.AdminHelper()

    def get(self, request):
        user = self.admin_helper.get_admin_or_400(request.auth.key)
        if user.is_error:
            return user.error_message
        
        if 'product_id' in request.data:
            product = self.get_product(request.data['product_id'])
            serializer = self.serializer_class(instance=product)
        else:
            serializer = self.serializer_class(self.queryset.all(), many=True)

        return Response(serializer.data)
    
    def post(self, request):
        try:
            user = self.admin_helper.get_admin_or_400(request.auth.key)
            if user.is_error:
                return user.error_message

            request_data = {
                'name' : request.data['name'],
                'price' : request.data['price'],
                'image_url' : request.data['image_url'],
                'created_by' : 'admin',
                'created_date' : date.today(),
                'modified_date' : date.today(),
                'description' : request.data['description']
            }

            serializer = ProductSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()

                return Response(status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)
            return Response(
                { GeneralConstants.ERROR:GeneralConstants.ERROR_IN_UPLOAD_IMAGE },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def delete(self, request):
        user = self.admin_helper.get_admin_or_400(request.auth.key)
        if user.is_error:
            return user.error_message

        product = self.get_product(request.data['product_id'])
        if not product:
            return Response(
                { GeneralConstants.MESSAGE:ProductConstants.PRODUCT_NOT_FOUND },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_serializer = self.serializer_class(
            product, 
            data={'is_delete':True}, 
            partial=True)

        if product_serializer.is_valid():
            product_serializer.save()
            
            return Response(status=status.HTTP_200_OK)

        return Response(
            { GeneralConstants.MESSAGE:ProductConstants.CAN_NOT_DELETE },
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_product(self, pk):
        try:
            return ProductModel.objects.get(pk=pk)
        except ProductModel.DoesNotExist:
            return None  


class AdminProductsSearch(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    admin_helper = AdminHelper.AdminHelper()
    db_helper = DBHelper.DB_helper()

    def get(self, request):
        try:
            user = self.admin_helper.get_admin_or_400(request.auth.key)
            if user.is_error:
                return user.error_message
            
            products = self.convert_to_product_search_serializer(
                self.db_helper.store_procedure(
                    "product_get_product_by_search('" + request.GET.get('keywords') + "')"))

            serializer = ProductSearchSerializer(products, many=True)

            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:AdminConstants.ERROR_PRODUCT_SEARCH }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def convert_to_product_search_serializer(self, list_data):
        temp_dict = {}
        temp_tuple = []
        for item in list_data:
            temp_dict["id"] = item[0]
            temp_dict["name"] = item[1]
            temp_dict["image_url"] = item[2]
            temp_dict["price"] = item[3]
            temp_dict["created_by"] = item[4]
            temp_dict["created_date"] = item[5]
            temp_dict["modified_date"] = item[6]
            temp_dict["star_review"] = item[7]

            temp_tuple.append(temp_dict)
            temp_dict = {}

        return temp_tuple

class AdminProductsUpload(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    # parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    admin_helper = AdminHelper.AdminHelper()

    #http://localhost:8000/media/images/Screenshot_2023-11-23_073706.png
    
    def post(self, request):
        try:
            user = self.admin_helper.get_admin_or_400(request.auth.key)
            if user.is_error:
                return user.error_message

            serializer = ProductSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response(status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:GeneralConstants.ERROR_IN_UPLOAD_IMAGE },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        serializer = self.serializer_class(self.queryset.all(), many=True)

        return Response(serializer.data)


class AdminUsers(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    admin_helper = AdminHelper.AdminHelper()

    def get(self, request):
        user = self.admin_helper.get_admin_or_400(request.auth.key)
        if user.is_error:
            return user.error_message
        
        serializer = self.serializer_class(self.queryset.all(), many=True)

        return Response(serializer.data)