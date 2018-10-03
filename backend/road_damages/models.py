from django.db import models
from django.utils.datetime_safe import datetime
from PIL import Image

from .prediction.road_prediction import detect_tables_image
from .settings import IMAGES_ROOT


class RegisteredDamage(models.Model):
    register_date = models.DateTimeField('date registered', default=datetime.now)
    longtitiude = models.FloatField()
    latitude = models.FloatField()
    photo = models.CharField(max_length=200)

    @property
    def photo_url(self):
        return IMAGES_ROOT + str(self.photo)

    def predict_damage(self):
        image = Image.open(self.photo_url)
        boxes, scores, classes = detect_tables_image(image)
        predictions = zip(boxes, scores, classes)
        for box, score, pred_class in predictions:
            bbox = BoundingBox(left=box[0], right=box[1], top=box[2], bottom=box[3])
            bbox.save()
            prediction = Prediction(registered_damage=self, damage_label=pred_class, bounding_box=bbox,
                                    confidence=score)
            prediction.save()


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
