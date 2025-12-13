from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Lista de Profissões
    PROFISSOES_CHOICES = [
        ('Tecnologia e TI', 'Tecnologia e TI'),
        ('Consultoria Jurídica', 'Consultoria Jurídica'),
        ('Consultoria Financeira', 'Consultoria Financeira'),
        ('Saúde e Bem-estar', 'Saúde e Bem-estar'),
        ('Marketing Digital', 'Marketing Digital'),
        ('Coaching Profissional', 'Coaching Profissional'),
        ('Design e Criatividade', 'Design e Criatividade'),
        ('Engenharia e Arquitetura', 'Engenharia e Arquitetura'),
        ('Outros', 'Outros'),
    ]

    # --- NOVO: Opções de Tipo de Acesso ---
    ACCESS_CHOICES = [
        ('nenhum', 'Não definido'),
        ('assinatura', 'Assinante (Plano Mensal)'),
        ('avulso', 'Pagamento Avulso (Por Consulta)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_specialist = models.BooleanField(default=False)
    
    profession = models.CharField(
        max_length=100, 
        choices=PROFISSOES_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Área de Atuação"
    )
    
    description = models.TextField(blank=True, null=True, verbose_name="Sobre mim")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Preço da Consulta")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp")
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Foto de Perfil")

    # --- Controle de Pagamento / Acesso ---
    # Mantivemos o has_active_plan para compatibilidade, mas o access_type é o principal agora
    has_active_plan = models.BooleanField(default=False, verbose_name="Tem Plano Ativo?")
    
    access_type = models.CharField(
        max_length=20, 
        choices=ACCESS_CHOICES, 
        default='nenhum',
        verbose_name="Tipo de Acesso"
    )

    # --- Limpeza do Telefone para o WhatsApp ---
    def clean_phone(self):
        """Retorna o telefone apenas com números para o link do WhatsApp"""
        if self.phone:
            return self.phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        return ''

    def __str__(self):
        return f"Perfil de {self.user.username}"