from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        max_length=60,
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    image = models.ImageField(
        upload_to='posts/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Загрузите изображение для поста'
    )
    
    def comments_count(self):
        """Количество комментариев к посту"""
        return self.comments.count()
    
    def can_delete(self, user):
        """Может ли пользователь удалить пост"""
        return user.is_authenticated and user == self.author

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})
    
    def has_image(self):
        """Проверяет, есть ли у поста изображение"""
        return bool(self.image)
    

class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        max_length=1000
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']  # от старых к новым
    
    def __str__(self):
        return f'Комментарий {self.author} к {self.post}'
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post.pk})
    
    def can_edit(self, user):
        """Может ли пользователь редактировать комментарий"""
        return user.is_authenticated and user == self.author
    
    def can_delete(self, user):
        """Может ли пользователь удалить комментарий"""
        return user.is_authenticated and (user == self.author or user == self.post.author)