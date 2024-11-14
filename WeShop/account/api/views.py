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



class CustomAuthToken(ObtainAuthToken):
    
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
    
    @swagger_auto_schema(
        operation_summary='Obtém o username do usuário',
        operation_description="Retorna o username do usuário ou apenas visitante se o usuário nã",
        security=[{'Token':[]}],
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token de autenticação no formato "token \<<i>valor do token</i>\>"',
                default='token ',
            ),
        ],
        responses={
            200: openapi.Response(
                description='Nome do usuário',
                schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'username': openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            )
        }
    )
    def get(self, request):
        '''
        Parâmetros: o token de acesso
        Retorna: o username ou 'visitante'
        '''
        try:
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1] # token
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            return Response(
                {'username': user.username},
                status=status.HTTP_200_OK)
        except (Token.DoesNotExist, AttributeError):
            return Response(
            {'username': 'visitante'},
            status=status.HTTP_404_NOT_FOUND)

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
