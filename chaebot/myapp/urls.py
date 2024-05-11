from django.urls import path
from myapp.views import index  # myapp은 사용 중인 앱의 이름으로 변경

urlpatterns = [
    path("", index, name="index"),  # 홈페이지로 바로 index 뷰를 연결
]
