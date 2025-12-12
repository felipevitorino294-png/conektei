from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Profile
from .forms import ProfileForm

def home(request):
    # 1. Busca apenas quem é Especialista E já definiu um preço
    specialists = Profile.objects.filter(is_specialist=True).exclude(price__isnull=True)
    
    # 2. Lógica da Barra de Busca
    query = request.GET.get('q')
    if query:
        # Filtra se o termo digitado aparece no Nome, Profissão OU Descrição
        specialists = specialists.filter(
            Q(user__first_name__icontains=query) | 
            Q(profession__icontains=query) |
            Q(description__icontains=query)
        )
    
    return render(request, 'home.html', {'specialists': specialists})

def specialist_detail_view(request, id):
    # Busca o perfil pelo ID. Se não achar, mostra erro 404.
    specialist = get_object_or_404(Profile, id=id)
    return render(request, 'specialist_detail.html', {'spec': specialist})

def login_view(request):
    if request.method == 'POST':
        # --- LÓGICA DE CADASTRO ---
        if 'confirm_password' in request.POST:
            nome = request.POST.get('name')
            email = request.POST.get('email')
            senha = request.POST.get('password')
            confirmar_senha = request.POST.get('confirm_password')
            tipo_usuario = request.POST.get('user_type') 

            # Validações
            if senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem!')
                return render(request, 'login.html')
            
            if User.objects.filter(username=email).exists():
                messages.error(request, 'Este email já está cadastrado!')
                return render(request, 'login.html')

            # Criar Usuário
            try:
                user = User.objects.create_user(username=email, email=email, password=senha)
                user.first_name = nome
                user.save()

                # Adicionar ao Grupo
                nome_grupo = 'Clientes' if tipo_usuario == 'client' else 'Especialistas'
                grupo, created = Group.objects.get_or_create(name=nome_grupo)
                user.groups.add(grupo)

                # Criar Perfil Automaticamente
                is_spec = (tipo_usuario == 'specialist')
                Profile.objects.create(user=user, is_specialist=is_spec)

                # Logar e Redirecionar
                auth_login(request, user)
                messages.success(request, f'Bem-vindo, {nome}!')
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, 'Erro ao criar conta. Tente novamente.')
                print(f"Erro no cadastro: {e}") 
                return render(request, 'login.html')

        # --- LÓGICA DE LOGIN ---
        else:
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
    # Verifica se o usuário pertence ao grupo de Especialistas
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
        messages.success(request, 'Sua conta foi excluída com sucesso.')
        return redirect('home')
    return redirect('dashboard')

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

    # 3. NOVO: Lógica dos Botões de Categoria
    category = request.GET.get('category')
    if category and category != 'all':
        specialists = specialists.filter(profession=category)
    
    return render(request, 'home.html', {'specialists': specialists})