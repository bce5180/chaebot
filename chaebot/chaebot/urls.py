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
    path("", v.index, name="index"),  # 홈페이지로 바로 index 뷰를 연결
    path("result/", v.result, name="result"),  # 홈페이지로 바로 index 뷰를 연결
    path("waiting/", v.waiting, name="waiting"),
    path("upload/", v.upload_mp3, name="upload_mp3"),
    path("login/", v.login_view, name="login"),
    path("logout/", v.logout_view, name="logout"),
    path("signup/", v.signup, name="signup"),
    path("age_gender/", v.age_gender, name="age_gender"),
    path("login_view/", v.login_view, name="login_view"),
    path("accounts/", include("allauth.urls")),
    path("select_genres/", v.select_genres, name="select_genres"),
    path("check_id/", v.check_id, name="check_id"),
    # chaetting
    path("chaetting_view/", v.chaetting_view, name="chaetting_view"),
    path("create_post/", v.create_post, name="create_post"),
    path("post/<int:post_id>/", v.post_detail, name="post_detail"),
    path("post/<int:post_id>/like/", v.like_post, name="like_post"),
    path("comment/<int:comment_id>/like/", v.like_comment, name="like_comment"),
    path("reply/<int:reply_id>/like/", v.like_reply, name="like_reply"),
    path("post/<int:post_id>/comment/", v.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/reply/", v.add_reply, name="add_reply"),
]
