from django.urls import path
from myapp import views as v
from myapp.views import upload_mp3
from django.contrib import admin

urlpatterns = [
    path("", v.home, name="index"),
    path("waiting/", v.waiting, name="waiting"),
    path("result/", v.result, name="result"),
    path("upload/", v.upload_mp3, name="upload_mp3"),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("signup/", v.signup, name="signup"),
    path("age_gender/", v.age_gender, name="age_gender"),
    path("login/", v.show_login, name="login"),
]
