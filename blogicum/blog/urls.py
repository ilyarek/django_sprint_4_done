from django.urls import path
from . import views

app_name = 'blog'  # пространство имен

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('posts/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'), 
    path('profile/<str:username>/', views.profile, name='profile'),
    path('registration/', views.registration, name='registration'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
    path('test-email/', views.test_email, name='test_email'),
    
    # Комментарии
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]