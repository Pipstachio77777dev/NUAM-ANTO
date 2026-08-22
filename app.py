import threading
import webbrowser

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pymongo.errors import DuplicateKeyError

import db
from db import ahora_iso, auditoria, calificaciones
from dominio.factores import COLUMNAS, calcular_factores
from dominio.validadores import _a_entero, validar

app = Flask(__name__)
CORS(app)

USUARIO_DEFECTO = "ADMIN@mail.com"
MSG_DUPLICADO = ("Ya existe una calificación con ese ejercicio, "
                 "mercado, instrumento y secuencia de evento")


def a_dto(doc):
    return {
        "id": str(doc["_id"]),
        "mercado": doc["mercado"],
        "instrumento": doc["instrumento"],
        "secuenciaEvento": doc["secuencia_evento"],
        "dividendo": doc["dividendo"],
        "fechaPago": doc["fecha_pago"],
        "valorHistorico": doc["valor_historico"],
        "ejercicio": doc["ejercicio"],
        "descripcion": doc.get("descripcion", ""),
        "isfut": bool(doc.get("isfut")),
        "factorActualizacion": doc["factor_actualizacion"],
        "origen": doc["origen"],
        "factores": {str(c): doc["factores"].get(str(c), 0) for c in COLUMNAS},
        "fechaCreacion": doc.get("fecha_creacion"),
        "fechaActualizacion": doc.get("fecha_actualizacion"),
    }


def normalizar(datos):
    datos = dict(datos)
    if datos.get("mercado"):
        datos["mercado"] = str(datos["mercado"]).upper()
    if datos.get("origen"):
        datos["origen"] = str(datos["origen"]).upper()
    if isinstance(datos.get("isfut"), str):
        datos["isfut"] = datos["isfut"].strip().lower() in ("si", "sí", "true", "1")
    ejercicio = _a_entero(datos.get("ejercicio"))
    if ejercicio is not None:
        datos["ejercicio"] = ejercicio
    secuencia = _a_entero(datos.get("secuenciaEvento"))
    if secuencia is not None:
        datos["secuenciaEvento"] = secuencia
    return datos


def construir_documento(datos):
    dividendo = float(datos["dividendo"])
    valor_historico = float(datos["valorHistorico"])
    factor_actualizacion = float(datos["factorActualizacion"])
    return {
        "mercado": datos["mercado"].upper(),
        "instrumento": str(datos["instrumento"]).strip(),
        "secuencia_evento": int(datos["secuenciaEvento"]),
        "dividendo": dividendo,
        "fecha_pago": str(datos.get("fechaPago") or datos.get("fecha")),
        "valor_historico": valor_historico,
        "ejercicio": int(datos["ejercicio"]),
        "descripcion": str(datos.get("descripcion", "") or "")[:255],
        "isfut": bool(datos.get("isfut")),
        "factor_actualizacion": factor_actualizacion,
        "origen": datos["origen"].upper(),
        "factores": calcular_factores(dividendo, valor_historico, factor_actualizacion),
    }


def registrar_auditoria(evento, registro_id=None, instrumento="", ejercicio=None,
                        resumen="", usuario=USUARIO_DEFECTO):
    auditoria.insert_one({
        "evento": evento,
        "registro_id": registro_id,
        "instrumento": instrumento or "",
        "ejercicio": ejercicio,
        "resumen": resumen,
        "usuario": usuario or USUARIO_DEFECTO,
        "fecha": ahora_iso(),
    })


def obtener_id(id_str):
    try:
        return ObjectId(id_str)
    except InvalidId:
        return None


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/calificaciones")
def listar():
    filtros = {}
    mercado = request.args.get("mercado", "").strip()
    origen = request.args.get("origen", "").strip()
    ejercicio = request.args.get("ejercicio", "").strip()
    if mercado:
        filtros["mercado"] = mercado.upper()
    if origen:
        filtros["origen"] = origen.upper()
    if ejercicio:
        ej = _a_entero(ejercicio)
        filtros["ejercicio"] = ej if ej is not None else -1
    docs = list(calificaciones.find(filtros))
    return jsonify({"total": len(docs), "registros": [a_dto(d) for d in docs]})


@app.route("/api/calificaciones", methods=["POST"])
def crear():
    datos = normalizar(request.get_json(silent=True) or {})
    errores = validar(datos)
    if errores:
        return jsonify({"errores": errores}), 400
    documento = construir_documento(datos)
    documento["fecha_creacion"] = ahora_iso()
    documento["fecha_actualizacion"] = ahora_iso()
    try:
        resultado = calificaciones.insert_one(documento)
    except DuplicateKeyError:
        return jsonify({"errores": [MSG_DUPLICADO]}), 400
    registrar_auditoria(
        "crear",
        registro_id=str(resultado.inserted_id),
        instrumento=documento["instrumento"],
        ejercicio=documento["ejercicio"],
        resumen=f"Se creó la calificación de {documento['instrumento']} ({documento['ejercicio']})",
        usuario=(request.get_json(silent=True) or {}).get("usuario"),
    )
    return jsonify(a_dto(calificaciones.find_one({"_id": resultado.inserted_id}))), 201


@app.route("/api/calificaciones/<id_doc>", methods=["PUT"])
def modificar(id_doc):
    _id = obtener_id(id_doc)
    if _id is None or calificaciones.find_one({"_id": _id}) is None:
        return jsonify({"errores": ["Registro no encontrado"]}), 404
    datos = normalizar(request.get_json(silent=True) or {})
    errores = validar(datos)
    if errores:
        return jsonify({"errores": errores}), 400
    documento = construir_documento(datos)
    documento["fecha_actualizacion"] = ahora_iso()
    try:
        calificaciones.replace_one({"_id": _id}, documento)
    except DuplicateKeyError:
        return jsonify({"errores": [MSG_DUPLICADO]}), 400
    registrar_auditoria(
        "modificar",
        registro_id=id_doc,
        instrumento=documento["instrumento"],
        ejercicio=documento["ejercicio"],
        resumen=f"Se modificó la calificación de {documento['instrumento']} ({documento['ejercicio']})",
        usuario=(request.get_json(silent=True) or {}).get("usuario"),
    )
    documento["_id"] = _id
    return jsonify(a_dto(documento))


@app.route("/api/calificaciones/<id_doc>", methods=["DELETE"])
def eliminar(id_doc):
    _id = obtener_id(id_doc)
    doc = calificaciones.find_one({"_id": _id}) if _id else None
    if doc is None:
        return jsonify({"errores": ["Registro no encontrado"]}), 404
    calificaciones.delete_one({"_id": _id})
    registrar_auditoria(
        "eliminar",
        registro_id=id_doc,
        instrumento=doc["instrumento"],
        ejercicio=doc["ejercicio"],
        resumen=f"Se eliminó la calificación de {doc['instrumento']} ({doc['ejercicio']})",
        usuario=request.args.get("usuario"),
    )
    return "", 204


@app.route("/api/calificaciones/catalogos")
def catalogos():
    ejercicios = sorted({int(e) for e in calificaciones.distinct("ejercicio") if e})
    return jsonify({"ejercicios": ejercicios})


@app.route("/api/calificaciones/auditoria")
def ver_auditoria():
    docs = list(auditoria.find().sort("fecha", -1))
    registros = [{
        "id": str(d["_id"]),
        "evento": d["evento"],
        "registroId": d.get("registro_id"),
        "instrumento": d.get("instrumento", ""),
        "ejercicio": d.get("ejercicio"),
        "resumen": d.get("resumen", ""),
        "usuario": d.get("usuario", ""),
        "fecha": d["fecha"],
    } for d in docs]
    return jsonify({"total": len(registros), "auditoria": registros})


@app.route("/api/calificaciones/masiva", methods=["POST"])
def carga_masiva():
    cuerpo = request.get_json(silent=True) or {}
    lineas = cuerpo.get("lineas", [])
    insertados = 0
    con_errores = 0
    errores = []
    for num, linea in enumerate(lineas, start=1):
        datos = normalizar(linea if isinstance(linea, dict) else {})
        fallos = validar(datos)
        if not fallos:
            documento = construir_documento(datos)
            documento["fecha_creacion"] = ahora_iso()
            documento["fecha_actualizacion"] = ahora_iso()
            try:
                calificaciones.insert_one(documento)
                insertados += 1
                continue
            except DuplicateKeyError:
                fallos.append(MSG_DUPLICADO)
        con_errores += 1
        errores.append({"fila": num, "errores": fallos, "linea": linea})
    registrar_auditoria(
        "carga masiva",
        resumen=f"Carga masiva: {insertados} insertado(s), {con_errores} con error(es)",
        usuario=cuerpo.get("usuario"),
    )
    return jsonify({
        "totalProcesadas": len(lineas),
        "insertados": insertados,
        "conErrores": con_errores,
        "errores": errores,
    })


if __name__ == "__main__":
    db.init_db(calcular_factores)
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
