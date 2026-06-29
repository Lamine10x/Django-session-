from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from .serializers import RegisterSerializer, UserSerializer
from .services import UserService

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = UserService.register_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    role=serializer.validated_data.get('role')
                )
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
