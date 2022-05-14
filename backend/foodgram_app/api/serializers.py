from rest_framework import serializers

from users.models import User
from foodgram.models import Subscription


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if Subscription.objects.filter(
            following=obj, user=user
            ).first():
            return True
        return False

