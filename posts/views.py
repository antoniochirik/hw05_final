import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "posts/index.html",
        {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "page": page,
        "paginator": paginator
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, "posts/new_post.html", {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")


@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, "posts/comments.html",
                      {"form": form, "post": post})
    comment = form.instance
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(
        Post,
        id=post_id,
        author=user
    )
    if request.user != post.author:
        return redirect("post", username=username, post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        context = {
            "form": form,
            "post": post
        }
        return render(request, "posts/new_post.html", context)
    form.save()
    return redirect("post", username=username, post_id=post_id)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = (request.user.is_authenticated and
                 request.user != author and
                 Follow.objects.filter(user=request.user,
                                       author=author).exists())
    context = {
        "author": author,
        "page": page,
        "paginator": paginator,
        "following": following
    }
    return render(request, "posts/profile.html", context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = Post.objects.get(author=author, id=post_id)
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    is_post = True
    context = {
        "author": author,
        "post": post,
        "comments": comments,
        "form": form,
        "is_post": is_post
    }
    return render(request, "posts/post.html", context)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "posts/follow.html",
        {"page": page, "paginator": paginator}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and not Follow.objects.filter(user=request.user,
                                                            author=author).exists():
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following_post = Follow.objects.filter(user=request.user, author=author)
    if following_post.exists():
        following_post.delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)