COLUMNAS = list(range(8, 38))


def round8(v):
    v = float(v)
    negativo = v < 0
    s = f"{abs(v):.9f}"
    entera, decimales = s.split(".")
    bloque = decimales[:8]
    noveno = decimales[8] if len(decimales) > 8 else "0"
    if noveno >= "5":
        bloque = str(int(bloque) + 1).rjust(8, "0")
        if len(bloque) > 8:
            entera = str(int(entera) + 1)
            bloque = bloque[-8:]
    resultado = float(f"{entera}.{bloque}")
    return -resultado if negativo else resultado


def _pesos():
    suma = sum(0.96 ** i for i in range(30))
    return {i: round8((0.96 ** i) / suma) for i in range(30)}


PESOS_COLUMNA = _pesos()


def factor_columna(dividendo, valor_historico, factor_actualizacion, i):
    actualizacion = factor_actualizacion if factor_actualizacion > 0 else 1
    valor_actualizado = valor_historico * actualizacion
    if valor_actualizado <= 0:
        return 0.0
    f = round8((dividendo * PESOS_COLUMNA[i]) / valor_actualizado)
    return min(max(f, 0.0), 1.0)


def calcular_factores(dividendo, valor_historico, factor_actualizacion):
    return {
        str(col): factor_columna(dividendo, valor_historico, factor_actualizacion, col - 8)
        for col in COLUMNAS
    }
