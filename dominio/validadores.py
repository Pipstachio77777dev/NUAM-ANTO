from datetime import datetime

MERCADOS = ("ACC", "CFI", "FMU")
ORIGENES = ("ENTIDAD", "SISTEMA")


def _a_numero(valor):
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        try:
            return float(valor.strip().replace(",", "."))
        except ValueError:
            return None
    return None


def _a_entero(valor):
    n = _a_numero(valor)
    if n is None or n != int(n):
        return None
    return int(n)


def validar(datos):
    errores = []

    ejercicio = _a_entero(datos.get("ejercicio"))
    if ejercicio is None or len(str(abs(ejercicio))) != 4:
        errores.append("Ejercicio debe ser numérico de largo 4")

    mercado = datos.get("mercado")
    if not isinstance(mercado, str) or len(mercado) != 3 or mercado.upper() not in MERCADOS:
        errores.append("Mercado debe ser texto de largo 3 (ACC/CFI/FMU)")

    instrumento = datos.get("instrumento")
    if not isinstance(instrumento, str) or not instrumento.strip() or len(instrumento) > 50:
        errores.append("Instrumento es obligatorio (máx. 50 caracteres)")

    fecha = datos.get("fechaPago") or datos.get("fecha")
    try:
        datetime.strptime(str(fecha), "%d-%m-%Y")
    except (ValueError, TypeError):
        errores.append("Fecha de pago debe tener formato DD-MM-AAAA")

    if _a_numero(datos.get("dividendo")) is None:
        errores.append("Dividendo debe ser numérico")
    if _a_numero(datos.get("valorHistorico")) is None:
        errores.append("Valor histórico debe ser numérico")
    if _a_numero(datos.get("factorActualizacion")) is None:
        errores.append("Factor de actualización debe ser numérico")

    origen = datos.get("origen")
    if not isinstance(origen, str) or origen.upper() not in ORIGENES:
        errores.append("Origen debe ser ENTIDAD o SISTEMA")

    secuencia = _a_entero(datos.get("secuenciaEvento"))
    if secuencia is None:
        errores.append("Secuencia de evento debe ser numérica")

    return errores
