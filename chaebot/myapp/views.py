from django.shortcuts import render, redirect, get_object_or_404
from .forms import FileUploadForm, PostForm
from django.http import JsonResponse
from .models import FileUpload, CustomUser, Post, Comment, Reply, Track, UserTrack
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
from django.conf import settings
from .ai_model import convert_mp3_to_pdf
import time


# 홈화면
def index(request):
    return render(request, "index.html")


# 대기화면
@login_required
def waiting(request):
    file_upload_id = request.session.get('file_upload_id')
    if not file_upload_id:
        return JsonResponse({"error": "No file upload ID in session"}, status=400)

    return render(request, 'waiting.html', {'file_upload_id': file_upload_id})


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
@csrf_exempt  
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user_id = request.POST.get("id")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")

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
            request.session['user_id'] = user.id  # 세션에 사용자 ID 저장
            return redirect("age_gender")
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


@login_required
def upload_mp3(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            file_upload.user = request.user
            mp3_file = request.FILES['file']
            
            # 파일 이름에서 확장자를 제외한 부분만 저장
            file_name, file_extension = os.path.splitext(mp3_file.name)
            file_upload.song_name = file_name
            file_upload.mp3_file = mp3_file
            file_upload.save()

            request.session['file_upload_id'] = file_upload.id
            return redirect('waiting')
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
@csrf_exempt
def process_conversion(request):
    if request.method == 'POST':
        file_upload_id = request.session.get('file_upload_id')
        if not file_upload_id:
            return JsonResponse({"error": "No file upload ID in session"}, status=400)

        file_upload = get_object_or_404(FileUpload, id=file_upload_id, user=request.user)

        # PDF 파일명 설정
        pdf_file_name = f"{file_upload.song_name}.pdf"
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', pdf_file_name)

        # AI 모델 실행
        convert_mp3_to_pdf(file_upload.mp3_file.path, pdf_file_path)

        # 파일 경로를 모델에 저장
        file_upload.pdf_file.name = os.path.join('pdfs', pdf_file_name)
        file_upload.save()

        # 인위적으로 지연 시간을 추가하여 로딩 화면이 충분히 표시되도록 함
        time.sleep(5)  # 5초 지연

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)



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

@csrf_exempt
@login_required
def save_selected_track(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if not data:
                raise ValueError("No data provided")

            artist = data.get('artist')
            track_name = data.get('track')
            spotify_track_id = data.get('spotify_track_id')
            album_image_url = data.get('album_image_url')

            # 필수 필드 확인
            if not artist:
                return JsonResponse({'status': 'error', 'message': 'Artist is required'}, status=400)
            if not track_name:
                return JsonResponse({'status': 'error', 'message': 'Track name is required'}, status=400)
            if not spotify_track_id:
                return JsonResponse({'status': 'error', 'message': 'Spotify track ID is required'}, status=400)
            if not album_image_url:
                return JsonResponse({'status': 'error', 'message': 'Album image URL is required'}, status=400)

            # 트랙이 이미 존재하는지 확인
            track, created = Track.objects.get_or_create(
                spotify_track_id=spotify_track_id,
                defaults={'name': track_name, 'artist': artist, 'album_image_url': album_image_url}
            )

            if not created:
                # 트랙이 이미 존재하면 selection_count를 증가시킴
                track.selection_count += 1
                track.save()
            else:
                # 새로 생성된 트랙이면 selection_count는 1로 설정됨
                track.selection_count = 1
                track.save()

            # UserTrack에 정보 저장
            user_track, user_track_created = UserTrack.objects.get_or_create(
                user=request.user,
                track=track
            )

            if not user_track_created:
                # 이미 존재하면 시간 업데이트 (선택 시간 갱신)
                user_track.timestamp = timezone.now()
                user_track.save()

            return JsonResponse({'status': 'success'}, status=200)
        except ValueError as ve:
            return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
        except Exception as e:
            # 여기에서 오류 메시지를 로그로 출력
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def result(request):
    file_upload_id = request.session.get('file_upload_id')
    if not file_upload_id:
        return JsonResponse({"error": "No file upload ID in session"}, status=400)

    file_upload = get_object_or_404(FileUpload, id=file_upload_id, user=request.user)
    initial_pdf_name = os.path.splitext(os.path.basename(file_upload.pdf_file.name))[0]

    return render(request, 'result.html', {'initial_pdf_name': initial_pdf_name})



@login_required

#파일 이름 사용자 정보대로 수정
@login_required
@csrf_exempt
def save_filename(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        filename = data.get('filename')
        file_upload_id = request.session.get('file_upload_id')
        if filename and file_upload_id:
            file_upload = get_object_or_404(FileUpload, id=file_upload_id, user=request.user)

            # 기존 PDF 파일 경로
            old_pdf_file_path = file_upload.pdf_file.path
            
            # 새로운 PDF 파일 경로
            new_pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', f"{filename}.pdf")
            
            # 파일명 변경
            os.rename(old_pdf_file_path, new_pdf_file_path)
            
            # 모델에 새 파일 경로 저장
            file_upload.pdf_file.name = os.path.join('pdfs', f"{filename}.pdf")
            file_upload.song_name = filename
            file_upload.save()
            
            return JsonResponse({'message': 'Filename saved successfully.'})
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)