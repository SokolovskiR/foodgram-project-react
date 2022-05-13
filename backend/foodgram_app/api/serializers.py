from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = User

    #### to be implemented###
    # add is_subscribed field