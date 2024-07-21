# myapp/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    user_id = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    age_group = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    genres = models.CharField(max_length=255, blank=True, null=True)  # 새로운 필드 추가

    username = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.email


class FileUpload(models.Model):
    mp3_file = models.FileField(upload_to="mp3s/", null=True, blank=True)
    pdf_file = models.FileField(upload_to="pdfs/", null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"File uploaded on {self.upload_date.strftime('%Y-%m-%d %H:%M:%S')}"


class KakaoUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=False)
    gender = models.CharField(max_length=10, blank=True)
    age_range = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nickname


class NaverUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=False)
    gender = models.CharField(max_length=10, blank=True)
    age_range = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nickname


class Post(models.Model):
    GENRES = [
        ("록", "록"),
        ("팝 록", "팝 록"),
        ("메탈", "메탈"),
        ("재즈", "재즈"),
        ("펑크 록", "펑크 록"),
        ("소울", "소울"),
        ("펑크", "펑크"),
        ("얼터너티브 록", "얼터너티브 록"),
        ("인디 록", "인디 록"),
        ("힙합", "힙합"),
        ("레게", "레게"),
        ("프로그레시브 록", "프로그레시브 록"),
        ("포스트 록", "포스트 록"),
        ("하드코어 펑크", "하드코어 펑크"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )
    genre = models.CharField(max_length=20, choices=GENRES)  # 추가된 필드

    @property
    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
