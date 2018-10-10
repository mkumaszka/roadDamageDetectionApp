from .models import RegisteredDamage
from .celery import app

@app.task
def make_predictions_to_images():
    damages = RegisteredDamage.objects.all()
    damages_no_prediction = [damage for damage in damages if not damage.prediction_set.exists()]
    for damage in damages_no_prediction:
        made_prediction = damage.predict_damage()
        if not made_prediction:
            damage.delete()
