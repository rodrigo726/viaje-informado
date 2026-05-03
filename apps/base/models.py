from django.db import models

class HomeHeroSlide(models.Model):
    TIPO_ARCHIVO_CHOICES = [
        ('image', 'Imagen'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]

    etiqueta = models.CharField(max_length=100, help_text="Ejemplo: Historia · Cultura · Naturaleza")
    titulo_principal = models.CharField(max_length=150, help_text="Ejemplo: Descubre lugares")
    titulo_resaltado = models.CharField(max_length=150, help_text="Ejemplo: con identidad")
    descripcion = models.TextField()
    
    tipo_archivo = models.CharField(max_length=10, choices=TIPO_ARCHIVO_CHOICES, default='image')
    archivo = models.FileField(upload_to="home/hero/", help_text="Acepta imagen, video o gif")
    poster_video = models.ImageField(upload_to="home/hero/posters/", blank=True, null=True, help_text="Imagen previa para videos (recomendado)")
    texto_alt = models.CharField(max_length=255, blank=True, help_text="Para accesibilidad de imágenes/gifs")
    
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    intervalo_ms = models.PositiveIntegerField(default=5500, help_text="Tiempo en milisegundos que dura el slide")
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = "Slide del Hero"
        verbose_name_plural = "Slides del Hero"

    def __str__(self):
        return f"{self.titulo_principal} {self.titulo_resaltado}"
