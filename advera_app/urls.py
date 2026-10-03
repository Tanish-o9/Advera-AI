from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate, name='generate'),
    path('page/<int:page_id>/', views.page_detail, name='page_detail'),
    path('history/', views.history, name='history'),
    path('delete/<int:page_id>/', views.delete_page, name='delete_page'),
]