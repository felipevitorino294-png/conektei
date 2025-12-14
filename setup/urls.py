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
    
    # Rotas de Especialista
    path('specialist/<int:id>/', views.specialist_detail_view, name='specialist_detail'),
    
    # --- ROTAS DE AGENDAMENTO (CLIENTE) ---
    # Essa rota recebe o ID do horário (Appointment) e faz a reserva
    path('appointment/book/<int:appointment_id>/', views.book_appointment_view, name='book_appointment'),

    # --- ROTAS DE GERENCIAMENTO DE AGENDA (ESPECIALISTA) ---
    path('appointment/create/', views.create_appointment_view, name='create_appointment'),
    path('appointment/delete/<int:appointment_id>/', views.delete_appointment_view, name='delete_appointment'),

    # --- ROTAS DE PAGAMENTO E PLANOS ---
    path('access/choose/<str:choice>/', views.choose_access_view, name='choose_access'),
    path('plans/selection/', views.plans_selection_view, name='plans_selection'),
    
    # Rota do Checkout (Essa é a correta! Leva para a tela de pagamento)
    path('checkout/<str:plan_type>/<str:price>/', views.checkout_view, name='checkout'),
    
    # Processamento do Pagamento
    path('payment/process/', views.process_payment_view, name='process_payment'),
    
    # --- ROTA REMOVIDA PARA EVITAR ATIVAÇÃO DIRETA/GRÁTIS ---
    # path('plan/subscribe/<str:plan_type>/', views.subscribe_plan_view, name='subscribe_plan'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)