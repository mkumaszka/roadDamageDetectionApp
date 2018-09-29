from django.db import models
MEDIA_ROOT = 'C:\\Users\\Martyna\\PycharmProjects\\roadDamageDetectionApp\\backend\\'


class RegisteredDamage(models.Model):
    register_date = models.DateTimeField('date registered')
    longtitiude = models.FloatField()
    latitude = models.FloatField()
    photo = models.CharField(max_length=200)
    damage_prediction = models.OneToOneField('Prediction', blank=True, default=None, on_delete=models.SET_NULL, null=True)

    # TODO check how to set proper photo url to be read by site
    @property
    def photo_url(self):
        return MEDIA_ROOT + str(self.photo)


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

