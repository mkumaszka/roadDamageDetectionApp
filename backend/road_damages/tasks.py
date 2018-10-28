from keras import backend as K

from .models import RegisteredDamage
from .celery import app

@app.task
def make_predictions_to_images():
    K.clear_session()
    damages = RegisteredDamage.objects.all()
    damages_no_prediction = [damage for damage in damages if not damage.prediction_set.exists()]
    for damage in damages_no_prediction:
        made_prediction = damage.predict_damage()
        print(made_prediction)
        if not made_prediction:
            success = damage.remove_image()
            print(success)
            damage.delete()
    # yolo.close_session()
    print('--------------End of task----------------')
