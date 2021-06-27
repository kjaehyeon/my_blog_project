from django.urls import path
from . import views #현재폴더의 views.py를 사용할 수 있게 가져오라는 의미

urlpatterns = [
    path('<int:pk>/', views.single_post_page),
    path('', views.index)
]