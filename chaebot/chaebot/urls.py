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
from django.conf import settings  # 추가
from django.conf.urls.static import static  # 추가

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", v.index, name="index"),  # 홈페이지로 바로 index 뷰를 연결
    # user관리
    path("signup/", v.signup, name="signup"),
    path("login/", v.login_view, name="login"),
    path("logout/", v.logout_view, name="logout"),
    path("accounts/", include("allauth.urls")),
    path("check_id/", v.check_id, name="check_id"),
    path("check_username/", v.check_username, name="check_username"),
    path("check_email/", v.check_email, name="check_email"),
    # 좋아하는 장르 선택
    path("select_genres/", v.select_genres, name="select_genres"),
    # 나이 성별 선택
    path("age_gender/", v.age_gender, name="age_gender"),
    # chaetting
    path('chaetting/', v.recommendation_and_chaetting_view, name='chaetting_view'),
    path("create_post/", v.create_post, name="create_post"),
    path("post/<int:post_id>/", v.post_detail, name="post_detail"),
    path("post/<int:post_id>/like/", v.like_post, name="like_post"),
    path("comment/<int:comment_id>/like/", v.like_comment, name="like_comment"),
    path("reply/<int:reply_id>/like/", v.like_reply, name="like_reply"),
    path("post/<int:post_id>/comment/", v.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/reply/", v.add_reply, name="add_reply"),
    # 스포티파이
    path('search_spotify/', v.search_spotify, name='search_spotify'),
    path('save_selected_track/', v.save_selected_track, name='save_selected_track'),
    # 파일저장
    path("upload/", v.upload_mp3, name="upload_mp3"),
    path('result/', v.result, name='result'),
    path('save_filename/', v.save_filename, name='save_filename'),
    path('save_file_upload_genre/', v.save_file_upload_genre, name='save_file_upload_genre'),
    path('download_pdf/', v.download_pdf, name='download_pdf'),
    # 대기화면
    path("waiting/", v.waiting, name="waiting"),
    # 모델 백그라운드 재생
    path('process_conversion/', v.process_conversion, name='process_conversion'),
    # 마이페이지
    path("mypage/", v.mypage, name="mypage"),
    path('update_profile/', v.update_profile, name='update_profile'),
    path('delete_account/', v.delete_account, name='delete_account'),
    path('download_pdf/<int:conversion_id>/', v.download_pdf, name='download_pdf'),
    path('update_note/<int:file_id>/', v.update_note, name='update_note'),
    path('delete_post/<int:post_id>/', v.delete_post, name='delete_post'),
]

# Static 및 Media 파일 URL 패턴 추가
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
