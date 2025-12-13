from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Profile
from .forms import ProfileForm
import time

def home(request):
    # 1. Busca todos os especialistas válidos
    specialists = Profile.objects.filter(is_specialist=True).exclude(price__isnull=True)
    
    # 2. Lógica da Barra de Busca (Texto)
    query = request.GET.get('q')
    if query:
        specialists = specialists.filter(
            Q(user__first_name__icontains=query) | 
            Q(profession__icontains=query) |
            Q(description__icontains=query)
        )

    # 3. Lógica dos Botões de Categoria
    category = request.GET.get('category')
    if category and category != 'all':
        specialists = specialists.filter(profession=category)
    
    return render(request, 'home.html', {'specialists': specialists})

def specialist_detail_view(request, id):
    specialist = get_object_or_404(Profile, id=id)
    return render(request, 'specialist_detail.html', {'spec': specialist})

def login_view(request):
    if request.method == 'POST':
        if 'confirm_password' in request.POST:
            # --- CADASTRO ---
            nome = request.POST.get('name')
            email = request.POST.get('email')
            senha = request.POST.get('password')
            confirmar_senha = request.POST.get('confirm_password')
            tipo_usuario = request.POST.get('user_type') 

            if senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem!')
                return render(request, 'login.html')
            
            if User.objects.filter(username=email).exists():
                messages.error(request, 'Este email já está cadastrado!')
                return render(request, 'login.html')

            try:
                user = User.objects.create_user(username=email, email=email, password=senha)
                user.first_name = nome
                user.save()

                nome_grupo = 'Clientes' if tipo_usuario == 'client' else 'Especialistas'
                grupo, created = Group.objects.get_or_create(name=nome_grupo)
                user.groups.add(grupo)

                is_spec = (tipo_usuario == 'specialist')
                Profile.objects.create(user=user, is_specialist=is_spec)

                auth_login(request, user)
                messages.success(request, f'Bem-vindo, {nome}!')
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, 'Erro ao criar conta.')
                print(f"Erro: {e}") 
                return render(request, 'login.html')

        else:
            # --- LOGIN ---
            email = request.POST.get('email')
            senha = request.POST.get('password')
            user = authenticate(request, username=email, password=senha)

            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Email ou senha incorretos!')
                return render(request, 'login.html')

    return render(request, 'login.html')

@login_required
def dashboard_view(request):
    is_specialist = request.user.groups.filter(name='Especialistas').exists()
    if is_specialist:
        return render(request, 'dashboard_specialist.html')
    else:
        return render(request, 'dashboard_client.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

@login_required
def edit_profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete() 
        messages.success(request, 'Sua conta foi excluída.')
        return redirect('home')
    return redirect('dashboard')

@login_required
def choose_access_view(request, choice):
    if choice not in ['assinatura', 'avulso', 'nenhum']:
        messages.error(request, "Escolha inválida.")
        return redirect('dashboard')
    
    profile = request.user.profile
    profile.access_type = choice
    
    if choice == 'assinatura':
        profile.has_active_plan = True
    else:
        profile.has_active_plan = False
        
    profile.save()
    messages.success(request, f'Acesso atualizado para: {profile.get_access_type_display()}')
    return redirect('dashboard')

# --- NOVAS FUNÇÕES DE CHECKOUT ---

@login_required
def plans_selection_view(request):
    return render(request, 'subscription_plans.html')

@login_required
def checkout_view(request, plan_type, price):
    context = {
        'plan_type': plan_type,
        'price': price
    }
    return render(request, 'checkout.html', context)

@login_required
def process_payment_view(request):
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        
        # Ativa o usuário como assinante
        profile = request.user.profile
        profile.access_type = 'assinatura'
        profile.has_active_plan = True
        profile.save()
        
        messages.success(request, f'Pagamento aprovado! Plano {plan_type} ativado com sucesso.')
        return redirect('dashboard')
    
    return redirect('home')

# Mantida para compatibilidade (botões antigos)
@login_required
def subscribe_plan_view(request, plan_type):
    profile = request.user.profile
    profile.has_active_plan = True
    profile.access_type = 'assinatura'
    profile.save()
    messages.success(request, f'Plano {plan_type} ativado.')
    return redirect('home')