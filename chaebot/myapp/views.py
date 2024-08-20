from django.shortcuts import render, redirect, get_object_or_404
from .forms import FileUploadForm, PostForm
from django.http import JsonResponse
from .models import FileUpload, CustomUser, Post, Comment, Reply, Track, UserTrack, FileUpload
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
from .ai_model import chaebot
import time
from random import sample
import random
import shutil
from django.http import FileResponse, Http404




GENRES = [
    "록",
    "팝",
    "메탈",
    "재즈",
    "펑크",
    "얼터너티브",
    "인디",
    "힙합",
    "레게",
]


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


@login_required
def mypage(request):
    # 유저의 업로드 파일을 날짜별로 그룹화
    uploaded_files = FileUpload.objects.filter(user=request.user).order_by('-upload_date')
    uploaded_files_by_date = {}

    for file in uploaded_files:
        date = file.upload_date.strftime('%Y-%m-%d')
        if date not in uploaded_files_by_date:
            uploaded_files_by_date[date] = []
        uploaded_files_by_date[date].append(file)
    
    # 내가 쓴 글을 날짜별로 그룹화
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    posts_by_date = {}

    for post in posts:
        date = post.created_at.strftime('%Y-%m-%d')
        if date not in posts_by_date:
            posts_by_date[date] = []
        posts_by_date[date].append(post)

    # 장르 데이터 가져오기
    genres = [
        "록",
        "팝",
        "메탈",
        "재즈",
        "펑크",
        "얼터너티브",
        "인디",
        "힙합",
        "레게",
    ]
    
    # 사용자가 선택한 장르를 가져옵니다. 
    # 예를 들어, User 모델에 genres 필드가 있다고 가정하면:
    selected_genres = request.user.genres.split(',') if request.user.genres else []

    return render(request, 'mypage.html', {
        'uploaded_files_by_date': uploaded_files_by_date,
        'posts_by_date': posts_by_date,
        'genres': genres,  # 장르 리스트 전달
        'selected_genres': selected_genres,  # 선택된 장르 전달
    })


@login_required
def update_profile(request):
    user = request.user
    selected_genres = user.genres.split(', ') if user.genres else []

    if request.method == 'POST':
        user.user_id = request.POST.get('user_id')  # 수정 가능하도록 설정
        user.email = request.POST.get('email')
        user.age_group = request.POST.get('age_group')
        user.gender = request.POST.get('gender')
        user.genres = ', '.join(request.POST.getlist('genres'))  # 선택한 장르를 저장

        # 비밀번호 변경이 입력된 경우
        password = request.POST.get('password')
        if password:
            user.set_password(password)

        user.save()
        messages.success(request, '프로필이 업데이트되었습니다.')
        return redirect('mypage')

    uploaded_files_by_date = (
        FileUpload.objects.filter(user=user)
        .order_by('-upload_date')
        .values('song_name', 'pdf_file', 'upload_date', 'note')
    )
    my_posts = Post.objects.filter(author=user).order_by('-created_at')
    notifications = Notification.objects.filter(user=user).order_by('-timestamp')

    return render(
        request,
        'mypage.html',
        {
            'genres': GENRES,
            'selected_genres': selected_genres,
            'uploaded_files_by_date': uploaded_files_by_date,
            'my_posts': my_posts,
            'notifications': notifications,
            'user': user,
        },
    )


@login_required
def delete_account(request):
    user = request.user
    user.delete()
    messages.success(request, '회원 탈퇴가 완료되었습니다.')
    return redirect('index')


@login_required
def download_pdf(request, file_id):
    file = FileUpload.objects.get(id=file_id, user=request.user)
    file_path = file.pdf_file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        messages.error(request, 'PDF 파일이 존재하지 않습니다.')
        return redirect('mypage')


@login_required
def update_note(request, file_id):
    file = get_object_or_404(FileUpload, id=file_id, user=request.user)
    
    if request.method == 'POST':
        note = request.POST.get('note')
        file.note = note
        file.save()
        return JsonResponse({'success': True, 'file_id': file.id})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})



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

        try:
            # 입력에 따라 다른 함수 호출
            if file_upload.mp3_file:
                # mp3 파일로 변환 진행
                bot = chaebot(mp3_file_path=file_upload.mp3_file.path)
            elif file_upload.youtube_url:
                # 유튜브 링크로 변환 진행
                bot = chaebot(youtube_link=file_upload.youtube_url)
            else:
                return JsonResponse({"error": "No valid input provided for conversion"}, status=400)

            # 변환 과정 실행
            bot.main()
            new_pdf_file_name = f"{file_upload.id}_drum.pdf"

            # 변환된 PDF 파일을 지정된 위치로 이동
            if os.path.exists("drum_pattern.pdf"):
                print("drum_pattern.pdf 파일이 생성되었습니다.")
                # 새 PDF 파일 이름 설정 (예: "fileupload_id_drum.pdf")
                new_pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', new_pdf_file_name)

                try:
                    shutil.move(drum_pdf_path, new_pdf_file_path)
                except Exception as e:
                    print(f"PDF 파일 이동 중 오류 발생: {e}")
                    return JsonResponse({"error": "PDF file move failed"}, status=500)


                # 파일 경로를 모델에 저장
                file_upload.pdf_file = os.path.join('pdfs', new_pdf_file_name)
                file_upload.save()
            else:
                print("drum_pattern.pdf 파일이 존재하지 않습니다.")
                return JsonResponse({"error": "PDF file not found"}, status=500)

            time.sleep(5)  # 5초 지연

            return JsonResponse({"status": "success", "redirect_url": reverse('result')}, status=200)
        except FileNotFoundError as fnf_error:
            print(f"FileNotFoundError: {fnf_error}")
            return JsonResponse({"error": "File not found"}, status=500)
        except Exception as e:
            print(f"Error during conversion: {e}")
            import traceback
            traceback.print_exc()  # 스택 트레이스를 로그에 출력
            return JsonResponse({"error": "Conversion failed"}, status=500)



# chaetting 페이지 로딩
@login_required
def chaetting_view(request):
    posts = Post.objects.annotate(
        comment_count=Count("comments", distinct=True)
        + Count("comments__replies", distinct=True)
    ).order_by('-created_at')  # 최신 순으로 정렬하여 게시물을 가져옴

    print("불러온 게시물:", posts)  # 추가된 디버깅 출력

    popular_posts = Post.objects.order_by("-created_at")[:5]  # 최신 5개 인기글

    context = {
        "posts": posts,  # posts를 템플릿으로 전달
        "popular_posts": popular_posts,
        "GENRES": GENRES,  # GENRES 전달
    }
    return render(request, "chaetting.html", context)




# 포스트 생성
@login_required
def create_post(request):
    if request.method == "POST":
        print(request.POST.get('genre'))  # 장르 값이 정상적으로 출력되는지 확인
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect("chaetting_view")
        else:
            print(form.errors)  # 서버 로그에서 오류를 확인
            messages.error(request, form.errors)  # 브라우저에서도 오류를 확인
            return redirect("chaetting_view")
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


#Track, userTrack db 저장
@login_required
@csrf_exempt
def save_selected_track(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            spotify_track_id = data.get('spotify_track_id')
            track_name = data.get('track')
            artist_name = data.get('artist')
            album_image_url = data.get('album_image_url')
            genre = data.get('genre')

            # 필수 필드 확인
            if not spotify_track_id:
                return JsonResponse({'status': 'error', 'message': 'Spotify track ID is required'}, status=400)
            if not track_name:
                return JsonResponse({'status': 'error', 'message': 'Track name is required'}, status=400)
            if not artist_name:
                return JsonResponse({'status': 'error', 'message': 'Artist name is required'}, status=400)
            if not genre:
                return JsonResponse({'status': 'error', 'message': 'Genre is required'}, status=400)

            # 동일한 spotify_track_id와 genre를 가진 트랙이 이미 있는지 확인
            existing_track = Track.objects.filter(spotify_track_id=spotify_track_id, genre=genre).first()

            if existing_track:
                # 동일한 트랙이 이미 있으면 selection_count를 증가시키고 저장
                existing_track.selection_count += 1
                existing_track.save()
                track = existing_track
            else:
                # 동일한 트랙이 없으면 새로 생성하고 selection_count를 1로 설정
                track = Track.objects.create(
                    spotify_track_id=spotify_track_id,
                    name=track_name,
                    artist=artist_name,
                    album_image_url=album_image_url,
                    genre=genre,
                    selection_count=1
                )

            # UserTrack에 데이터 저장
            UserTrack.objects.create(
                user=request.user,
                track=track
            )

            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
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


def generate_recommendations(user):
    # 유저의 관심 장르를 쉼표로 구분하여 리스트로 변환
    user_genres = user.genres.split(',')

    # 유저의 성별, 나이대 기반 추천곡 필터링
    gender_age_recommendations = Track.objects.filter(
        usertrack__user__gender=user.gender,
        usertrack__user__age_group=user.age_group
    ).order_by('-selection_count')[:5]

    # 유저의 관심 장르 중 2개 랜덤 선택
    selected_genres = random.sample(user_genres, 2)

    genre_recommendations = {}

    for genre in selected_genres:
        tracks = Track.objects.filter(genre=genre).order_by('-selection_count')[:5]
        genre_recommendations[genre] = list(tracks)

    # 중복된 트랙 제거 (spotify_track_id와 genre를 기준으로)
    seen = set()
    unique_gender_age_recommendations = []
    for track in gender_age_recommendations:
        identifier = (track.spotify_track_id, track.genre)
        if identifier not in seen:
            unique_gender_age_recommendations.append(track)
            seen.add(identifier)

    for genre in genre_recommendations:
        seen = set()
        unique_tracks = []
        for track in genre_recommendations[genre]:
            identifier = (track.spotify_track_id, track.genre)
            if identifier not in seen:
                unique_tracks.append(track)
                seen.add(identifier)
        genre_recommendations[genre] = unique_tracks

    return unique_gender_age_recommendations, genre_recommendations, selected_genres



def recommendation_view(request):
    user = request.user

    # 추천곡을 생성
    gender_age_recommendations, genre_recommendations, selected_genres = generate_recommendations(user)
    
    genre_1_tracks = genre_recommendations[selected_genres[0]]
    genre_2_tracks = genre_recommendations[selected_genres[1]]

    print(gender_age_recommendations)
    print(genre_1_tracks)
    print(genre_2_tracks)
    
    context = {
        'user': user,
        'gender_age_recommendations': gender_age_recommendations,
        'genre_1_tracks': genre_1_tracks,
        'genre_2_tracks': genre_2_tracks,
        'selected_genres': selected_genres,  # 선택된 장르 리스트를 템플릿에 전달
    }
    return render(request, 'chaetting.html', context)


@login_required
def recommendation_and_chaetting_view(request):
    # 추천 시스템 관련 데이터
    user = request.user
    gender_age_recommendations, genre_recommendations, selected_genres = generate_recommendations(user)
    genre_1_tracks = genre_recommendations[selected_genres[0]]
    genre_2_tracks = genre_recommendations[selected_genres[1]]

    # 게시물 관련 데이터
    posts = Post.objects.all().order_by('-created_at')
    
    # 좋아요 순으로 정렬된 인기 게시물 (예: 상위 5개)
    popular_posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')[:5]

    context = {
        'user': user,
        'gender_age_recommendations': gender_age_recommendations,
        'genre_1_tracks': genre_1_tracks,
        'genre_2_tracks': genre_2_tracks,
        'selected_genres': selected_genres,
        'posts': posts,
        'popular_posts': popular_posts,
        'GENRES': GENRES,
    }
    return render(request, 'chaetting.html', context)



@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == "POST":
        post.delete()
        messages.success(request, "글이 삭제되었습니다.")
        return redirect('mypage')

    return render(request, 'confirm_delete.html', {'post': post})



@csrf_exempt
@login_required
def save_file_upload_genre(request):
    if request.method == 'POST':
        try:
            if 'mp3_file' in request.FILES:
                # MP3 파일 처리
                mp3_file = request.FILES['mp3_file']
                file_upload = FileUpload.objects.create(
                    user=request.user,
                    mp3_file=mp3_file,
                    song_name=mp3_file.name
                )

            elif 'youtube_url' in request.POST:
                # YouTube 링크 처리
                youtube_url = request.POST.get('youtube_url')
                if not youtube_url:
                    return JsonResponse({'status': 'error', 'message': '유튜브 링크가 필요합니다.'}, status=400)

                file_upload = FileUpload.objects.create(
                    user=request.user,
                    youtube_url=youtube_url,
                    song_name="YouTube Track"  # 실제로는 YouTube에서 제목을 가져오는 로직을 추가 가능
                )

            else:
                return JsonResponse({'status': 'error', 'message': '파일 또는 유튜브 링크가 필요합니다.'}, status=400)

            # 세션에 file_upload_id 저장
            request.session['file_upload_id'] = file_upload.id

            return JsonResponse({'status': 'success', 'file_upload_id': file_upload.id}, status=200)

        except Exception as e:
            # 오류 메시지 및 상세 내용 출력
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()  # 자세한 스택 트레이스 출력
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    

@login_required
def download_pdf(request):
    file_upload_id = request.session.get('file_upload_id')
    if not file_upload_id:
        raise Http404("File upload ID not found in session.")

    file_upload = get_object_or_404(FileUpload, id=file_upload_id, user=request.user)
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, file_upload.pdf_file.name)

    if not os.path.exists(pdf_file_path):
        raise Http404("PDF file not found.")

    response = FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_upload.song_name}.pdf"'
    return response
