from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    # Rotas do Perfil
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('account/delete/', views.delete_account_view, name='delete_account'),
    
    # NOVA ROTA: Detalhes do Especialista (O <int:id> pega o ID do banco)
    path('specialist/<int:id>/', views.specialist_detail_view, name='specialist_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)