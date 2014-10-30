from rest_framework import serializers

from .models import ContactFormEntry


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormEntry
        fields = ('type', 'content')
