from django.db import models
from django.core.exceptions import ValidationError

class CategoriaEvento(models.Model):
    TIPO_ICONO_CHOICES = [
        ("bootstrap", "Bootstrap Icon"),
        ("imagen", "Imagen / SVG / GIF"),
        ("lottie", "Lottie JSON"),
    ]

    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    descripcion = models.TextField(blank=True)
    
    tipo_icono = models.CharField(max_length=20, choices=TIPO_ICONO_CHOICES, default="bootstrap")
    icono_bootstrap = models.CharField(
        max_length=80, 
        blank=True, 
        help_text="Ejemplo: bi-calendar-star-fill, bi-music-note-beamed"
    )
    icono_archivo = models.FileField(
        upload_to="eventos/categorias/iconos/", 
        blank=True, 
        help_text="Sube SVG, PNG, WebP, GIF o JSON Lottie si no usarás Bootstrap Icons."
    )

    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría de evento"
        verbose_name_plural = "Categorías de eventos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    TIPO_COSTO_CHOICES = [
        ("gratis", "Gratis"),
        ("pagado", "Pagado"),
        ("consultar", "Consultar"),
    ]

    MODALIDAD_CHOICES = [
        ("presencial", "Presencial"),
        ("virtual", "Virtual"),
        ("mixta", "Mixta"),
    ]

    # Clasificación
    categoria_principal = models.ForeignKey(
        CategoriaEvento, 
        related_name="eventos_principales", 
        on_delete=models.PROTECT, 
        verbose_name="Categoría principal"
    )
    categorias_secundarias = models.ManyToManyField(
        CategoriaEvento, 
        related_name="eventos_secundarios", 
        blank=True, 
        verbose_name="Categorías secundarias"
    )

    # Principal
    nombre = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    descripcion_corta = models.CharField(max_length=255, blank=True)
    descripcion = models.TextField(blank=True)

    # Fechas y horarios
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)

    # Ubicación
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default="presencial")
    distrito = models.ForeignKey(
        'ubicaciones.Distrito', 
        related_name="eventos", 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    localidad = models.ForeignKey(
        'ubicaciones.Localidad', 
        related_name="eventos", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    lugar = models.CharField(
        max_length=180, 
        blank=True, 
        help_text="Ejemplo: Plaza de Armas, Coliseo, Centro Cultural, explanada, auditorio."
    )
    direccion = models.CharField(max_length=255, blank=True)
    referencia = models.CharField(max_length=255, blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Costos
    tipo_costo = models.CharField(max_length=20, choices=TIPO_COSTO_CHOICES, default="consultar")
    precio_desde = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Precio desde", 
        help_text="Monto mínimo referencial en soles, si aplica."
    )
    precio_hasta = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Precio hasta", 
        help_text="Monto máximo referencial en soles, si aplica."
    )

    # Organización y contacto
    organizador = models.CharField(max_length=180, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    sitio_web = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    # Información útil
    recomendaciones = models.TextField(
        blank=True, 
        help_text="Consejos para asistentes: llegar temprano, llevar abrigo, restricciones, etc."
    )
    publico_objetivo = models.CharField(
        max_length=160, 
        blank=True, 
        help_text="Ejemplo: público general, familias, niños, turistas, jóvenes."
    )
    notas = models.TextField(blank=True, help_text="Información adicional interna o pública.")

    # Multimedia
    imagen_principal = models.ImageField(upload_to="eventos/principales/", blank=True)
    texto_alt_imagen = models.CharField(max_length=180, blank=True)

    # Control
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-fecha_inicio", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "fecha_inicio"],
                name="unique_evento_nombre_fecha_inicio"
            )
        ]

    def clean(self):
        super().clean()
        if self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': "La fecha de fin no puede ser anterior a la fecha de inicio."})
        
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio == self.fecha_fin:
            if self.hora_inicio and self.hora_fin and self.hora_fin < self.hora_inicio:
                raise ValidationError({'hora_fin': "La hora de fin no puede ser anterior a la hora de inicio."})
                
        if self.precio_desde and self.precio_hasta and self.precio_hasta < self.precio_desde:
            raise ValidationError({'precio_hasta': "El precio hasta no puede ser menor que el precio desde."})

    def __str__(self):
        return self.nombre


class ImagenEvento(models.Model):
    evento = models.ForeignKey(Evento, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="eventos/galeria/")
    titulo = models.CharField(max_length=160, blank=True)
    texto_alt = models.CharField(max_length=180, blank=True)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de evento"
        verbose_name_plural = "Imágenes de eventos"
        ordering = ["evento__nombre", "orden", "id"]

    def __str__(self):
        if self.titulo:
            return self.titulo
        return f"Imagen de {self.evento.nombre}"
