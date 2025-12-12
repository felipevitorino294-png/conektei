from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Lista de Opções (O primeiro valor é o que salva no banco, o segundo é o que aparece na tela)
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
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # --- NOVO: Limpeza do Telefone para o WhatsApp ---
    def clean_phone(self):
        """Retorna o telefone apenas com números para o link do WhatsApp"""
        if self.phone:
            return self.phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        return ''
    # -------------------------------------------------

    def __str__(self):
        return f"Perfil de {self.user.username}"