from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import UniqueConstraint

class CustomUser(AbstractUser):
    user_id = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    age_group = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    genres = models.CharField(max_length=255, blank=True, null=True)  # 새로운 필드 추가

    username = models.CharField(max_length=150)

    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.email


class FileUpload(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    song_name = models.CharField(max_length=255, null=True, blank=True)
    mp3_file = models.FileField(upload_to="mp3s/", null=True, blank=True)
    youtube_url = models.URLField(null=True, blank=True)  
    pdf_file = models.FileField(upload_to="pdfs/", null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    genre = models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
        return f"{self.song_name} - Uploaded by {self.user.username} on {self.upload_date.strftime('%Y-%m-%d %H:%M:%S')}"

    def save(self, *args, **kwargs):
        initial = not self.pk  # 처음 저장인지 확인

        # 첫 번째 저장
        super().save(*args, **kwargs)

        # 파일명을 설정하는 로직을 첫 번째 저장 후에만 수행
        if initial and self.song_name and self.pdf_file:
            self.rename_pdf_file()
            # 파일명 변경 후 다시 저장 (필요한 경우에만)
            super().save(*args, **kwargs)



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
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    genre = models.CharField(max_length=100)
    mp3_file = models.FileField(upload_to="mp3s/", blank=True, null=True)
    sheet_file = models.FileField(upload_to="sheets/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_comments", blank=True
    )

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Reply(models.Model):
    comment = models.ForeignKey(
        Comment, related_name="replies", on_delete=models.CASCADE
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_replies", blank=True
    )

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Reply by {self.author} on {self.comment}"

class Track(models.Model):
    spotify_track_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album_image_url = models.URLField()
    selection_count = models.PositiveIntegerField(default=0)
    genre = models.CharField(max_length=50, null=True, blank=True)
    file_upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['spotify_track_id', 'genre'], name='unique_track_genre')
        ]

    def __str__(self):
        return f"{self.name} by {self.artist} ({self.genre})"

class UserTrack(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

