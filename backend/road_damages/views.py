import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST

from .utils.files import save_binary, hash_file
from .utils.images import image_to_byte_array
from .forms import ImageUploadForm
from .models import RegisteredDamage
from .settings import IMAGES_ROOT


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


@require_POST
def upload_pic(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.cleaned_data['image']
            photo_path = default_storage.save(photo.name, ContentFile(photo.read()))
            path = os.path.join(IMAGES_ROOT, photo_path)
            image_byte_array = image_to_byte_array(path)
            filename = hash_file(image_byte_array)
            filename = filename + '.png'
            curr_dir = os.getcwd()
            path_to_save = os.path.join(IMAGES_ROOT, filename)
            save_binary(path_to_save, image_byte_array)
            m = RegisteredDamage(register_date=timezone.now(), longtitiude=1.0, latitude=123.432, photo=filename)
            path_to_remove = os.path.join(curr_dir, path)
            os.remove(path_to_remove)
            m.save()
            return HttpResponse('image upload success')
    return HttpResponseForbidden('allowed only via POST')
