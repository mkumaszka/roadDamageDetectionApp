from rest_framework.serializers import ModelSerializer

from .models import RegisteredDamage, BoundingBox, Prediction


class BoundingBoxSerializer(ModelSerializer):
    class Meta:
        model = BoundingBox
        fields = ('left', 'right', 'top', 'bottom')


class PredictionSerializer(ModelSerializer):
    class Meta:
        model = Prediction
        fields = ('registered_damage', 'damage_label', 'bounding_box', 'confidence')
        depth = 1


class DamageSerializer(ModelSerializer):
    prediction_set = PredictionSerializer(many=True, required=False)

    class Meta:
        model = RegisteredDamage
        fields = ('id', 'register_date', 'longtitiude', 'latitude', 'photo', 'prediction_set')
