from django.urls import path

from . import views

app_name = 'road_damages'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:damage_id>/', views.detail, name='detail'),
    path('<int:damage_id>/predictions/', views.detail_with_prediction, name='detail_with_prediction'),
    path('upload_pic/', views.upload_pic, name='upload_pic'),
    path('put_image/', views.put_image, name='put_image'),
    path('put_images/', views.put_images, name='put_images'),
    path('put_video/', views.put_video, name='put_video'),
    path('upload_video/', views.upload_video, name='upload_video'),
    path('upload_multiple_images/', views.upload_multiple_images, name='upload_multiple_images'),
    path('damage/', views.damage, name='damage'),
]
