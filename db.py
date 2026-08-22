from datetime import datetime, timezone

from pymongo import ASCENDING, MongoClient

client = MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=5000)
db = client["nuam"]

calificaciones = db["calificaciones"]
auditoria = db["auditoria"]

calificaciones.create_index(
    [("ejercicio", ASCENDING), ("mercado", ASCENDING),
     ("instrumento", ASCENDING), ("secuencia_evento", ASCENDING)],
    unique=True,
)

SEED = [
    {"mercado": "ACC", "instrumento": "EMPRESAS CMPC S.A.", "secuencia_evento": 12345,
     "dividendo": 1200.5, "fecha_pago": "15-05-2023", "valor_historico": 12500,
     "ejercicio": 2023, "descripcion": "Dividendo definitivo N°200", "isfut": True,
     "factor_actualizacion": 1.00024, "origen": "SISTEMA"},
    {"mercado": "ACC", "instrumento": "SQM-B", "secuencia_evento": 54321,
     "dividendo": 850.75, "fecha_pago": "30-08-2023", "valor_historico": 9800,
     "ejercicio": 2023, "descripcion": "Dividendo provisorio N°115", "isfut": False,
     "factor_actualizacion": 1.00018, "origen": "ENTIDAD"},
    {"mercado": "CFI", "instrumento": "CFI LARRAINVIAL US", "secuencia_evento": 98765,
     "dividendo": 4320.0, "fecha_pago": "10-03-2022", "valor_historico": 45000,
     "ejercicio": 2022, "descripcion": "Distribución renta CFI", "isfut": True,
     "factor_actualizacion": 1.0011, "origen": "ENTIDAD"},
    {"mercado": "FMU", "instrumento": "FM CONSULTORA PROYECCION", "secuencia_evento": 10234,
     "dividendo": 150.25, "fecha_pago": "22-11-2024", "valor_historico": 1800,
     "ejercicio": 2024, "descripcion": "Reparto utilidades FMU", "isfut": False,
     "factor_actualizacion": 0, "origen": "SISTEMA"},
    {"mercado": "FMU", "instrumento": "FM PRINCIPAL CHILE", "secuencia_evento": 10567,
     "dividendo": 275.4, "fecha_pago": "05-07-2024", "valor_historico": 2400,
     "ejercicio": 2024, "descripcion": "Cuota N°8", "isfut": True,
     "factor_actualizacion": 1.00005, "origen": "ENTIDAD"},
]


def ahora_iso():
    return datetime.now(timezone.utc).isoformat()


def init_db(calcular_factores):
    viejos = calificaciones.count_documents({"mercado": {"$exists": False}})
    if viejos:
        calificaciones.drop()
        auditoria.drop()
        calificaciones.create_index(
            [("ejercicio", ASCENDING), ("mercado", ASCENDING),
             ("instrumento", ASCENDING), ("secuencia_evento", ASCENDING)],
            unique=True,
        )
    if calificaciones.count_documents({}) == 0:
        ahora = ahora_iso()
        documentos = []
        for s in SEED:
            doc = dict(s)
            doc["factores"] = calcular_factores(s["dividendo"], s["valor_historico"],
                                                s["factor_actualizacion"])
            doc["fecha_creacion"] = ahora
            doc["fecha_actualizacion"] = ahora
            documentos.append(doc)
        calificaciones.insert_many(documentos)
        auditoria.insert_one({
            "evento": "carga masiva",
            "registro_id": None,
            "instrumento": "",
            "ejercicio": None,
            "resumen": "Se sembraron 5 registros iniciales de ejemplo",
            "usuario": "SISTEMA",
            "fecha": ahora,
        })
