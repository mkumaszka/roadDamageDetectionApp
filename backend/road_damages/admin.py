from django.contrib import admin

from .models import RegisteredDamage, BoundingBox, Prediction

admin.site.register(RegisteredDamage)
admin.site.register(BoundingBox)
admin.site.register(Prediction)


