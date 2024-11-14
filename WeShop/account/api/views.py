from .serializers import ProfileSerializer
from rest_framework.views import APIView
from account.models import Profile
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import login

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
        operation_summary='Obter o token de autenticação',
        operation_description='Retorna o token em caso de sucesso na autenticação ou HTTP 401',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['username', 'password', ],
        ),
        responses={
            status.HTTP_200_OK: 'Token is returned.',
            status.HTTP_401_UNAUTHORIZED: 'Unauthorized request.',
    },
)
class CustomAuthToken(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
            serializer = self.serializer_class(data=request.data, context={'request': request})
            if serializer.is_valid():
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    token, _ = Token.objects.get_or_create(user=user)
                    login(request, user)
                    return Response({'token': token.key})
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({'token': token.key})
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class ProfileView(APIView):
    def get(self, request):
        queryset = Profile.objects.all()
        
        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer.data)
    
class RegisterUserAPI(APIView):
    """
    API to register a new user and their profile.
    """
    def post(self, request):
        """
        Create a new user and their associated profile.
        """
        # Extract user data from the request
        user_data = {
            'username': request.data.get('username'),
            'password': request.data.get('password'),
            'email': request.data.get('email'),
        }

        # Validate required fields
        if not all(user_data.values()):
            return Response({"error": "Username, password, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the user
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                email=user_data['email']
            )

            # Create a profile for the user (if profile-specific data is provided)
            profile_data = {
                'date_of_birth': request.data.get('date_of_birth')
            }
            serializer = ProfileSerializer(data=profile_data)
            if serializer.is_valid():
                serializer.save(user=user)

            return Response({"message": "User and profile created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
