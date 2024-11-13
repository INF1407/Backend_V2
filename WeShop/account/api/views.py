from .serializers import ProfileSerializer
from rest_framework.views import APIView
from account.models import Profile
from rest_framework.response import Response

class ProfileView(APIView):
    def get(self, request):
        queryset = Profile.objects.all()
        
        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer.data)