from PIL import Image

from backend.road_damages.prediction.road_prediction import detect_tables_image
fpath = r'C:\Users\Martyna\PycharmProjects\roadDamageDetectionApp\backend\media\images\car2.jpg'
image = Image.open(fpath)
boxes, scores, classes = detect_tables_image(image, fpath)
predictions = zip(boxes, scores, classes)
for box, score, pred_class in predictions:
    print(box)
    print(score)
    print(pred_class)