from django.forms import modelformset_factory
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils.images import save_uploaded_photo_as_binary_array
from .serializers import DamageSerializer
from .forms import ImageUploadForm, FileUploadForm
from .models import RegisteredDamage


@require_POST
def upload_pic(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.cleaned_data['image']
            filename = save_uploaded_photo_as_binary_array(photo)
            m = RegisteredDamage(register_date=timezone.now(), longtitiude=1.0, latitude=123.432, photo=filename)
            m.save()
            return HttpResponse('image upload success')
    return HttpResponseForbidden('allowed only via POST')


@require_POST
def upload_multiple_images(request):
    out_files = ''
    for image in request.FILES.getlist("image"):
        filename = save_uploaded_photo_as_binary_array(image)
        damage = RegisteredDamage(register_date=timezone.now(), longtitiude=1.0, latitude=123.432, photo=filename)
        out_files += filename + '\n'
        damage.save()
    return HttpResponse(out_files)


@require_POST
def upload_video(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.cleaned_data['file']
            # TODO process video
            # filename = save_uploaded_photo_as_binary_array(photo)
            # m = RegisteredDamage(register_date=timezone.now(), longtitiude=1.0, latitude=123.432, photo=filename)
            # m.save()
            return HttpResponse('video upload success')
        return HttpResponseForbidden('form not valid')
    return HttpResponseForbidden('allowed only via POST')


# For mobile app - rest api
@api_view(['POST'])
def file_upload(request):
    photos = request.FILES.getlist("file")
    is_valid = False
    error_serializer = None
    counter = 0
    for photo in photos:
        filename = save_uploaded_photo_as_binary_array(photo)
        damage_data = {'photo': filename}
        serializer = DamageSerializer(data=damage_data)
        if serializer.is_valid():
            serializer.save()
            is_valid = True
            counter += 1
        else:
            is_valid = False
            error_serializer = serializer
    if error_serializer is not None:
        to_return = error_serializer.data
    else:
        to_return = {'counter': counter}
    if is_valid:
        return Response(to_return, status=status.HTTP_201_CREATED)
    return Response(to_return, status=status.HTTP_400_BAD_REQUEST)


class ListDamages(generics.ListCreateAPIView):
    queryset = RegisteredDamage.objects.all()
    serializer_class = DamageSerializer


class DamageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RegisteredDamage.objects.all()
    serializer_class = DamageSerializer
