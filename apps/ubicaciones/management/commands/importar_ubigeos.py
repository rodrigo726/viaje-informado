import json
import urllib.request
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from apps.ubicaciones.models import Departamento, Provincia, Distrito

class Command(BaseCommand):
    help = "Importa departamentos, provincias y distritos desde un JSON (archivo local o URL)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            type=str,
            help='Ruta al archivo JSON local'
        )
        parser.add_argument(
            '--url',
            type=str,
            help='URL del archivo JSON'
        )
        parser.add_argument(
            '--departamento',
            type=str,
            help='Opcional: Importar solo un departamento específico'
        )

    def handle(self, *args, **options):
        archivo = options.get('archivo')
        url = options.get('url')
        depto_filtro = options.get('departamento')

        if not archivo and not url:
            raise CommandError("Debes especificar --archivo o --url.")

        if archivo and url:
            raise CommandError("No puedes especificar --archivo y --url al mismo tiempo.")

        try:
            if archivo:
                with open(archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                response = urllib.request.urlopen(url)
                data = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise CommandError(f"Error al leer el JSON: {e}")

        deptos_creados_actualizados = 0
        provs_creados_actualizados = 0
        distritos_creados_actualizados = 0

        for depto_nombre, provs_data in data.items():
            if depto_filtro and depto_nombre.upper() != depto_filtro.upper():
                continue

            # Para el codigo inei del departamento, podemos inferirlo de un distrito cualquiera si existe
            depto_inei = None
            for _, distritos_data in provs_data.items():
                for _, distrito_info in distritos_data.items():
                    inei_val = distrito_info.get("inei")
                    if inei_val and len(str(inei_val)) >= 2:
                        depto_inei = str(inei_val)[:2]
                        break
                if depto_inei:
                    break

            depto, created = Departamento.objects.update_or_create(
                nombre_oficial=depto_nombre,
                defaults={
                    'slug': slugify(depto_nombre),
                    'codigo_inei': depto_inei
                }
            )
            deptos_creados_actualizados += 1

            for prov_nombre, distritos_data in provs_data.items():
                prov_inei = None
                for _, distrito_info in distritos_data.items():
                    inei_val = distrito_info.get("inei")
                    if inei_val and len(str(inei_val)) >= 4:
                        prov_inei = str(inei_val)[:4]
                        break
                if prov_inei:
                    pass

                prov, created = Provincia.objects.update_or_create(
                    departamento=depto,
                    nombre_oficial=prov_nombre,
                    defaults={
                        'slug': slugify(prov_nombre),
                        'codigo_inei': prov_inei
                    }
                )
                provs_creados_actualizados += 1

                for dist_nombre, distrito_info in distritos_data.items():
                    inei_val = distrito_info.get("inei")
                    if not inei_val:
                        self.stdout.write(self.style.WARNING(f"Saltando distrito {dist_nombre}: no tiene INEI"))
                        continue
                    
                    defaults_dist = {
                        'provincia': prov,
                        'nombre_oficial': dist_nombre,
                        'slug': slugify(dist_nombre),
                        'codigo_api': str(distrito_info.get("ubigeo", "")),
                        'api_id': distrito_info.get("id")
                    }
                    
                    dist, created = Distrito.objects.update_or_create(
                        codigo_inei=str(inei_val),
                        defaults=defaults_dist
                    )
                    distritos_creados_actualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Importación completada:\n"
            f"- Departamentos: {deptos_creados_actualizados}\n"
            f"- Provincias: {provs_creados_actualizados}\n"
            f"- Distritos: {distritos_creados_actualizados}"
        ))
