# blogicum/templatetags/custom_bootstrap.py
from django import template
from django.template import Library

register = Library()

try:
    # Пробуем импортировать оригинальные теги
    from django_bootstrap5.templatetags import django_bootstrap5 as bootstrap_tags
    register = bootstrap_tags.register
except ImportError:
    # Если не установлено, создаем заглушки
    @register.simple_tag
    def bootstrap_css():
        return ''
    
    @register.simple_tag  
    def bootstrap_javascript():
        return ''
    
    @register.simple_tag
    def bootstrap_form(*args, **kwargs):
        return ''