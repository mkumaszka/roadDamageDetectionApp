from django.urls import path

from . import views

app_name = 'road_damages'
urlpatterns = [
    path('upload_video/', views.upload_video, name='upload_video'),
    path('upload_multiple_images/', views.upload_multiple_images, name='upload_multiple_images'),
    path('file_upload/', views.file_upload, name='file_upload'),
    path('damages/', views.ListDamages.as_view(), name='damages'),
    path('damages/<int:pk>/', views.DamageDetail.as_view(), name='damage_detail'),
]
