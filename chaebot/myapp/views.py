from django.shortcuts import render, redirect
from .forms import FileUploadForm
from django.http import JsonResponse
from .models import FileUpload
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, "index.html")


def home(request):
    return render(request, "home.html")


def result(request):
    return render(request, "result.html")


@csrf_exempt
def upload_mp3(request):
    if request.method == "POST" and request.FILES.get("file"):
        mp3_file = request.FILES["file"]
        file_upload = FileUpload(mp3_file=mp3_file)
        file_upload.save()
        # Redirect to a waiting page that will handle the redirection to result after 5 seconds
        return render(request, "waiting.html")
    return JsonResponse({"error": "Invalid request"}, status=400)


def waiting(request):
    return render(request, "waiting.html")


def home(request):
    conversion_count = FileUpload.objects.count()  # 파일 업로드 수를 세는 쿼리
    return render(request, "home.html", {"conversion_count": conversion_count})
