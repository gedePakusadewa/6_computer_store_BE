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

from .models import ProductModel, CartModel

from django.db import connection

from computer_store.constants.general import UserDemoConstants, UserConstants, GeneralConstants, ProfileConstants, LogInConstants, ProductConstants, CartConstants

class LogIn(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    demo_username =  getattr(settings, UserDemoConstants.USERNAME_DEMO, None)
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
                return Response(
                    { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                    status=status.HTTP_404_NOT_FOUND
                )

            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(instance=user)

            return Response({
                GeneralConstants.TOKEN:token.key, 
                UserConstants.USER:serializer.data
            })
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:LogInConstants.ERROR_IN_LOGIN },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SignUp(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(username=request.data['username'])
                user.set_password(request.data['password'])
                user.save()
                token = Token.objects.create(user=user)

                return Response({
                    GeneralConstants.TOKEN:token.key, 
                    UserConstants.USER:serializer.data
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:GeneralConstants.ERROR_IN_SIGNUP },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 

# TODO if user account got deleted through post man and then user log out using
# frontend, server will send unautorised account
# find a way to handle this
class LogOut(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            request.user.auth_token.delete()

            return Response(
                { GeneralConstants.SUCCESS:GeneralConstants.SUCCESS_LOG_OUT },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:GeneralConstants.ERROR_IN_LOG_OUT },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProductImage(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    # parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #http://localhost:8000/media/images/Screenshot_2023-11-23_073706.png
    
    def post(self, request):
        try:
            serializer = ProductSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response({ GeneralConstants.IMAGE_URL:serializer.data })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:GeneralConstants.ERROR_IN_UPLOAD_IMAGE },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
        try:
            keywords = request.GET.get("keywords")

            db_helper = DB_helper()
            products = self.convert_tuple_to_dict(db_helper.store_procedure("product_get_product_by_search('" + keywords + "')"))
        
            serializer = ProductSearchSerializer(products, many=True)

            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:ProductConstants.ERROR_IN_PRODUCT_SEARCH },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        
    
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

        return Response({ ProductConstants.PRODUCT_DETAIL:serializer.data }) 

class Profile(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    username_demo = getattr(settings, UserDemoConstants.USERNAME_DEMO, None)

    def get(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)

        if not user:
            return Response(
                { GeneralConstants.MESSAGE: UserConstants.NOT_FOUND },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.serializer_class(instance=user)

        return Response({ GeneralConstants.USER:serializer.data })
            
    def post(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)

            if not user:
                return Response(
                    { GeneralConstants.MESSAGE: UserConstants.NOT_FOUND },
                    status=status.HTTP_404_NOT_FOUND
                )

            if user.username.upper() == self.username_demo.upper():
                return Response(
                    { GeneralConstants.ERROR:UserDemoConstants.CAN_NOT_MODIFY },
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
                { GeneralConstants.ERROR:ProfileConstants.ERROR_IN_UPDATE_PROFILE },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        
    
    def delete(self, request):        
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)

            if not user:
                return Response(
                    { GeneralConstants.MESSAGE: UserConstants.NOT_FOUND },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if user.username.upper() == self.username_demo.upper():
                return Response(
                    { GeneralConstants.MESSAGE:UserDemoConstants.CAN_NOT_MODIFY },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # TODO find a way to delete user using SP instead using ORM
            # track sql query using
            # print(connection.queries)       
            user.delete()
            db_helper = DB_helper()
            carts = db_helper.store_procedure("profile_delete_user_by_user_id("+str(user_id)+")")

            return Response(
                { GeneralConstants.MESSAGE:UserConstants.USER_DELETED },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:UserConstants.ERROR_WHEN_DELETE_USER },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserDemo(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    demo_username = getattr(settings, UserDemoConstants.USERNAME_DEMO, None)

    def get(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)

        if not user:
            return Response(
                { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_user_demo = False
        
        if user.username == self.demo_username:
            is_user_demo = True

        return Response(
            { GeneralConstants.DATA:is_user_demo}, 
            status=status.HTTP_200_OK
        )
        
# TODO
# find way so it can pass data through body data for delete request not in url param
class Cart(generics.GenericAPIView):
    queryset = CartModel.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
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
                            { GeneralConstants.MESSAGE:serializer.errors },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                return Response(
                        { GeneralConstants.MESSAGE:ProductConstants.PRODUCT_NOT_FOUND },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                    { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:CartConstants.ERROR_IN_CART }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)
            
            if user:
                db_helper = DB_helper()
                carts = self.convert_tuple_to_dict(db_helper.store_procedure("cart_get_all_by_user_id("+str(user_id)+")"))
                
                serializer = CartDetailSerializer(instance=carts, many=True)
                
                return Response({ CartConstants.CART_PRODUCT:serializer.data }) 

            return Response(
                    { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:CartConstants.ERROR_IN_CART }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)
            
            if not user:
                return Response(
                        { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                        status=status.HTTP_404_NOT_FOUND
                    )

            cart = CartModel.objects.get(product_id=request.data['product_id'])

            if not cart:
                return Response(
                    { GeneralConstants.MESSAGE:CartConstants.PRODUCT_CART_NOT_FOUND },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart.delete()

            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:CartConstants.ERROR_IN_CART }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
    



