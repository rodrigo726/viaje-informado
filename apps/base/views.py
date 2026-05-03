from django.views.generic import TemplateView
from .models import HomeHeroSlide

class HomeView(TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "inicio"
        context["hero_slides"] = HomeHeroSlide.objects.filter(activo=True).order_by("orden", "id")
        return context

class PrivacidadView(TemplateView):
    template_name = 'base/privacidad.html'

class TerminosView(TemplateView):
    template_name = 'base/terminos.html'

class ContactoView(TemplateView):
    template_name = 'base/contacto.html'

class LoginVisualView(TemplateView):
    template_name = 'base/login_visual.html'
