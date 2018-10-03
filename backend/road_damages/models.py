from django.db import models
from django.utils.datetime_safe import datetime

from .settings import IMAGES_ROOT


class RegisteredDamage(models.Model):
    register_date = models.DateTimeField('date registered', default=datetime.now)
    longtitiude = models.FloatField()
    latitude = models.FloatField()
    photo = models.CharField(max_length=200)
    damage_prediction = models.OneToOneField('Prediction', blank=True, default=None, on_delete=models.SET_NULL,
                                             null=True)

    @property
    def photo_url(self):
        return IMAGES_ROOT + str(self.photo)


class BoundingBox(models.Model):
    left = models.FloatField()
    right = models.FloatField()
    top = models.FloatField()
    bottom = models.FloatField()


class Prediction(models.Model):
    registered_damage = models.ForeignKey(RegisteredDamage, on_delete=models.CASCADE)
    damage_label = models.CharField(max_length=50)
    bounding_box = models.ForeignKey(BoundingBox, on_delete=models.PROTECT)
    confidence = models.FloatField()

