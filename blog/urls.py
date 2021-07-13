from django.urls import path
from . import views #현재폴더의 views.py를 사용할 수 있게 가져오라는 의미

urlpatterns = [
    path('<int:pk>/', views.PostDetail.as_view()),
   # path('<int:pk>/', views.single_post_page),
    path('', views.PostList.as_view()),
   # path('', views.index)
    path('category/<str:slug>/', views.category_page),
    path('tag/<str:slug>/', views.tag_page),
    path('create_post/', views.PostCreate.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('<int:pk>/new_comment/', views.new_comment)
]