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

# --- HOME (Com Busca e Filtros Otimizados) ---
def home(request):
    # 1. Pega apenas quem é especialista e tem preço definido (perfil completo)
    specialists = Profile.objects.filter(is_specialist=True).exclude(price__isnull=True)
    
    # 2. Lógica de Busca (Barra de Pesquisa)
    query = request.GET.get('q')
    if query:
        specialists = specialists.filter(
            Q(user__first_name__icontains=query) | 
            Q(profession__icontains=query) |
            Q(description__icontains=query)
        )

    # 3. Filtro por Categoria (Botões da Home)
    category = request.GET.get('category')
    if category and category != 'all':
        specialists = specialists.filter(profession=category)
    
    # 4. Lista de Profissões para o Menu
    all_professions = [
        'Tecnologia e TI', 'Saúde e Bem-estar', 'Consultoria Jurídica',
        'Consultoria Financeira', 'Marketing Digital', 'Coaching Profissional',
        'Educação', 'Engenharia', 'Arquitetura e Design', 'Psicologia'
    ]
    
    return render(request, 'home.html', {
        'specialists': specialists,
        'all_professions': all_professions
    })

# --- DETALHES (Página de Ver Perfil) ---
def specialist_detail_view(request, id):
    specialist = get_object_or_404(Profile, id=id)
    
    if not specialist.is_specialist:
        return redirect('home')

    # Mostra apenas horários futuros
    appointments = Appointment.objects.filter(
        specialist=specialist, 
        date__gte=date.today()
    ).order_by('date', 'time')

    return render(request, 'specialist_detail.html', {
        'spec': specialist,
        'appointments': appointments
    })

# --- DASHBOARD (CORRIGIDO E COMPLETO) ---
@login_required
def dashboard_view(request):
    profile = get_profile(request.user)
    
    # Contexto Base (Enviamos 'profile' para corrigir o erro de link)
    context = {
        'user': request.user,
        'profile': profile,  # <--- CORREÇÃO IMPORTANTE AQUI
        'is_specialist': profile.is_specialist,
    }

    if profile.is_specialist:
        # Painel do Especialista: Vê horários que ele criou
        appointments = Appointment.objects.filter(
            specialist=profile,
            date__gte=date.today()
        ).order_by('date', 'time')
        
        context['appointments'] = appointments
        return render(request, 'dashboard.html', context)
    
    else:
        # Painel do Cliente: Vê agendamentos que ELE MARCOU
        my_appointments = Appointment.objects.filter(
            client=request.user,
            date__gte=date.today()
        ).order_by('date', 'time')
        
        # Sugestão de especialistas
        specialists = Profile.objects.filter(is_specialist=True).exclude(price__isnull=True)
        
        context['appointments'] = my_appointments
        context['specialists'] = specialists
        
        return render(request, 'dashboard.html', context)

# --- AGENDAMENTO (Cliente reserva horário) ---
@login_required
def book_appointment_view(request, appointment_id):
    profile = get_profile(request.user)
    
    # Validações
    if profile.is_specialist:
        messages.error(request, 'Especialistas não podem agendar consultas.')
        return redirect('dashboard')

    # Validação de Plano (Opcional - descomente se quiser ativar)
    # if not profile.has_active_plan:
    #     messages.error(request, 'Você precisa de um plano ativo para agendar.')
    #     return redirect('plans_selection')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.is_booked:
        messages.error(request, 'Horário já reservado por outra pessoa.')
    else:
        appointment.is_booked = True
        appointment.client = request.user
        appointment.save()
        messages.success(request, 'Agendamento confirmado com sucesso!')
    
    return redirect('dashboard')

# --- GERENCIAMENTO DE AGENDA (Especialista cria/deleta horários) ---
@login_required
def create_appointment_view(request):
    profile = get_profile(request.user)
    if not profile.is_specialist:
        return redirect('dashboard')

    if request.method == 'POST':
        date_appt = request.POST.get('date')
        time_appt = request.POST.get('time')
        
        # Evita duplicidade
        if not Appointment.objects.filter(specialist=profile, date=date_appt, time=time_appt).exists():
            Appointment.objects.create(
                specialist=profile,
                date=date_appt,
                time=time_appt
            )
            messages.success(request, 'Horário liberado na agenda!')
        else:
            messages.error(request, 'Você já tem um horário liberado nesta data e hora.')
            
    return redirect('dashboard')

@login_required
def delete_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Garante que só o dono do horário pode deletar
    if appointment.specialist.user == request.user:
        appointment.delete()
        messages.success(request, 'Horário removido da agenda.')
    return redirect('dashboard')

# --- LOGIN / CADASTRO / LOGOUT ---
def login_view(request):
    if request.method == 'POST':
        # CADASTRO
        if 'confirm_password' in request.POST:
            try:
                if request.POST.get('password') != request.POST.get('confirm_password'):
                    messages.error(request, 'As senhas não coincidem.')
                    return render(request, 'login.html')

                if User.objects.filter(email=request.POST.get('email')).exists():
                    messages.error(request, 'Este email já está cadastrado.')
                    return render(request, 'login.html')

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
                messages.success(request, 'Conta criada com sucesso!')
                
                if is_spec:
                    return redirect('edit_profile')
                else:
                    return redirect('home')

            except Exception as e:
                messages.error(request, 'Erro ao criar conta. Tente novamente.')
                print(e)
                return render(request, 'login.html')
        
        # LOGIN
        else:
            user = authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
            if user:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Email ou senha incorretos.')
                
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

# --- EDITAR PERFIL ---
@login_required
def edit_profile_view(request):
    profile = get_profile(request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado!')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        auth_logout(request)
        user.delete()
        messages.success(request, 'Sua conta foi excluída.')
        return redirect('home')
    return redirect('dashboard')

# --- PAGAMENTOS E PLANOS ---
@login_required
def plans_selection_view(request):
    # Aponta para o arquivo correto criado anteriormente
    return render(request, 'plans_selection.html')

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
        messages.success(request, 'Pagamento aprovado! Agora você pode agendar consultas.')
        return redirect('dashboard')
    return redirect('home')