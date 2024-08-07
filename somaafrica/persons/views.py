import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from somaafrica.commons.authentication_backends import AuthenticationError

LOGGER = logging.getLogger(__name__)


class LoginAPIView(APIView):

    def post(self, request):
        """
        Return a list of all users.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        # pdb.set_trace()
        LOGGER.info(f"Username: {username} and Password: {password}")
        try:
            user = authenticate(request, username=username, password=password)
            # pdb.set_trace()
            user_response = {
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            return Response({"message": "OK", "user": user_response})
        except (AuthenticationError, User.DoesNotExist) as e:
            # pdb.set_trace()
            LOGGER.error(e)
            return Response(
                {
                    "message": str(e),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
