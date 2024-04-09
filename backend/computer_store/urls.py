from django.urls import path
from computer_store.views import LogIn, SignUp, LogOut, ProductImage, ProductDetail, Profile, Cart, ProductSearch

urlpatterns= [
    path('login', LogIn.as_view()),
    path('signup', SignUp.as_view()),
    path('logout', LogOut.as_view()),
    path('productimage', ProductImage.as_view()),
    path('productdetail', ProductDetail.as_view()),
    path('profile', Profile.as_view()),
    path('cart', Cart.as_view()),
    path('productsearch', ProductSearch.as_view()),
]