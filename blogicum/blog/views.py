from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.core.paginator import Paginator
from .models import Post
from django.contrib import messages
from .forms import PostForm, CommentForm
from .models import Post, Comment, Category
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

def index(request):
    posts = Post.objects.select_related(
        'author', 'category', 'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')[:5]
    return render(request, 'blog/index.html', {'post_list': posts})


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        pk=post_id,
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    """Отображение постов определенной категории"""
    category = get_object_or_404(Category, slug=category_slug)
    posts_list = Post.objects.filter(
        category=category
    ).select_related('author', 'category').order_by('-created_at')
    
    paginator = Paginator(posts_list, 10)  # 10 постов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category_posts.html', context)

def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration_form.html', {'form': form})

def csrf_failure(request, reason=""):
    return render(request, 'pages/403csrf.html', status=403)

def permission_denied(request, exception):
    return render(request, 'pages/403.html', status=403)

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

def server_error(request):
    return render(request, 'pages/500.html', status=500)

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    
    context = {
        'profile_user': user,
        'posts': posts,
    }
    return render(request, 'blog/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'blog/edit_profile.html', {'form': form})

def index(request):
    posts_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts_list, 10)  # 10 постов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/index.html', {'page_obj': page_obj})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(author=user).order_by('-created_at')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)

def index(request):
    """Главная страница со списком постов"""
    posts_list = Post.objects.select_related('author').all().order_by('-created_at')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/index.html', {'page_obj': page_obj})

def post_detail(request, pk):
    """Детальная страница поста"""
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def create_post(request):
    """Создание нового поста"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def edit_post(request, pk):
    """Редактирование поста"""
    post = get_object_or_404(Post, pk=pk)
    
    # Проверяем, что пользователь - автор поста
    if post.author != request.user:
        return redirect('blog:post_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'blog/create_post.html', context)

def post_detail(request, pk):
    """Детальная страница поста с комментариями"""
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    comments = post.comments.select_related('author').all()
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
def add_comment(request, pk):
    """Добавление комментария с уведомлением автора поста"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            
            send_mail(
                f'Новый комментарий к вашему посту "{post.title}"',
                f'Пользователь {request.user.username} оставил комментарий к вашему посту "{post.title}".\n\n'
                f'Комментарий: {comment.text}\n\n'
                f'Посмотреть: http://127.0.0.1:8000{post.get_absolute_url()}',
                settings.DEFAULT_FROM_EMAIL,
                [post.author.email],
                fail_silently=True, 
            )
            
            return redirect('blog:post_detail', pk=post.pk)
    
    return redirect('blog:post_detail', pk=post.pk)

@login_required
def edit_comment(request, pk, comment_id):
    """Редактирование комментария"""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=pk)
    
    if not comment.can_edit(request.user):
        return HttpResponseForbidden("Вы не можете редактировать этот комментарий")
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлен!')
            return redirect('blog:post_detail', pk=pk)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'post': comment.post,
        'is_edit': True,
    }
    return render(request, 'blog/comment_form.html', context)

@login_required
def delete_comment(request, pk, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=pk)
    
    if not comment.can_delete(request.user):
        return HttpResponseForbidden("Вы не можете удалить этот комментарий")
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('blog:post_detail', pk=pk)
    
    context = {
        'object': comment,
        'object_type': 'comment',
        'post': comment.post,
    }
    return render(request, 'blog/confirm_delete.html', context)

@login_required
def delete_post(request, pk):
    """Удаление поста"""
    post = get_object_or_404(Post, pk=pk)
    
    if not post.can_delete(request.user):
        return HttpResponseForbidden("Вы не можете удалить эту публикацию")
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация удалена!')
        return redirect('blog:index')
    
    context = {
        'object': post,
        'object_type': 'post',
    }
    return render(request, 'blog/confirm_delete.html', context)

@login_required
def test_email(request):
    """Тестовая функция для проверки отправки email"""
    
    # Проверяем существование папки
    emails_dir = settings.EMAIL_FILE_PATH
    if not os.path.exists(emails_dir):
        os.makedirs(emails_dir)
        message = f"✅ Папка {emails_dir} создана!<br>"
    else:
        message = f"✅ Папка {emails_dir} уже существует!<br>"
    
    # Подсчитываем существующие письма
    existing_emails = len([f for f in os.listdir(emails_dir) if f.endswith('.log') or f.endswith('.txt')])
    message += f"📊 Отправленных писем до теста: {existing_emails}<br><br>"
    
    try:
        # Отправляем тестовое письмо
        from django.core.mail import send_mail
        send_mail(
            'Тестовое письмо из Блогикума 🚀',
            f'''Привет, {request.user.username}!

Это тестовое письмо для проверки работы почтовой системы.

Детали отправки:
- Пользователь: {request.user.username}
- Время: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}
- Email бэкенд: {settings.EMAIL_BACKEND}
- Папка для писем: {settings.EMAIL_FILE_PATH}

Если вы читаете это письмо, значит система работает корректно! ✅

С уважением,
Блогикум''',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        
        message += "✅ Тестовое письмо успешно отправлено!<br>"
        
        new_emails = len([f for f in os.listdir(emails_dir) if f.endswith('.log') or f.endswith('.txt')])
        message += f"📊 Отправленных писем после теста: {new_emails}<br>"
        message += f"📨 Новых писем: {new_emails - existing_emails}<br><br>"
        
        # Показываем список файлов в папке
        email_files = sorted([f for f in os.listdir(emails_dir) if f.endswith('.log') or f.endswith('.txt')], reverse=True)[:5]
        message += "📁 Последние 5 писем:<br>"
        for file in email_files:
            file_path = os.path.join(emails_dir, file)
            file_size = os.path.getsize(file_path)
            message += f"&nbsp;&nbsp;• {file} ({file_size} bytes)<br>"
            
        message += f"<br>📍 Полный путь: {emails_dir}"
        
    except Exception as e:
        message += f"❌ Ошибка при отправке письма: {str(e)}<br>"
        message += f"📍 Путь: {emails_dir}"
    
    return HttpResponse(message)