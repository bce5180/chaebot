from django.shortcuts import render, redirect, get_object_or_404
from .forms import FileUploadForm, PostForm
from django.http import JsonResponse
from .models import FileUpload, CustomUser, Post, Comment, Reply
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count
import json
import requests
import base64
import os
import logging
from dotenv import load_dotenv


# 홈화면
def index(request):
    return render(request, "index.html")


# pdf나오는 결과화면
def result(request):
    return render(request, "result.html")


# 대기화면
def waiting(request):
    return render(request, "waiting.html")


# 로그아웃
def logout_view(request):
    logout(request)
    return redirect("index")


# 회원가입화면
def show_signup(request):  # 첫 번째 `signup`을 `show_signup`으로 변경
    return render(request, "signup.html")


# 로그인동작
def login_view(request):
    form = AuthenticationForm()  # 기본 값을 설정합니다.
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        password = request.POST.get("password")
        try:
            user = CustomUser.objects.get(user_id=user_id)
            if user.check_password(password):
                auth_login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                request.session["user_id"] = user.id  # 세션에 user_id 저장
                print(f"Login: user_id {user.id} stored in session.")  # 디버그용 로그
                return redirect("index")
            else:
                messages.error(request, "비밀번호가 틀렸습니다.")
        except CustomUser.DoesNotExist:
            messages.error(request, "회원정보가 없습니다!")
    return render(request, "login.html", {"form": form})


# 회원가입
def signup(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        user_id = data.get("id")
        password = data.get("password")
        password2 = data.get("password2")
        email = data.get("email")

        if password != password2:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        try:
            user = CustomUser.objects.create_user(
                username=username, user_id=user_id, email=email, password=password
            )
            user.save()
            user = authenticate(request, user_id=user_id, password=password)
            auth_login(
                request, user, backend="django.contrib.auth.backends.ModelBackend"
            )
            return redirect("index")
        except IntegrityError:
            return render(
                request,
                "signup.html",
                {"error": "Username, ID or Email already exists"},
            )
    return render(request, "signup.html")


def check_id(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get("user_id")
        exists = CustomUser.objects.filter(user_id=user_id).exists()
        return JsonResponse({"exists": exists})


def check_username(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        exists = CustomUser.objects.filter(username=username).exists()
        return JsonResponse({"exists": exists})


def check_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        exists = CustomUser.objects.filter(email=email).exists()
        return JsonResponse({"exists": exists})


# 성별 연령대
def age_gender(request):
    if request.method == "POST":
        age_group = request.POST.get("age_group")
        gender = request.POST.get("gender")

        # 세션에서 사용자 ID 가져오기
        user_id = request.session.get("user_id")
        print(f"Age/Gender: Retrieved user_id {user_id} from session.")  # 디버그용 로그

        if user_id:
            user = CustomUser.objects.get(id=user_id)
            user.age_group = age_group
            user.gender = gender
            user.save()

            return redirect("select_genres")
        else:
            return redirect("signup")

    return render(request, "age_gender.html")


GENRES = [
    "록",
    "팝 록",
    "메탈",
    "재즈",
    "펑크 록",
    "소울",
    "펑크",
    "얼터너티브 록",
    "인디 록",
    "힙합",
    "레게",
    "프로그레시브 록",
    "포스트 록",
    "하드코어 펑크",
]


# 장르 선택
def select_genres(request):
    if request.method == "POST":
        selected_genres = request.POST.get("selected_genres", "").split(",")
        user_id = request.session.get("user_id")

        print("Selected genres:", selected_genres)  # 디버그용 로그
        print("User ID from session:", user_id)  # 디버그용 로그

        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                user.genres = ",".join(selected_genres)
                user.save()
                del request.session["user_id"]
                print(
                    f"Select Genres: user_id {user_id} deleted from session."
                )  # 디버그용 로그
                return redirect("login")
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist.")
                return redirect("login")
        else:
            return redirect("signup")
    return render(request, "select_genres.html", {"genres": GENRES})


@csrf_exempt
def upload_mp3(request):
    if request.method == "POST" and request.FILES.get("file"):
        song_name = request.POST.get("song_name")
        mp3_file = request.FILES["file"]
        file_upload = FileUpload(song_name=song_name, mp3_file=mp3_file)
        file_upload.save()
        return redirect("/")
    return JsonResponse({"error": "Invalid request"}, status=400)


# chaetting 페이지 로딩
@login_required
def chaetting_view(request):
    posts = Post.objects.annotate(
        comment_count=Count("comments", distinct=True)
        + Count("comments__replies", distinct=True)
    )
    popular_posts = Post.objects.order_by("-created_at")[:5]  # 예시로 최신 5개 인기글

    context = {
        "posts": posts,
        "popular_posts": popular_posts,
        "GENRES": GENRES,
    }
    return render(request, "chaetting.html", context)


# 포스트 생성
@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect("chaetting_view")
        else:
            messages.error(request, "Error creating post.")
    return redirect("chaetting_view")


# 포스트 상세보기
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    total_comments = post.comments.count()
    for comment in post.comments.all():
        total_comments += comment.replies.count()
    popular_posts = Post.objects.order_by("-likes")[:5]
    context = {
        "post": post,
        "total_comments": total_comments,
        "popular_posts": popular_posts,
    }
    return render(request, "post_detail.html", context)


# 좋아요 기능
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse("post_detail", args=[post.id]))


# 댓글 좋아요
@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


# 대댓글 좋아요
@login_required
def like_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if reply.likes.filter(id=request.user.id).exists():
        reply.likes.remove(request.user)
    else:
        reply.likes.add(request.user)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


# 댓글 쓰기
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            comment = Comment(post=post, author=request.user, content=content)
            comment.save()
    return redirect("post_detail", post_id=post.id)


# 대댓글 쓰기
@login_required
def add_reply(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            reply = Reply(comment=comment, author=request.user, content=content)
            reply.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

logger = logging.getLogger(__name__)

def get_spotify_token():
    load_dotenv()  # 환경 변수 로드
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        headers={'Authorization': f'Basic {client_creds_b64}'}
    )
    auth_data = auth_response.json()
    if auth_response.status_code != 200:
        logger.error(f"Failed to retrieve access token: {auth_data}")
        raise Exception(f"Failed to retrieve access token: {auth_data}")
    return auth_data['access_token']

def search_spotify(request):
    try:
        token = get_spotify_token()
        artist = request.GET.get('artist', '').strip()
        track = request.GET.get('track', '').strip()
        
        # 가수와 제목을 이용한 검색 쿼리 구성
        query = ''
        if artist and track:
            query = f'artist:{artist} track:{track}'
        elif artist:
            query = f'artist:{artist}'
        elif track:
            query = f'track:{track}'
        else:
            return JsonResponse({'error': 'Artist or track parameter is required'}, status=400)

        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'https://api.spotify.com/v1/search?type=track&q={query}', headers=headers)
        return JsonResponse(response.json(), safe=False)
    except Exception as e:
        logger.error(f"Error in search_spotify: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)