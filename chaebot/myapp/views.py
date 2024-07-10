from django.shortcuts import render, redirect
from .forms import FileUploadForm
from django.http import JsonResponse
from .models import FileUpload
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login


# 홈화면
def index(request):
    return render(request, "index.html")


# pdf나오는 결과화면
def result(request):
    return render(request, "result.html")


# 대기화면
def waiting(request):
    return render(request, "waiting.html")


# 로그인화면
def show_login(request):  # `login`을 `show_login`으로 변경
    return render(request, "login.html")


# 회원가입화면
def show_signup(request):  # 첫 번째 `signup`을 `show_signup`으로 변경
    return render(request, "signup.html")


# 로그인동작
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # 수정된 `auth_login` 사용
                return redirect("index")  # `main`을 `home`으로 변경
            else:
                messages.error(request, "회원정보가 없습니다!")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


# 회원가입동작
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")

        if password != password2:
            messages.error(request, "비밀번호가 일치하지 않습니다.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "아이디가 이미 존재합니다.")
            return redirect("signup")

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.save()

        user = authenticate(username=username, password=password)
        return redirect("login")

    return render(request, "signup.html")


# mp3업로드
@csrf_exempt
def upload_mp3(request):
    if request.method == "POST" and request.FILES.get("file"):
        mp3_file = request.FILES["file"]
        file_upload = FileUpload(mp3_file=mp3_file)
        file_upload.save()
        return render(request, "waiting.html")
    return JsonResponse({"error": "Invalid request"}, status=400)
