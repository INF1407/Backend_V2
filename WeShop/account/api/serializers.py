from rest_framework import serializers
from account.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'date_of_birth']
        

    def to_representation(self, instance):
        """
        Customize the serialized output to include user-related data.
        """
        representation = super().to_representation(instance)
        representation['username'] = instance.user.username  # Add username to the serialized output
        return representation