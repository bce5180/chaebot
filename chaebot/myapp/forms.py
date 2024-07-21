# forms.py

from django import forms
from .models import FileUpload
from .models import Post
from .constants import GENRES
from .models import Post, Comment


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ["mp3_file"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["genre", "title", "content"]
        widgets = {
            "genre": forms.Select(choices=Post.GENRES),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
