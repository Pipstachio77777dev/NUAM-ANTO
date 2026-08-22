const CREDENCIALES = { correo: "ADMIN@mail.com", clave: "1234" };

let vistaActual = "inicio";
let registroSeleccionado = null;
let registrosCache = [];
let editandoId = null;

const $ = (id) => document.getElementById(id);

const TITULOS = {
    inicio: "Inicio",
    consultar: "Consultar calificaciones",
    formulario: "Ingresar / Modificar calificación",
    masiva: "Carga masiva",
    trazabilidad: "Trazabilidad"
};

function alternarMenuUsuario() {
    $("menu-usuario").classList.toggle("oculto");
}

document.addEventListener("click", (e) => {
    if (!e.target.closest(".zona-usuario")) {
        $("menu-usuario").classList.add("oculto");
    }
});

function iniciarSesion(evento) {
    evento.preventDefault();
    const correo = $("login-correo").value.trim();
    const clave = $("login-clave").value;
    if (correo.toLowerCase() === CREDENCIALES.correo.toLowerCase() && clave === CREDENCIALES.clave) {
        $("vista-login").classList.add("oculto");
        $("app-principal").classList.remove("oculto");
        irA("inicio");
    } else {
        const caja = $("login-error");
        caja.textContent = "Correo o contraseña incorrectos.";
        caja.classList.remove("oculto");
    }
    return false;
}

function cerrarSesion() {
    $("app-principal").classList.add("oculto");
    $("vista-login").classList.remove("oculto");
    $("menu-usuario").classList.add("oculto");
    $("login-clave").value = "";
    registroSeleccionado = null;
    return false;
}

function alternarSidebar() {
    const sidebar = $("sidebar");
    const colapsado = sidebar.classList.toggle("colapsado");
    $("btn-colapsar").textContent = colapsado ? "›" : "‹";
}

function irA(vista) {
    vistaActual = vista;
    ["inicio", "consultar", "formulario", "masiva", "trazabilidad"].forEach((v) => {
        $("pantalla-" + v).classList.toggle("oculto", v !== vista);
    });
    $("tab-titulo").textContent = TITULOS[vista];
    $("btn-volver").style.visibility = vista === "inicio" ? "hidden" : "visible";
    ["nav-inicio", "nav-consultar", "nav-ingresar", "nav-masiva", "nav-trazabilidad"]
        .forEach((id) => $(id).classList.remove("activo"));
    const navMap = { inicio: "nav-inicio", consultar: "nav-consultar", formulario: "nav-ingresar",
                     masiva: "nav-masiva", trazabilidad: "nav-trazabilidad" };
    $(navMap[vista]).classList.add("activo");

    if (vista === "consultar") { deseleccionar(); cargarCatalogos(); consultar(); }
    if (vista === "trazabilidad") cargarTrazabilidad();
}

async function api(ruta, opciones = {}) {
    const respuesta = await fetch(ruta, opciones);
    if (respuesta.status === 204) return null;
    const cuerpo = await respuesta.json();
    if (!respuesta.ok) throw { estado: respuesta.status, cuerpo };
    return cuerpo;
}

/* ---------- CATÁLOGOS ---------- */

let catalogosCargados = false;

async function cargarCatalogos() {
    if (catalogosCargados) return;
    try {
        const datos = await api("/api/calificaciones/catalogos");
        const combo = $("filtro-ejercicio");
        datos.ejercicios.forEach((ej) => {
            const opcion = document.createElement("option");
            opcion.value = ej;
            opcion.textContent = ej;
            combo.appendChild(opcion);
        });
        catalogosCargados = true;
    } catch (e) {
        console.error("No se pudieron cargar los catálogos", e);
    }
}

/* ---------- CONSULTAR ---------- */

function seleccionarFila(tr, id) {
    document.querySelectorAll("#grilla-cuerpo tr").forEach((f) => f.classList.remove("seleccionada"));
    tr.classList.add("seleccionada");
    registroSeleccionado = registrosCache.find((r) => r.id === id) || null;
    $("btn-modificar").disabled = !registroSeleccionado;
    $("btn-eliminar").disabled = !registroSeleccionado;
}

function deseleccionar() {
    registroSeleccionado = null;
    $("btn-modificar").disabled = true;
    $("btn-eliminar").disabled = true;
}

function formatearNumero(n) {
    return Number(n).toLocaleString("es-CL", { maximumFractionDigits: 2 });
}

async function consultar() {
    const mercado = $("filtro-mercado").value;
    const origen = $("filtro-origen").value;
    const ejercicio = $("filtro-ejercicio").value;
    const params = new URLSearchParams();
    if (mercado) params.set("mercado", mercado);
    if (origen) params.set("origen", origen);
    if (ejercicio) params.set("ejercicio", ejercicio);

    try {
        const datos = await api("/api/calificaciones?" + params.toString());
        registrosCache = datos.registros;
        const cuerpo = $("grilla-cuerpo");
        cuerpo.innerHTML = "";
        $("grilla-vacia").classList.toggle("oculto", datos.total > 0);
        deseleccionar();
        datos.registros.forEach((r) => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td>${r.id.substring(0, 8)}</td>
                <td>${r.mercado}</td>
                <td>${r.instrumento}</td>
                <td>${r.secuenciaEvento}</td>
                <td style="text-align:right">${formatearNumero(r.dividendo)}</td>
                <td>${r.fechaPago}</td>
                <td style="text-align:right">${formatearNumero(r.valorHistorico)}</td>
                <td>${r.ejercicio}</td>
                <td>${r.isfut ? "Sí" : "No"}</td>
                <td>${r.origen}</td>
                <td>${(r.factores["8"] ?? 0).toFixed(8)}</td>`;
            fila.onclick = () => seleccionarFila(fila, r.id);
            cuerpo.appendChild(fila);
        });
    } catch (e) {
        alert("Error al consultar: " + JSON.stringify(e.cuerpo || e));
    }
}

/* ---------- FORMULARIO ---------- */

function irAFormulario() {
    editarId = null;
    limpiarFormulario();
    irA("formulario");
}

function modificarSeleccionado() {
    if (!registroSeleccionado) return;
    editarId = registroSeleccionado.id;
    const r = registroSeleccionado;
    $("titulo-formulario").textContent = `Modificar calificación — ${r.instrumento} (${r.ejercicio})`;
    $("f-mercado").value = r.mercado;
    $("f-instrumento").value = r.instrumento;
    $("f-secuencia").value = r.secuenciaEvento;
    $("f-dividendo").value = r.dividendo;
    $("f-fecha").value = r.fechaPago;
    $("f-valor-historico").value = r.valorHistorico;
    $("f-ejercicio").value = r.ejercicio;
    $("f-factor-actualizacion").value = r.factorActualizacion;
    $("f-origen").value = r.origen;
    $("f-isfut").checked = !!r.isfut;
    $("f-descripcion").value = r.descripcion || "";
    ocultarErroresFormulario();
    irA("formulario");
}

function limpiarFormulario() {
    $("titulo-formulario").textContent = "Ingresar calificación";
    ["f-instrumento", "f-secuencia", "f-dividendo", "f-fecha", "f-valor-historico",
     "f-ejercicio", "f-factor-actualizacion", "f-descripcion"].forEach((id) => ($(id).value = ""));
    $("f-mercado").value = "ACC";
    $("f-origen").value = "ENTIDAD";
    $("f-isfut").checked = false;
    ocultarErroresFormulario();
}

function mostrarErroresFormulario(errores) {
    const caja = $("form-errores");
    caja.innerHTML = "<b>No se pudo guardar:</b><ul>" +
        errores.map((e) => `<li>${e}</li>`).join("") + "</ul>";
    caja.classList.remove("oculto");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function ocultarErroresFormulario() {
    $("form-errores").classList.add("oculto");
}

async function guardarFormulario(evento) {
    evento.preventDefault();
    const cuerpo = {
        mercado: $("f-mercado").value,
        instrumento: $("f-instrumento").value,
        secuenciaEvento: $("f-secuencia").value,
        dividendo: $("f-dividendo").value,
        fechaPago: $("f-fecha").value,
        valorHistorico: $("f-valor-historico").value,
        ejercicio: $("f-ejercicio").value,
        descripcion: $("f-descripcion").value,
        isfut: $("f-isfut").checked,
        factorActualizacion: $("f-factor-actualizacion").value,
        origen: $("f-origen").value
    };
    const opciones = {
        method: editarId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cuerpo)
    };
    const url = editarId ? `/api/calificaciones/${editarId}` : "/api/calificaciones";
    try {
        await api(url, opciones);
        catalogosCargados = false;
        irA("consultar");
        consultar();
    } catch (e) {
        if (e.cuerpo && e.cuerpo.errores) mostrarErroresFormulario(e.cuerpo.errores);
        else mostrarErroresFormulario(["Error inesperado al guardar."]);
    }
    return false;
}

async function eliminarSeleccionado() {
    if (!registroSeleccionado) return;
    const r = registroSeleccionado;
    if (!confirm(`¿Eliminar la calificación de ${r.instrumento} (${r.ejercicio})?`)) return;
    try {
        await api(`/api/calificaciones/${r.id}`, { method: "DELETE" });
        deseleccionar();
        consultar();
    } catch (e) {
        alert("Error al eliminar: " + JSON.stringify(e.cuerpo || e));
    }
}

/* ---------- CARGA MASIVA ---------- */

const CAMPOS_MASIVA = [
    "ejercicio", "mercado", "instrumento", "fecha", "secuenciaEvento", "dividendo",
    "valorHistorico", "descripcion", "isfut", "factorActualizacion", "origen"
];

function leerArchivoMasiva(input) {
    const archivo = input.files[0];
    if (!archivo) return;
    const lector = new FileReader();
    lector.onload = () => { $("masiva-texto").value = lector.result; };
    lector.readAsText(archivo, "UTF-8");
}

function parsearLineasMasivas(texto) {
    return texto.split(/\r?\n/)
        .map((l) => l.trim())
        .filter((l) => l.length > 0)
        .map((linea) => {
            const partes = linea.split(",").map((p) => p.trim());
            const objeto = {};
            CAMPOS_MASIVA.forEach((campo, i) => { objeto[campo] = partes[i] ?? ""; });
            return objeto;
        });
}

async function procesarMasiva() {
    const texto = $("masiva-texto").value;
    if (!texto.trim()) { alert("Pega líneas o selecciona un archivo CSV primero."); return; }
    const lineas = parsearLineasMasivas(texto);
    try {
        const resultado = await api("/api/calificaciones/masiva", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lineas })
        });
        const resumen = $("masiva-resumen");
        resumen.classList.remove("oculto");
        resumen.className = "resumen-masiva";
        resumen.innerHTML =
            `<b>Total procesadas:</b> ${resultado.totalProcesadas} &nbsp;·&nbsp; ` +
            `<b class="ok">Insertadas:</b> ${resultado.insertados} &nbsp;·&nbsp; ` +
            `<b class="mal">Con errores:</b> ${resultado.conErrores}`;
        const cajaErrores = $("masiva-errores");
        if (resultado.errores.length) {
            cajaErrores.innerHTML = "<b>Detalle de errores:</b><ul>" +
                resultado.errores.map((e2) =>
                    `<li>Fila ${e2.fila}: ${e2.errores.join(" · ")}</li>`).join("") + "</ul>";
            cajaErrores.classList.remove("oculto");
        } else {
            cajaErrores.classList.add("oculto");
            $("masiva-texto").value = "";
        }
        catalogosCargados = false;
    } catch (e) {
        alert("Error en la carga masiva: " + JSON.stringify(e.cuerpo || e));
    }
}

/* ---------- TRAZABILIDAD ---------- */

function formatearFechaAuditoria(iso) {
    const d = new Date(iso);
    const pad = (n) => String(n).padStart(2, "0");
    return `${pad(d.getDate())}-${pad(d.getMonth() + 1)}-${d.getFullYear()} ` +
           `${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

async function cargarTrazabilidad() {
    try {
        const datos = await api("/api/calificaciones/auditoria");
        const lista = $("trazabilidad-lista");
        lista.innerHTML = "";
        if (!datos.total) {
            lista.innerHTML = '<div class="tarjeta-blanca vacio">Sin movimientos registrados.</div>';
            return;
        }
        datos.auditoria.forEach((a) => {
            const div = document.createElement("div");
            div.className = "evento-auditoria" + (a.evento === "eliminar" ? " eliminar" : "");
            div.innerHTML = `
                <div class="evento-tipo">${a.evento}</div>
                <div class="evento-resumen">${a.resumen}</div>
                <div class="evento-meta">${a.usuario} · ${formatearFechaAuditoria(a.fecha)}</div>`;
            lista.appendChild(div);
        });
    } catch (e) {
        alert("Error al cargar la trazabilidad: " + JSON.stringify(e.cuerpo || e));
    }
}
