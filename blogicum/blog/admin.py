from django.contrib import admin
from .models import Category, Location, Post, Comment

admin.site.site_header = 'Администрирование Блогикума'
admin.site.index_title = 'Управление контентом'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'author', 
        'created_at', 
        'has_image'
    )
    list_filter = (
        'author',
        'created_at',
    )
    search_fields = (
        'title',
        'content',
        'author__username',
    )
    date_hierarchy = 'created_at'
    
    def has_image(self, obj):
        """Отображает есть ли у поста изображение"""
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Есть изображение'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'text_preview')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username', 'post__title')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'