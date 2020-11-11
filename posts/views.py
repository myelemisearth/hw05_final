from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import  get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_post_list = group.posts.all()
    paginator = Paginator(group_post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {'page': page,'paginator': paginator, 'author': author})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    return render(
        request,
        'post.html',
        {'post': post, 'author': post.author})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post, author=User.objects.get(username=username),
        id=post_id)
    if request.user != post.author:
        return redirect('post', username=post.author, post_id=post.id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if not form.is_valid():
        return render(
            request,
            'new.html',
            {'form': form, 'post': post})
    form.save()
    return redirect('post', username=post.author, post_id=post.id)
