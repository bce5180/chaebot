# myapp/models.py

from django.db import models


class FileUpload(models.Model):
    mp3_file = models.FileField(upload_to="mp3s/", null=True, blank=True)
    pdf_file = models.FileField(upload_to="pdfs/", null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"File uploaded on {self.upload_date.strftime('%Y-%m-%d %H:%M:%S')}"


class KakaoUser(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=False)
    gender = models.CharField(max_length=10, blank=True)
    age_range = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nickname


class NaverUser(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=False)
    gender = models.CharField(max_length=10, blank=True)
    age_range = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nickname
