from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Profile, Appointment
from .forms import ProfileForm
from datetime import date

# --- AUXILIAR ---
def get_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile

# --- HOME ---
def home(request):
    specialists = Profile.objects.filter(is_specialist=True).exclude(price__isnull=True)
    
    query = request.GET.get('q')
    if query:
        specialists = specialists.filter(
            Q(user__first_name__icontains=query) | 
            Q(profession__icontains=query) |
            Q(description__icontains=query)
        )

    category = request.GET.get('category')
    if category and category != 'all':
        specialists = specialists.filter(profession=category)
    
    return render(request, 'home.html', {'specialists': specialists})

# --- DETALHES (Página de Ver Perfil) ---
def specialist_detail_view(request, id):
    specialist = get_object_or_404(Profile, id=id)
    
    if not specialist.is_specialist:
        return redirect('home')

    appointments = Appointment.objects.filter(
        specialist=specialist, 
        date__gte=date.today()
    ).order_by('date', 'time')

    return render(request, 'specialist_detail.html', {
        'spec': specialist,
        'appointments': appointments
    })

# --- DASHBOARD ---
@login_required
def dashboard_view(request):
    profile = get_profile(request.user)
    
    if profile.is_specialist:
        # Painel do Especialista
        appointments = Appointment.objects.filter(
            specialist=profile,
            date__gte=date.today()
        ).order_by('date', 'time')
        return render(request, 'dashboard_specialist.html', {'appointments': appointments})
    else:
        # Painel do Cliente
        specialists = Profile.objects.filter(is_specialist=True).exclude(price__isnull=True)
        return render(request, 'dashboard_client.html', {'specialists': specialists})

# --- AGENDAMENTO ---
@login_required
def book_appointment_view(request, appointment_id):
    profile = get_profile(request.user)
    
    if profile.is_specialist:
        messages.error(request, 'Especialistas não podem agendar consultas.')
        return redirect('dashboard')

    if not profile.has_active_plan:
        messages.error(request, 'Você precisa de um plano ativo para agendar.')
        return redirect('plans_selection')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.is_booked:
        messages.error(request, 'Horário já reservado.')
    else:
        appointment.is_booked = True
        appointment.client = request.user
        appointment.save()
        messages.success(request, 'Agendamento confirmado!')
    
    return redirect('specialist_detail', id=appointment.specialist.id)

# --- GERENCIAMENTO DE AGENDA ---
@login_required
def create_appointment_view(request):
    profile = get_profile(request.user)
    if not profile.is_specialist:
        return redirect('dashboard')

    if request.method == 'POST':
        Appointment.objects.create(
            specialist=profile,
            date=request.POST.get('date'),
            time=request.POST.get('time')
        )
        messages.success(request, 'Horário criado!')
    return redirect('dashboard')

@login_required
def delete_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.specialist.user == request.user:
        appointment.delete()
        messages.success(request, 'Horário removido.')
    return redirect('dashboard')

# --- LOGIN / CADASTRO (A Lógica Nova Está Aqui) ---
def login_view(request):
    if request.method == 'POST':
        if 'confirm_password' in request.POST:
            # --- CADASTRO ---
            try:
                user = User.objects.create_user(
                    username=request.POST.get('email'), 
                    email=request.POST.get('email'), 
                    password=request.POST.get('password')
                )
                user.first_name = request.POST.get('name')
                user.save()

                tipo = request.POST.get('user_type')
                is_spec = (tipo == 'specialist')
                
                Profile.objects.create(user=user, is_specialist=is_spec)
                grupo, _ = Group.objects.get_or_create(name='Especialistas' if is_spec else 'Clientes')
                user.groups.add(grupo)

                auth_login(request, user)

                if is_spec:
                    return redirect('edit_profile') # Cadastro novo -> Edita Perfil
                else:
                    return redirect('home')

            except Exception:
                messages.error(request, 'Erro no cadastro.')
                return render(request, 'login.html')
        else:
            # --- LOGIN ---
            user = authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
            if user:
                auth_login(request, user)
                
                # VERIFICA O TIPO E REDIRECIONA
                profile = get_profile(user)
                if profile.is_specialist:
                    return redirect('dashboard') # Especialista -> Painel
                else:
                    return redirect('home') # Cliente -> Home
            else:
                messages.error(request, 'Dados incorretos.')
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

@login_required
def edit_profile_view(request):
    profile = get_profile(request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return redirect('dashboard')

@login_required
def plans_selection_view(request):
    return render(request, 'subscription_plans.html')

@login_required
def checkout_view(request, plan_type, price):
    return render(request, 'checkout.html', {'plan_type': plan_type, 'price': price})

@login_required
def process_payment_view(request):
    if request.method == 'POST':
        profile = get_profile(request.user)
        profile.has_active_plan = True
        profile.access_type = 'assinatura'
        profile.save()
        messages.success(request, 'Pagamento aprovado!')
        return redirect('dashboard')
    return redirect('home')

@login_required
def choose_access_view(request, choice):
    profile = get_profile(request.user)
    profile.access_type = choice
    profile.has_active_plan = (choice == 'assinatura')
    profile.save()
    return redirect('dashboard')