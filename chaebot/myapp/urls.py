from django.urls import path
from myapp import views as v  # myapp은 사용 중인 앱의 이름으로 변경
from myapp.views import upload_mp3

urlpatterns = [
    path("", v.index, name="index"),  # 홈페이지로 바로 index 뷰를 연결
    path("result/", v.result, name="result"),  # 홈페이지로 바로 index 뷰를 연결
    path("waiting/", v.waiting, name="waiting"),
    path("result/", v.result, name="result"),
    path("upload/", v.upload_mp3, name="upload_mp3"),
]
