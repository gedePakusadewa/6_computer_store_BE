from django.contrib.auth.models import User
from rest_framework.response import Response
from computer_store.constants.general import UserConstants, GeneralConstants, AdminConstants
from rest_framework import status
from rest_framework.authtoken.models import Token

class AdminHelper():  
    def get_admin_or_400(self, token):
        user_id = Token.objects.get(key=token).user_id
        user = User
        user.is_error = False

        try:
            user = User.objects.get(pk=user_id, is_superuser=1)
        except User.DoesNotExist:
            user.is_error = True
            user.error_message =  Response(
                { GeneralConstants.MESSAGE:AdminConstants.INVALID_ADMIN },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return user