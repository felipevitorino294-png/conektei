from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Páginas Principais
    path('', views.home, name='home'),
    path('specialist/<int:id>/', views.specialist_detail_view, name='specialist_detail'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Autenticação e Perfil
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/delete/', views.delete_account_view, name='delete_account'),

    # Agenda (Criação e Agendamento)
    path('appointment/create/', views.create_appointment_view, name='create_appointment'),
    path('appointment/delete/<int:appointment_id>/', views.delete_appointment_view, name='delete_appointment'),
    path('appointment/book/<int:appointment_id>/', views.book_appointment_view, name='book_appointment'),

    # Pagamentos e Planos (ATUALIZADO)
    path('plans/', views.plans_selection_view, name='plans_selection'),
    path('checkout/<str:plan_type>/<str:price>/', views.checkout_view, name='checkout'),
    path('payment/process/', views.process_payment_view, name='process_payment'),
]

# Configuração para servir imagens (Media) no modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)