from django.urls import path

from . import views

app_name = 'road_damages'
urlpatterns = [
    path('file_upload/', views.file_upload, name='file_upload'),
    path('damages/', views.ListDamages.as_view(), name='damages'),
    path('damages/<int:pk>/', views.DamageDetail.as_view(), name='damage_detail'),
]
