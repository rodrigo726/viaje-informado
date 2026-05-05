from django.contrib import admin
from .models import CategoriaEvento, Evento, ImagenEvento

@admin.register(CategoriaEvento)
class CategoriaEventoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "tipo_icono", "icono_bootstrap", "activo", "creado"]
    search_fields = ["nombre", "descripcion", "icono_bootstrap"]
    list_filter = ["activo", "tipo_icono"]
    prepopulated_fields = {"slug": ("nombre",)}
    readonly_fields = ["creado", "actualizado"]
    ordering = ["nombre"]
    
    fieldsets = (
        ("Información principal", {
            "fields": ("nombre", "slug", "descripcion")
        }),
        ("Iconografía", {
            "fields": ("tipo_icono", "icono_bootstrap", "icono_archivo")
        }),
        ("Configuración", {
            "fields": ("activo", "creado", "actualizado")
        }),
    )


class ImagenEventoInline(admin.TabularInline):
    model = ImagenEvento
    extra = 0
    fields = ["imagen", "titulo", "texto_alt", "orden", "activo"]


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = [
        "nombre", "categoria_principal", "fecha_inicio", "fecha_fin", 
        "modalidad", "distrito", "tipo_costo", "rango_precios_soles", 
        "destacado", "activo"
    ]
    search_fields = [
        "nombre", "descripcion_corta", "descripcion", "organizador", 
        "lugar", "direccion", "referencia", "distrito__nombre_oficial", 
        "localidad__nombre", "categoria_principal__nombre", "categorias_secundarias__nombre"
    ]
    list_filter = [
        "activo", "destacado", "categoria_principal", "categorias_secundarias", 
        "tipo_costo", "modalidad", "fecha_inicio", 
        "distrito__provincia__departamento", "distrito__provincia", "distrito"
    ]
    prepopulated_fields = {"slug": ("nombre",)}
    autocomplete_fields = ["categoria_principal", "distrito", "localidad"]
    filter_horizontal = ["categorias_secundarias"]
    readonly_fields = ["creado", "actualizado"]
    ordering = ["-fecha_inicio", "nombre"]
    date_hierarchy = "fecha_inicio"
    inlines = [ImagenEventoInline]
    
    fieldsets = (
        ("Información principal", {
            "fields": (
                "categoria_principal", "categorias_secundarias", 
                "nombre", "slug", "descripcion_corta", "descripcion"
            )
        }),
        ("Fechas y horarios", {
            "fields": ("fecha_inicio", "fecha_fin", "hora_inicio", "hora_fin")
        }),
        ("Ubicación", {
            "fields": (
                "modalidad", "distrito", "localidad", "lugar", 
                "direccion", "referencia", "latitud", "longitud"
            )
        }),
        ("Costos", {
            "fields": ("tipo_costo", "precio_desde", "precio_hasta")
        }),
        ("Organización y contacto", {
            "fields": (
                "organizador", "telefono", "whatsapp", "correo", 
                "sitio_web", "facebook", "instagram"
            )
        }),
        ("Información útil", {
            "fields": ("publico_objetivo", "recomendaciones", "notas")
        }),
        ("Multimedia", {
            "fields": ("imagen_principal", "texto_alt_imagen")
        }),
        ("Configuración", {
            "fields": ("destacado", "activo", "creado", "actualizado")
        }),
    )

    def rango_precios_soles(self, obj):
        if obj.precio_desde and obj.precio_hasta:
            return f"S/ {obj.precio_desde} - S/ {obj.precio_hasta}"
        if obj.precio_desde:
            return f"Desde S/ {obj.precio_desde}"
        if obj.precio_hasta:
            return f"Hasta S/ {obj.precio_hasta}"
        return "-"
    
    rango_precios_soles.short_description = "Rango en soles"


@admin.register(ImagenEvento)
class ImagenEventoAdmin(admin.ModelAdmin):
    list_display = ["evento", "titulo", "orden", "activo", "creado"]
    search_fields = ["evento__nombre", "titulo", "texto_alt"]
    list_filter = ["activo", "evento"]
    autocomplete_fields = ["evento"]
    ordering = ["evento__nombre", "orden", "id"]
    list_per_page = 25
