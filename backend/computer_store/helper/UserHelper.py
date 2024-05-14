from django.contrib.auth.models import User
from rest_framework.response import Response
from computer_store.constants.general import UserConstants, GeneralConstants
from rest_framework import status
from rest_framework.authtoken.models import Token

class UserHelper():
    # def get_user(self, user_id):
    #     try:
    #         return User.objects.get(pk=user_id)
    #     except User.DoesNotExist:
    #         return None
        
    # def get_user_with_404(self, user_id):
    #     user = User

    #     try:
    #         user = User.objects.get(pk=user_id)
    #     except User.DoesNotExist:
    #         user.is_error = True
    #         user.error_message =  Response(
    #             { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
    #             status=status.HTTP_404_NOT_FOUND
    #         )
        
    #     return user
    
    def get_user_by_token_or_404(self, token):
        user_id = Token.objects.get(key=token).user_id
        user = User
        user.is_error = False

        try:
            user = User.objects.get(pk=user_id)            
        except User.DoesNotExist:
            user.is_error = True
            user.error_message =  Response(
                { GeneralConstants.MESSAGE:UserConstants.NOT_FOUND },
                status=status.HTTP_404_NOT_FOUND
            )
        
        return user