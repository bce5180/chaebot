from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from django.http import JsonResponse
from .models import Post, CustomUser, Comment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from .constants import GENRES
from django.contrib.auth.decorators import login_required


# Home view
def index(request):
    return render(request, "index.html")


# PDF result view
def result(request):
    return render(request, "result.html")


# Waiting view
def waiting(request):
    return render(request, "waiting.html")


# Logout view
def logout_view(request):
    logout(request)
    return redirect("index")


# Show signup view
def show_signup(request):
    return render(request, "signup.html")


# Login view
def login_view(request):
    form = AuthenticationForm()
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        password = request.POST.get("password")
        try:
            user = CustomUser.objects.get(user_id=user_id)
            if user.check_password(password):
                auth_login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                request.session["user_id"] = user.id
                return redirect("index")
            else:
                messages.error(request, "비밀번호가 틀렸습니다.")
        except CustomUser.DoesNotExist:
            messages.error(request, "회원정보가 없습니다!")
    return render(request, "login.html", {"form": form})


# Signup view
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user_id = request.POST.get("id")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")

        if password != password2:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        if CustomUser.objects.filter(user_id=user_id).exists():
            return render(request, "signup.html", {"error": "User ID already exists"})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email already exists"})

        user = CustomUser.objects.create_user(
            username=username, password=password, email=email, user_id=user_id
        )
        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        request.session["user_id"] = user.id
        return redirect("age_gender")

    return render(request, "signup.html")


# Chaetting view
def chaetting(request):
    posts = Post.objects.all()
    popular_posts = Post.objects.order_by("-likes")[:5]
    return render(
        request,
        "chaetting.html",
        {"posts": posts, "popular_posts": popular_posts, "GENRES": GENRES},
    )


# Age and gender view
def age_gender(request):
    if request.method == "POST":
        age_group = request.POST.get("age_group")
        gender = request.POST.get("gender")

        user_id = request.session.get("user_id")

        if user_id:
            user = CustomUser.objects.get(id=user_id)
            user.age_group = age_group
            user.gender = gender
            user.save()

            return redirect("select_genres")
        else:
            return redirect("signup")

    return render(request, "age_gender.html")


# Select genres view
def select_genres(request):
    if request.method == "POST":
        selected_genres = request.POST.get("selected_genres", "").split(",")
        user_id = request.session.get("user_id")

        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                user.genres = ",".join(selected_genres)
                user.save()
                del request.session["user_id"]
                return redirect("login")
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist.")
                return redirect("login")
        else:
            return redirect("signup")
    return render(request, "select_genres.html", {"genres": GENRES})


# MP3 upload view
@csrf_exempt
def upload_mp3(request):
    if request.method == "POST" and request.FILES.get("file"):
        mp3_file = request.FILES["file"]
        file_upload = FileUpload(mp3_file=mp3_file)
        file_upload.save()
        return render(request, "waiting.html")
    return JsonResponse({"error": "Invalid request"}, status=400)


# Create post view
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("chaetting")
    return redirect("chaetting")


# Like post view
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    popular_posts = Post.objects.order_by("-likes")[:5]
    context = {
        "post": post,
        "popular_posts": popular_posts,
    }
    return render(request, "post_detail.html", context)


def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        parent_comment_id = request.POST.get("parent_comment_id")
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            # 대댓글 처리
            if parent_comment_id:
                parent_comment = get_object_or_404(Comment, id=parent_comment_id)
                comment.parent = parent_comment
            comment.save()
            return redirect("post_detail", post_id=post.id)
    return redirect("post_detail", post_id=post.id)


def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return JsonResponse(
        {"liked": request.user in post.likes.all(), "total_likes": post.likes.count()}
    )


def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return JsonResponse(
        {
            "liked": request.user in comment.likes.all(),
            "total_likes": comment.likes.count(),
        }
    )
