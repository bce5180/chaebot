"""
URL configuration for chaebot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from myapp import views as v


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", v.home, name="home"),  # 홈페이지로 바로 index 뷰를 연결
    path("index/", v.index, name="index"),  # 홈페이지로 바로 index 뷰를 연결
    path("result/", v.result, name="result"),  # 홈페이지로 바로 index 뷰를 연결
    path("waiting/", v.waiting, name="waiting"),
    path("upload/", v.upload_mp3, name="upload_mp3"),
    path("accounts/", include("allauth.urls")),
]
