from rest_framework.serializers import ModelSerializer

from .models import RegisteredDamage


class DamageSerializer(ModelSerializer):
    class Meta:
        model = RegisteredDamage
        fields = '__all__'
