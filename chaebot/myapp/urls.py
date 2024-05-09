# urls.py
from django.urls import path
from myapp.views import home

urlpatterns = [
    path("", home, name="home"),  # 루트 URL에 대한 처리
    path("home/", home, name="home"),  # /home/에 대한 처리
]
