# forms.py

from django import forms
from .models import FileUpload, Post


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ["mp3_file"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "genre",
            "mp3_file",
            "sheet_file",
        ]  # MP3와 악보 파일 필드 추가
