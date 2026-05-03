from django.contrib import admin
from .models import HomeHeroSlide

@admin.register(HomeHeroSlide)
class HomeHeroSlideAdmin(admin.ModelAdmin):
    list_display = ['etiqueta', 'titulo_principal', 'titulo_resaltado', 'tipo_archivo', 'orden', 'activo']
    list_editable = ['orden', 'activo']
    search_fields = ['titulo_principal', 'etiqueta', 'descripcion']
    list_filter = ['activo', 'tipo_archivo']
    
    fieldsets = (
        ('Textos', {
            'fields': ('etiqueta', 'titulo_principal', 'titulo_resaltado', 'descripcion')
        }),
        ('Multimedia', {
            'fields': ('tipo_archivo', 'archivo', 'poster_video', 'texto_alt')
        }),
        ('Configuración', {
            'fields': ('orden', 'activo', 'intervalo_ms')
        }),
    )
