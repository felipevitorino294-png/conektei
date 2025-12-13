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
    
    # Rotas de Especialista e Planos
    path('specialist/<int:id>/', views.specialist_detail_view, name='specialist_detail'),
    path('plan/subscribe/<str:plan_type>/', views.subscribe_plan_view, name='subscribe_plan'),

    # --- NOVA ROTA: Escolha de Acesso (Assinante vs Avulso) ---
    path('access/choose/<str:choice>/', views.choose_access_view, name='choose_access'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)