document.addEventListener("DOMContentLoaded", function () {
    const conmutador = document.querySelector(".establecimientos-pagina .tipo-conmutador");

    if (!conmutador) return;

    const opciones = conmutador.querySelectorAll(".tipo-opcion");
    let cambiando = false;

    opciones.forEach(function (opcion) {
        opcion.addEventListener("click", function (event) {
            const destino = opcion.getAttribute("href");
            const tipo = opcion.dataset.tipo;

            /*
                Permitimos comportamiento normal si:
                - No existe href
                - Ya está activo
                - El usuario abre en nueva pestaña con Ctrl, Shift, Cmd o click central
            */
            if (
                !destino ||
                opcion.classList.contains("active") ||
                event.ctrlKey ||
                event.metaKey ||
                event.shiftKey ||
                event.altKey ||
                event.button === 1
            ) {
                return;
            }

            event.preventDefault();

            if (cambiando) return;
            cambiando = true;

            // Mueve el fondo activo del switch
            conmutador.classList.remove(
                "tipo-conmutador--izquierda",
                "tipo-conmutador--derecha"
            );

            if (tipo === "derecha") {
                conmutador.classList.add("tipo-conmutador--derecha");
            } else {
                conmutador.classList.add("tipo-conmutador--izquierda");
            }

            // Cambia visualmente el enlace activo
            opciones.forEach(function (item) {
                item.classList.remove("active");
                item.removeAttribute("aria-current");
            });

            opcion.classList.add("active");
            opcion.setAttribute("aria-current", "page");

            // Espera un momento para que se vea la animación antes de navegar
            window.setTimeout(function () {
                window.location.href = destino;
            }, 320);
        });
    });
});