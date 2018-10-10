from django.forms import modelformset_factory
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils.images import save_uploaded_photo_as_binary_array
from .serializers import DamageSerializer
from .forms import ImageUploadForm, FileUploadForm
from .models import RegisteredDamage


# For browser website


def index(request):
    all_damages = RegisteredDamage.objects.all()
    context = {
        'all_damages': all_damages
    }
    return render(request, 'road_damages/index.html', context)


def detail(request, damage_id):
    try:
        damage = RegisteredDamage.objects.get(pk=damage_id)
    except RegisteredDamage.DoesNotExist:
        raise Http404("Damage not in database")
    return render(request, 'road_damages/detail.html', {'damage': damage})


def detail_with_prediction(request, damage_id):
    response = "You're looking at the prediction of damage %s."
    return HttpResponse(response % damage_id)


def put_image(request):
    return render(request, 'road_damages/put_image.html')


def put_images(request):
    return render(request, 'road_damages/put_images.html')


def put_video(request):
    return render(request, 'road_damages/video_uploader.html')


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
def damage(request):
    photo = request.data['photo']
    filename = save_uploaded_photo_as_binary_array(photo)
    request.data['photo'] = filename
    serializer = DamageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

