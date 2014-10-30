from rest_framework import serializers

from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    reference = serializers.Field()

    class Meta:
        model = Alert
        fields = ('id', 'datetime', 'content', 'viewed',
                  'reference', 'reference_type')

    def transform_reference(self, obj, value):
        from visualorg.apps.accounts.serializers import CondensedUserSerializer
        if obj.reference_type.name == 'user':
            return CondensedUserSerializer(obj.reference).data

    def transform_reference_type(self, obj, value):
        return obj.reference_type.name
