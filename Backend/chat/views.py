from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, action, permission_classes
from .models import User, Conversation, ConversationParticipant, Message
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    MessageSerializer,
    RegistrationSerializer,
    PasswordChangeSerializer,
    LoginSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status, viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import MethodNotAllowed
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings


# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def check_server_status(request):
    return Response({'status': 'ok'})


@extend_schema_view(
    register=extend_schema(description='Register a new user'),
    # login=extend_schema(description='Login a user and obtain JWT tokens'),
    change_password=extend_schema(description='Change user password'),
    logout=extend_schema(description='Logout a user'),
)
class AuthViewSet(viewsets.ViewSet):
    @extend_schema(request=RegistrationSerializer, responses=UserSerializer)
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=LoginSerializer, responses={'200': 'Login successful'})
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=PasswordChangeSerializer, responses={'200': 'Password changed successfully'})
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @extend_schema(request={'email': str}, responses={'200': 'Password reset email sent'})
    # @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    # def forget_password(self, request):
    #     email = request.data.get('email')
    #     try:
    #         user = User.objects.get(email=email)
    #         # Generate password reset token
    #         token = default_token_generator.make_token(user)
    #         uid = urlsafe_base64_encode(force_bytes(user.pk))

    #         # Send password reset email
    #         reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
    #         subject = "Password Reset Request"
    #         message = f"Click the following link to reset your password: {reset_url}"
    #         send_mail(
    #             subject,
    #             message,
    #             settings.EMAIL_HOST_USER,
    #             [email],
    #             fail_silently=False,
    #         )
    #         return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
    #     except User.DoesNotExist:
    #         return Response({'error': 'No user found with this email address'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    list=extend_schema(description='List all users and  Search user by username or email'),
    retrieve=extend_schema(description='Retrieve a specific user'),
    create=extend_schema(description='Create a new user'),
    update=extend_schema(description='Update a user'),
    partial_update=extend_schema(description='Partially update a user'),
    destroy=extend_schema(description='Delete a user'),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')
