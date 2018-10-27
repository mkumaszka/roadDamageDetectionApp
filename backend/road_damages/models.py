import os

from django.db import models
from django.utils.datetime_safe import datetime
from PIL import Image

from .prediction.road_prediction import detect_tables_image
from .settings import IMAGES_ROOT, MEDIA_ROOT


class RegisteredDamage(models.Model):
    register_date = models.DateTimeField('date registered', default=datetime.now)
    longtitiude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    photo = models.CharField(max_length=200)

    @property
    def photo_url(self):
        return IMAGES_ROOT + str(self.photo)

    def remove_image(self):
        photo_name = str(self.photo)
        photo_path = os.path.join(MEDIA_ROOT, photo_name)
        os.remove(photo_path)
        return os.path.exists(photo_path)

    def predict_damage(self):
        image = Image.open(self.photo_url)
        predictions = detect_tables_image(image)
        print(predictions)
        if len(predictions[0]) is 0:
            return False
        boxes, scores, classes = predictions
        predictions = zip(boxes, scores, classes)
        for box, score, pred_class in predictions:
            bbox = BoundingBox(left=box[0], right=box[1], top=box[2], bottom=box[3])
            bbox.save()
            prediction = Prediction(registered_damage=self, damage_label=pred_class, bounding_box=bbox,
                                    confidence=score)
            prediction.save()
        return True


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

