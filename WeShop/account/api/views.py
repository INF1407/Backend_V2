from .serializers import ProfileSerializer
from rest_framework.views import APIView
from account.models import Profile
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

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
