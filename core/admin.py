from django.contrib import admin
from .models import Profile, Appointment

# Registra o Perfil para poder editar/ver no admin
admin.site.register(Profile)

# Configuração avançada para a Agenda no Admin
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin): # <--- A CORREÇÃO ESTÁ AQUI (era admin.site.ModelAdmin)
    # O que aparece na lista
    list_display = ('specialist', 'date', 'time', 'is_booked', 'client')
    
    # Filtros laterais para facilitar a busca
    list_filter = ('is_booked', 'date', 'specialist')
    
    # Barra de busca
    search_fields = ('specialist__user__first_name', 'client__username')