from django.contrib import admin
from django.urls import path
from core import views  # <--- 1. Adicione essa importação

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 2. Adicione essa linha para a página inicial
    # '' (vazio) significa: quando entrar no site sem digitar nada depois da barra
    # views.home significa: use a função 'home' que está dentro do arquivo views.py do core
    path('', views.home, name='home'), 
]