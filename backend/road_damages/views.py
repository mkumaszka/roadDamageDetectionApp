from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils.images import save_uploaded_photo_as_binary_array, extract_images
from .utils.files import check_file_extension
from .serializers import DamageSerializer
from .models import RegisteredDamage
from .tasks import make_predictions_to_images


@api_view(['POST'])
def file_upload(request):
    files = request.FILES.getlist("file")
    is_valid = False
    error_serializer = None
    counter = 0
    for file in files:
        file_path = default_storage.save(file.name, ContentFile(file.read()))
        file_type = check_file_extension(file_path)
        if 'image' in file_type:
            filename = save_uploaded_photo_as_binary_array(file_path)
            counter, error_serializer, is_valid = serialize_single_file(counter, error_serializer, filename)
        if 'video' in file_type:
            filenames = extract_images(file_path)
            for filename in filenames:
                counter, error_serializer, is_valid = serialize_single_file(counter, error_serializer, filename)
    make_predictions_to_images.delay()
    if error_serializer is not None:
        to_return = error_serializer.data
    else:
        to_return = {'counter': counter, 'file_type': file_type}
    if is_valid:
        return Response(to_return, status=status.HTTP_201_CREATED)
    return Response(to_return, status=status.HTTP_400_BAD_REQUEST)


def serialize_single_file(counter, error_serializer, filename):
    damage_data = {'photo': filename}
    serializer = DamageSerializer(data=damage_data)
    if serializer.is_valid():
        serializer.save()
        is_valid = True
        counter += 1
    else:
        is_valid = False
        error_serializer = serializer
    return counter, error_serializer, is_valid


class ListDamages(generics.ListCreateAPIView):
    queryset = RegisteredDamage.objects.all()
    serializer_class = DamageSerializer


class DamageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RegisteredDamage.objects.all()
    serializer_class = DamageSerializer
