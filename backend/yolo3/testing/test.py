from PIL import Image

from backend.road_damages.prediction.road_prediction import detect_tables_image

image = Image.open(r'C:\Users\Martyna\PycharmProjects\roadDamageDetectionApp\backend\media\images\car.jpg')
boxes, scores, classes = detect_tables_image(image)
predictions = zip(boxes, scores, classes)
for box, score, pred_class in predictions:
    print(box)
    print(score)
    print(pred_class)