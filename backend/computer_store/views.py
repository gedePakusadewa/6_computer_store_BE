from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer, ProductSerializer, CartSerializer, CartDetailSerializer, ProductSearchSerializer
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

# from rest_framework.parsers import MultiPartParser, FormParser
from .models import ProductModel, CartModel

from django.db import connection

from computer_store.constants.general import UserDemoConstants, UserConstants

class LogIn(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    demo_username =  getattr(settings, "USERNAME_DEMO", None)
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            is_demo = request.data['isDemo']

            if is_demo:
                user = get_object_or_404(User, username=self.demo_username)
            else:
                user = get_object_or_404(User, username=request.data['username'])

            if not is_demo and not user.check_password(request.data['password']):
                return Response({"detail":"Not Found"}, status=status.HTTP_404_NOT_FOUND)

            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(instance=user)

            return Response({"token":token.key, "user":serializer.data})
        
        except Exception:
            return Response(
                {"message":"Error in Log In"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SignUp(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data['username'])
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)

            return Response({"token":token.key, "user":serializer.data})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogOut(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass

        return Response(
            {"Success":"Success Log Out"},
            status=status.HTTP_200_OK
        )

class ProductImage(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    # parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #http://localhost:8000/media/images/Screenshot_2023-11-23_073706.png
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({"image_url":serializer.data})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        serializer = self.serializer_class(self.queryset.all(), many=True)

        return Response(serializer.data)
    
class ProductSearch(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    # TODO
    # - add validation for string from user keywords
    def get(self, request):
        keywords = request.GET.get("keywords")

        db_helper = DB_helper()
        products = self.convert_tuple_to_dict(db_helper.store_procedure("product_get_product_by_search('" + keywords + "')"))
    
        serializer = ProductSearchSerializer(products, many=True)

        return Response(serializer.data)
    
    def convert_tuple_to_dict(self, list_data):
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

class ProductDetail(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    # parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        product = get_object_or_404(ProductModel, pk=request.GET.get('pk'))
        serializer = self.serializer_class(instance=product)

        return Response({"product_detail":serializer.data}) 

class Profile(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    username_demo = getattr(settings, "USERNAME_DEMO", None)

    def get(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)

            if not user:
                return Response(
                    {"message": UserConstants.NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.serializer_class(instance=user)

            return Response({"user":serializer.data})
        
        except Exception as e:
            return Response(
                { "Error": "Error In Profile" },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def post(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)

            if not user:
                return Response(
                    {"message": UserConstants.NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND
                )

            if user.username.upper() == self.username_demo.upper():
                return Response(
                    { "Error":UserDemoConstants.CAN_NOT_MODIFY },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user is not None:
                serializer_user = self.serializer_class(user, data=request.data, partial=True)

                if serializer_user.is_valid():
                    serializer_user.save()

                    return Response(status=status.HTTP_200_OK)
                
            return Response(
                serializer_user.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                { "Error":"Error In Update Profile" },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        
    
    def delete(self, request):        
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)

            if not user:
                return Response(
                    {"message": UserConstants.NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if user.username.upper() == self.username_demo.upper():
                return Response(
                    { "Error":UserDemoConstants.CAN_NOT_MODIFY },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.delete()           

            return Response(
                {"message":"User deleted"},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {"message":"Error when delete user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserDemo(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    demo_username = getattr(settings, "USERNAME_DEMO", None)

    def get(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)

            if not user:
                return Response(
                    {"message": UserConstants.NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            is_user_demo = False
            
            if user.username == self.demo_username:
                is_user_demo = True

            return Response(
                {"data" : is_user_demo}, 
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"Message":"Error In Log In"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# TODO
# find way so it can pass data through body data for delete request not in url param
class Cart(generics.GenericAPIView):
    queryset = CartModel.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)

        if user:
            product = ProductModel.objects.get(pk=request.data['product_pk'])
            
            if product:

                product_data = {
                    "user" : user_id,
                    "product" : request.data['product_pk'],
                    "created_date" : "2024-03-18",
                    "total_order" : request.data['total_order']
                }

                serializer = self.serializer_class(data=product_data)

                if  serializer.is_valid():
                    serializer.save()

                    return Response(status=status.HTTP_200_OK)
                
                return Response(
                        {
                            "message":"Can not save product"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            return Response(
                    {
                        "message":"Product not found"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
                {
                    "message":"User not found"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)
        
        if user:
            db_helper = DB_helper()
            carts = self.convert_tuple_to_dict(db_helper.store_procedure("cart_get_all_by_user_id("+str(user_id)+")"))
            
            serializer = CartDetailSerializer(instance=carts, many=True)
            
            return Response({"cart_products":serializer.data}) 

        return Response(
                {"message":"User not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)
        
        if not user:
            return Response(
                {"message":"User not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = CartModel.objects.get(product_id=request.data['product_id'])

        if not cart:
            return Response(
                {"message":"Product cart not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart.delete()

        return Response(status=status.HTTP_200_OK)
    
    def convert_tuple_to_dict(self, tuple_data):
        temp_dict = {}
        temp_tuple = []
        for item in tuple_data:
            temp_dict["id"] = item[0]
            temp_dict["name"] = item[1]
            temp_dict["image_url"] = item[2]
            temp_dict["price"] = item[3]
            temp_dict["total_order"] = item[4]

            temp_tuple.append(temp_dict)
            temp_dict = {}

        return temp_tuple

#TODO:
    #find a new structure to place db helper
    #search what is connection, connection.cursor, cursor.execute, cursor.fetahcall()
    #is there alternative to this?
class DB_helper():
    def function_get_all(self, function_name):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM "+ function_name +";")
            row = cursor.fetchall()

        return row
    
    def store_procedure(self, sp_name):
        with connection.cursor() as cursor:
            cursor.execute("CALL "+ sp_name +";")
            row = cursor.fetchall()

        return row
    



