import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.conf import settings

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, settings.PER_PAGE)
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
    paginator = Paginator(post_list, settings.PER_PAGE)
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
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, "posts/includes/comments.html",
                      {"form": form, "post": post})
    comment = form.instance
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username
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
    paginator = Paginator(posts, settings.PER_PAGE)
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
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username
    )
    comments = post.comments.all()
    form = CommentForm()
    is_post = True
    context = {
        "author": post.author,
        "post": post,
        "comments": comments,
        "form": form,
        "is_post": is_post
    }
    return render(request, "posts/post.html", context)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "posts/follow.html",
        {"page": page, "paginator": paginator}
    )


@login_required
def profile_follow(request, username, post_id=None):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user, 
            author=author 
        )
    if post_id == None:
        return redirect("profile", username)
    else:
        return redirect("post", username, post_id)


@login_required
def profile_unfollow(request, username, post_id=None):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    if post_id != None:
        return redirect("post", username, post_id)
    else:
        return redirect("profile", username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
