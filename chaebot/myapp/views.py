from django.shortcuts import render, redirect
from .forms import FileUploadForm


def index(request):
    return render(request, "index.html")


def result(request):
    return render(request, "result.html")


def file_upload(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("waiting")  # 업로드 성공 후 리디렉션
    else:
        form = FileUploadForm()
    return render(request, "waiting.html", {"form": form})
