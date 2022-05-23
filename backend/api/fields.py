import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Custom field to convert Base64 string to file."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(
                base64.b64decode(imgstr),
                name=id.urn[9:] + '.' + ext
            )
        return super(Base64ImageField, self).to_internal_value(data)

    def to_representation(self, value):
        return self.context.get('request').build_absolute_uri(value.url)
