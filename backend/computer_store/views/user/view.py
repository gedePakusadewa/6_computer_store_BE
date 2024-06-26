from rest_framework.decorators import api_view
from rest_framework.response import Response
from computer_store.serializers import UserSerializer, ProductSerializer, CartSerializer, CartDetailSerializer, ProductSearchSerializer, PurchasingSerializer, PurchasingDetailSerializer, PurchasedSerializer
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

from computer_store.models import ProductModel, CartModel, PurchasingModel, PurchasingDetailModel

from django.db import connection

from computer_store.constants.general import UserDemoConstants, UserConstants, GeneralConstants, ProfileConstants, LogInConstants, ProductConstants, CartConstants, PaymentConstants, DemoUserConstants, AdminConstants

import datetime

from computer_store.helper import UserHelper, AdminHelper, DBHelper

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
        
class Products(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
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

            db_helper = DBHelper.DB_helper()
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
            db_helper = DBHelper.DB_helper()
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
    user_helper = UserHelper.UserHelper()

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
            user = self.user_helper.get_user_by_token_or_404(request.auth.key)
            if user.is_error:
                return user.error_message
            
            if user:
                db_helper = DBHelper.DB_helper()
                carts = self.convert_tuple_to_dict(db_helper.store_procedure("cart_get_all_by_user_id("+str(user.id)+")"))
                total_order_price = self.get_total_order_and_price(carts)

                serializer = CartDetailSerializer(instance=carts, many=True)
                
                return Response({
                    CartConstants.CART_PRODUCT:serializer.data,   
                    CartConstants.TOTAL_ORDER_PRICE:total_order_price
                }) 
            
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:CartConstants.ERROR_IN_CART }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            user = self.user_helper.get_user_by_token_or_404(request.auth.key)
            if user.is_error:
                return user.error_message

            cart = self.get_cart_or_400(request.data['cart_id'])
            if cart.is_error:
                return cart
            
            cart.delete()

            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:CartConstants.ERROR_IN_CART }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_cart_or_400(self, id):
        cart = CartModel
        cart.is_error = False
        
        try:
            cart = CartModel.objects.get(pk=id)         
        except User.DoesNotExist:
            cart.is_error = True
            cart.error_message = Response(
                { GeneralConstants.MESSAGE:CartConstants.PRODUCT_CART_NOT_FOUND },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return cart

    def convert_tuple_to_dict(self, tuple_data):
        temp_dict = {}
        temp_tuple = []
        for item in tuple_data:
            temp_dict["id_product"] = item[0]
            temp_dict["name"] = item[1]
            temp_dict["image_url"] = item[2]
            temp_dict["price"] = item[3]
            temp_dict["total_order"] = item[4]
            temp_dict["id_cart"] = item[5]

            temp_tuple.append(temp_dict)
            temp_dict = {}

        return temp_tuple
    
    def get_total_order_and_price(self, cart_data):
        total_order = 0
        total_price = 0

        for item in cart_data:
            total_order += int(item["total_order"])

        total_price = total_order * int(item["price"])

        return {"total_order":total_order,  "total_price":total_price}

class Payment(generics.GenericAPIView):
    queryset = PurchasingModel.objects.all()
    serializer_class = PurchasingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    db_helper = DBHelper.DB_helper()

    def post(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)

            if not user:
                return Response(
                    { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            carts = self.convert_tuple_to_dict(self.db_helper.store_procedure("cart_get_all_by_user_id("+str(user_id)+")"))

            if len(carts) == 0:
                return Response(
                        { GeneralConstants.MESSAGE:CartConstants.PRODUCT_CART_NOT_FOUND },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            purchasing_detail = self.carts_to_purchasing_detail(carts)            
            purchasing_detail_serializer = PurchasingDetailSerializer(data=purchasing_detail, many=True)
            if  purchasing_detail_serializer.is_valid():
                purchasing_detail_serializer.save()

                purchasing = self.purchasing_detail_to_purchasing(purchasing_detail_serializer.data, user)
                purchasing_serializer = PurchasingSerializer(data=purchasing, many=True)
                if  purchasing_serializer.is_valid():
                    purchasing_serializer.save()
                    
                    self.db_helper.store_procedure("cart_delete_by_user_id("+str(user_id)+")")

                    return Response(status=status.HTTP_200_OK)

                else:
                    return Response(
                            { GeneralConstants.MESSAGE:purchasing_serializer.errors },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
            else:
                return Response(
                        { GeneralConstants.MESSAGE:purchasing_detail_serializer.errors },
                        status=status.HTTP_400_BAD_REQUEST
                    )

        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:PaymentConstants.ERROR_IN_PAYMENT }, 
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

    def carts_to_purchasing_detail(self, carts):
        temp_dict = {}
        temp_tuple = []
        current_datetime = datetime.date.today().strftime ("%Y-%m-%d")
        for item in carts:
            temp_dict["product"] = item["id"]
            temp_dict["quantity"] = item["total_order"]
            temp_dict["price"] = item["price"]
            temp_dict["total_price"] = int(item["total_order"]) * int(item["price"])
            temp_dict["created_date"] = current_datetime
            temp_dict["modified_date"] = current_datetime

            temp_tuple.append(temp_dict)
            temp_dict = {}

        return temp_tuple
    
    def purchasing_detail_to_purchasing(self, purchasing_detail, user):
        temp_dict = {}
        temp_tuple = []
        current_datetime = datetime.date.today().strftime ("%Y-%m-%d")
        for item in purchasing_detail:
            temp_dict["user"] = user.id
            temp_dict["purchasing_detail"] = item["id"]
            temp_dict["created_date"] = current_datetime
            temp_dict["modified_date"] = current_datetime

            temp_tuple.append(temp_dict)
            temp_dict = {}

        return temp_tuple
    
class Purchased(generics.GenericAPIView):
    queryset = PurchasingModel.objects.all()
    serializer_class = PurchasingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    db_helper = DBHelper.DB_helper()

    def get(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)            
            if not user:
                return Response(
                    { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                    status=status.HTTP_404_NOT_FOUND
                )

            purchased_data = self.db_helper.store_procedure("purchasing_get_all_by_user_id("+str(user_id)+")")
            if len(purchased_data) == 0:
                return Response(
                    { GeneralConstants.DATA:[] },
                    status=status.HTTP_200_OK
                )

            purchased_serializer_ready = self.purchased_data_to_serializer_format(purchased_data)

            purchaser_serializered = PurchasedSerializer(purchased_serializer_ready, many=True)

            return Response(
                { GeneralConstants.DATA:purchaser_serializered.data },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:GeneralConstants.ERROR_IN_PURCHASED }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def purchased_data_to_serializer_format(self, data):
        temp_dict = {}
        temp_list = []

        for x in data:
            temp_dict["name"] = x[2]
            temp_dict["image_url"] = x[1]
            temp_dict["price"] = x[3]
            temp_dict["created_date"] = x[0]
            temp_dict["total_price"] = x[5] 
            temp_dict["total_unit"] = x[4]

            temp_list.append(temp_dict)
            temp_dict = {}

        return temp_list

class DemoUserData(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    demo_username = getattr(settings, UserDemoConstants.USERNAME_DEMO, None)
    db_helper = DBHelper.DB_helper()

    def delete(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)            
            if not user:
                return Response(
                    { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if user.username != self.demo_username:
                return Response(
                    { GeneralConstants.MESSAGE:DemoUserConstants.NOT_DEMO_USER },
                    status=status.HTTP_400_BAD_REQUEST
                )
   
            self.db_helper.store_procedure("demo_user_delete_all_data('" + user.username + "')")

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:DemoUserConstants.ERROR_IN_DEMOUSER }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        pass

class CartProducts(generics.GenericAPIView):
    queryset = CartModel.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    demo_username = getattr(settings, UserDemoConstants.USERNAME_DEMO, None)
    db_helper = DBHelper.DB_helper()
    user_helper = UserHelper.UserHelper()

    # limit for total order by user
    lower_limit = 0
    upper_limit = 100

    def post(self, request):
        try:
            user = self.user_helper.get_user_by_token_or_404(request.auth.key)
            if user.is_error:
                return user.error_message
               
            cart_product = self.get_cart_product(request.data["cart_product_id"])            
            if not cart_product:
                return Response(
                    { GeneralConstants.MESSAGE:CartConstants.CART_PRODUCT_NOT_FOUND },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            total_order = request.data["total_order"]
            if not total_order.isdigit():
                return Response(
                    { GeneralConstants.MESSAGE:CartConstants.CART_PRODUCT_TOTAL_UNIT_ERROR },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if int(total_order) < self.lower_limit or int(total_order) > self.upper_limit:
                return Response(
                    { GeneralConstants.MESSAGE:CartConstants.CART_PRODUCT_TOTAL_UNIT_ERROR },
                    status=status.HTTP_400_BAD_REQUEST
                )

            self.db_helper.store_procedure("cart_product_update_by_id('" + cart_product.id.hex + "', '" + str(total_order) + "')")

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                { GeneralConstants.ERROR:CartConstants.ERROR_IN_CART }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_cart_product(self, id):
        try:
            return CartModel.objects.get(pk=id)
        except CartModel.DoesNotExist:
            return None

# class AdminProducts(generics.GenericAPIView):
#     queryset = ProductModel.objects.all()
#     serializer_class = ProductSerializer
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     admin_helper = AdminHelper.AdminHelper()

#     def get(self, request):
#         user = self.admin_helper.get_admin_or_400(request.auth.key)
#         if user.is_error:
#             return user.error_message
        
#         serializer = self.serializer_class(self.queryset.all(), many=True)

#         return Response(serializer.data)
    
#     # def post(self, request):
#     #     try:
#     #         user = self.admin_helper.get_admin_or_400(request.auth.key)
#     #         if user.is_error:
#     #             return user.error_message

#     #         serializer = ProductSerializer(data=request.data)

#     #         if serializer.is_valid():
#     #             serializer.save()

#     #             return Response(status=status.HTTP_200_OK)
            
#     #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#     #     except Exception as e:
#     #         return Response(
#     #             { GeneralConstants.ERROR:GeneralConstants.ERROR_IN_UPLOAD_IMAGE },
#     #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#     #         )
        
#     def delete(self, request):
#         user = self.admin_helper.get_admin_or_400(request.auth.key)
#         if user.is_error:
#             return user.error_message
        
#         product = self.get_product
#         if not product:
#             return Response(
#                 { GeneralConstants.MESSAGE:ProductConstants.PRODUCT_NOT_FOUND },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         product.is_delete = True

#         product_serializer = self.serializer_class(instance=product)

#         if product_serializer.is_valid():
#             product_serializer.save()
            
#             return Response(status=status.HTTP_200_OK)

#         return Response(
#             { GeneralConstants.MESSAGE:ProductConstants.CAN_NOT_DELETE },
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     def get_product(self, pk):
#         try:
#             return ProductModel.objects.get(pk=pk)
#         except ProductModel.DoesNotExist:
#             return None    


# class AdminProductsSearch(generics.GenericAPIView):
#     queryset = ProductModel.objects.all()
#     serializer_class = ProductSerializer
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     admin_helper = AdminHelper.AdminHelper()
#     db_helper = DB_helper()

#     def get(self, request):
#         try:
#             user = self.admin_helper.get_admin_or_400(request.auth.key)
#             if user.is_error:
#                 return user.error_message
            
#             products = self.convert_to_product_search_serializer(
#                 self.db_helper.store_procedure(
#                     "product_get_product_by_search('" + request.GET.get('keywords') + "')"))

#             serializer = ProductSearchSerializer(products, many=True)

#             return Response(serializer.data)
        
#         except Exception as e:
#             return Response(
#                 { GeneralConstants.ERROR:AdminConstants.ERROR_PRODUCT_SEARCH }, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def convert_to_product_search_serializer(self, list_data):
#         temp_dict = {}
#         temp_tuple = []
#         for item in list_data:
#             temp_dict["id"] = item[0]
#             temp_dict["name"] = item[1]
#             temp_dict["image_url"] = item[2]
#             temp_dict["price"] = item[3]
#             temp_dict["created_by"] = item[4]
#             temp_dict["created_date"] = item[5]
#             temp_dict["modified_date"] = item[6]
#             temp_dict["star_review"] = item[7]

#             temp_tuple.append(temp_dict)
#             temp_dict = {}

#         return temp_tuple

# class AdminProductsUpload(generics.GenericAPIView):
#     queryset = ProductModel.objects.all()
#     serializer_class = ProductSerializer
#     # parser_classes = (MultiPartParser, FormParser)
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     admin_helper = AdminHelper.AdminHelper()

#     #http://localhost:8000/media/images/Screenshot_2023-11-23_073706.png
    
#     def post(self, request):
#         try:
#             user = self.admin_helper.get_admin_or_400(request.auth.key)
#             if user.is_error:
#                 return user.error_message

#             serializer = ProductSerializer(data=request.data)

#             if serializer.is_valid():
#                 serializer.save()

#                 return Response(status=status.HTTP_200_OK)
            
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         except Exception as e:
#             return Response(
#                 { GeneralConstants.ERROR:GeneralConstants.ERROR_IN_UPLOAD_IMAGE },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     def get(self, request):
#         serializer = self.serializer_class(self.queryset.all(), many=True)

#         return Response(serializer.data)


# class AdminUsers(generics.GenericAPIView):
    # queryset = User.objects.all()
    # serializer_class = UserSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    # admin_helper = AdminHelper.AdminHelper()

    # def get(self, request):
    #     user = self.admin_helper.get_admin_or_400(request.auth.key)
    #     if user.is_error:
    #         return user.error_message
        
    #     serializer = self.serializer_class(self.queryset.all(), many=True)

    #     return Response(serializer.data)