from django.urls import path
from myapp import views as v  # myapp은 사용 중인 앱의 이름으로 변경
from myapp.views import upload_mp3
from django.contrib import admin

urlpatterns = [
    path("", v.home, name="index"),
    path("waiting/", v.waiting, name="waiting"),
    path("result/", v.result, name="result"),
    path("upload/", v.upload_mp3, name="upload_mp3"),
    path("accounts/", include("allauth.urls")),
    path("login/", v.show_login, name="login"),
    path("signup/", v.signup, name="signup"),
    path("login_view/", v.login_view, name="login_view"),
    path("admin/", admin.site.urls),
]
