from django.urls import path
from computer_store.views.user.view import LogIn, SignUp, LogOut, \
    ProductDetail, Profile, Cart, ProductSearch, UserDemo, Payment, \
        Purchased, DemoUserData, CartProducts, Products
from computer_store.views.admin.view import AdminProductsUpload, \
    AdminProducts, AdminUsers, AdminProductsSearch

urlpatterns= [
    path('login', LogIn.as_view()),
    path('signup', SignUp.as_view()),
    path('logout', LogOut.as_view()),
    path('productdetail', ProductDetail.as_view()),
    path('profile', Profile.as_view()),
    path('cart', Cart.as_view()),
    path('products', Products.as_view()),
    path('cartproducts', CartProducts.as_view()),
    path('productsearch', ProductSearch.as_view()),
    path('userdemo', UserDemo.as_view()),
    path('payment', Payment.as_view()),
    path('purchased', Purchased.as_view()),
    path('demouserdata', DemoUserData.as_view()),

    path('adminproducts', AdminProducts.as_view()),
    path('adminproductssearch', AdminProductsSearch.as_view()),
    path('adminproductsupload', AdminProductsUpload.as_view()),
    
    path('adminusers', AdminUsers.as_view()),
]