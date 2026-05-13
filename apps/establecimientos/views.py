from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from .models import (
    ContactoSucursalEstablecimiento,
    Establecimiento,
    CategoriaEstablecimiento,
    ImagenEstablecimiento,
    ServicioEstablecimiento,
    SucursalEstablecimiento,
)


def get_listado_context(request, tipo_establecimiento, titulo, subtitulo):
    """
    Contexto reutilizable para listados públicos de restaurantes y alojamientos.
    """

    # Queryset base por tipo y estado activo
    base_qs = Establecimiento.objects.filter(
        tipo=tipo_establecimiento,
        activo=True
    )

    # Categorías disponibles SOLO para el tipo actual:
    # restaurantes -> categorías de restaurantes
    # alojamientos -> categorías de alojamientos
    categorias_principales_ids = base_qs.exclude(
        categoria_principal__isnull=True
    ).values_list(
        "categoria_principal_id",
        flat=True
    )

    categorias_secundarias_ids = base_qs.exclude(
        categorias_secundarias__isnull=True
    ).values_list(
        "categorias_secundarias__id",
        flat=True
    )

    categorias_ids = list(categorias_principales_ids) + list(categorias_secundarias_ids)

    categorias = CategoriaEstablecimiento.objects.filter(
        activo=True,
        id__in=categorias_ids
    ).distinct().order_by("nombre")

    # Prefetch para sucursales activas.
    # Primero intenta traer la sucursal principal y luego las demás.
    sucursales_prefetch = Prefetch(
        "sucursales",
        queryset=SucursalEstablecimiento.objects.filter(
            activo=True
        ).order_by(
            "-es_principal",
            "id"
        )
    )

    qs = base_qs.select_related(
        "categoria_principal"
    ).prefetch_related(
        sucursales_prefetch
    )

    # Parámetros GET
    q = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "").strip()
    orden = request.GET.get("orden", "").strip()

    # Filtro por nombre
    if q:
        qs = qs.filter(nombre__icontains=q)

    # Filtro por categoría
    if categoria_id.isdigit():
        qs = qs.filter(
            Q(categoria_principal_id=categoria_id) |
            Q(categorias_secundarias__id=categoria_id)
        ).distinct()

    # Ordenamiento
    if orden == "nombre_asc":
        qs = qs.order_by("nombre", "id")

    elif orden == "nombre_desc":
        qs = qs.order_by("-nombre", "id")

    elif orden == "precio_asc":
        qs = qs.order_by("precio_desde", "precio_hasta", "nombre", "id")

    elif orden == "precio_desc":
        qs = qs.order_by("-precio_hasta", "-precio_desde", "nombre", "id")

    else:
        # Orden predeterminado
        qs = qs.order_by("id")

    # Paginación: 6 resultados por página
    paginator = Paginator(qs, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Opciones de categorías preparadas para el template.
    # Así evitamos usar comparaciones tipo categoria_sel == c.id dentro del HTML.
    categorias_opciones = []
    for categoria in categorias:
        categorias_opciones.append({
            "id": categoria.id,
            "nombre": categoria.nombre,
            "selected": str(categoria.id) == categoria_id,
        })

    # Opciones de orden preparadas para el template.
    # Así el select muestra correctamente la opción seleccionada.
    opciones_orden = [
    {
        "value": "",
        "label": "Seleccione",
        "selected": orden == "",
    },
    {
        "value": "nombre_asc",
        "label": "Nombre Ascendente",
        "selected": orden == "nombre_asc",
    },
    {
        "value": "nombre_desc",
        "label": "Nombre Descendente",
        "selected": orden == "nombre_desc",
    },
    {
        "value": "precio_asc",
        "label": "Menor a Mayor Precio",
        "selected": orden == "precio_asc",
    },
    {
        "value": "precio_desc",
        "label": "Mayor a Menor Precio",
        "selected": orden == "precio_desc",
    },
    ]

    context = {
    "page_obj": page_obj,
    "titulo": titulo,
    "subtitulo": subtitulo,
    "tipo": tipo_establecimiento,
    "q": q,
    "categoria_sel": categoria_id,
    "orden_sel": orden,
    "categorias": categorias,
    "categorias_opciones": categorias_opciones,
    "opciones_orden": opciones_orden,
    "total_resultados": paginator.count,

    # Switcher de apartados
    "es_restaurante": tipo_establecimiento == "restaurante",
    "es_alojamiento": tipo_establecimiento == "alojamiento",
    }

    return context


def listado_restaurantes(request):
    context = get_listado_context(
        request,
        "restaurante",
        "Descubre los mejores restaurantes de Huánuco",
        "Encuentra los lugares más deliciosos para disfrutar de la gastronomía local."
    )
    return render(request, "establecimientos/listado_establecimientos.html", context)


def listado_alojamientos(request):
    context = get_listado_context(
        request,
        "alojamiento",
        "Descubre los mejores alojamientos de Huánuco",
        "Encuentra el lugar perfecto para descansar y disfrutar de tu estadía."
    )
    return render(request, "establecimientos/listado_establecimientos.html", context)


def detalle_establecimiento(request, tipo_establecimiento, slug):
    sucursales_prefetch = Prefetch(
        "sucursales",
        queryset=SucursalEstablecimiento.objects.filter(
            activo=True
        ).select_related(
            "distrito",
            "localidad"
        ).prefetch_related(
            Prefetch(
                "contactos",
                queryset=ContactoSucursalEstablecimiento.objects.filter(
                    activo=True
                ).order_by(
                    "-es_principal",
                    "orden",
                    "id"
                )
            )
        ).order_by(
            "-es_principal",
            "nombre",
            "id"
        )
    )

    establecimiento = get_object_or_404(
        Establecimiento.objects.filter(
            activo=True,
            tipo=tipo_establecimiento
        ).select_related(
            "categoria_principal"
        ).prefetch_related(
            Prefetch(
                "categorias_secundarias",
                queryset=CategoriaEstablecimiento.objects.filter(activo=True).order_by("nombre")
            ),
            Prefetch(
                "servicios",
                queryset=ServicioEstablecimiento.objects.filter(activo=True).order_by("nombre")
            ),
            Prefetch(
                "imagenes",
                queryset=ImagenEstablecimiento.objects.filter(activo=True).order_by("orden", "id")
            ),
            sucursales_prefetch
        ),
        slug=slug
    )

    context = {
        "establecimiento": establecimiento,
        "es_restaurante": tipo_establecimiento == "restaurante",
        "es_alojamiento": tipo_establecimiento == "alojamiento",
        "volver_url_name": "establecimientos:listado_restaurantes"
        if tipo_establecimiento == "restaurante"
        else "establecimientos:listado_alojamientos",
    }

    return render(request, "establecimientos/detalle_establecimiento.html", context)
