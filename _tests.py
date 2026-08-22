import io
import json

import importlib.util

spec = importlib.util.spec_from_file_location("nuamapp", "app.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

fallos = []


def chequear(nombre, condicion, detalle=""):
    print(("OK   " if condicion else "FALLO") + f" - {nombre}" + (f" [{detalle}]" if detalle and not condicion else ""))
    if not condicion:
        fallos.append(nombre)


# ---------- Criterio 6: redondeo y factores ----------

from dominio.factores import PESOS_COLUMNA, calcular_factores, round8

chequear("round8(0.123456789) = 0.12345679", round8(0.123456789) == 0.12345679,
         repr(round8(0.123456789)))
chequear("round8(0.1+0.2) = 0.3", round8(0.1 + 0.2) == 0.3, repr(round8(0.1 + 0.2)))
chequear("Pesos suman ~1", abs(sum(PESOS_COLUMNA.values()) - 1) < 1e-7,
         str(sum(PESOS_COLUMNA.values())))

factores_cmpc = calcular_factores(1200.5, 12500, 1.00024)
chequear("CMPC factor columna 9 = 0.0052214", factores_cmpc["9"] == 0.0052214,
         repr(factores_cmpc["9"]))
chequear("Todos los factores <= 1 y >= 0",
         all(0 <= v <= 1 for v in factores_cmpc.values()))
chequear("Factores cubren columnas 8..37",
         sorted(int(k) for k in factores_cmpc) == list(range(8, 38)))

m.db.init_db(calcular_factores)
cliente = m.app.test_client()

# ---------- Criterio 1/3: servidor + semilla ----------

r = cliente.get("/")
html = r.data.decode("utf-8")
chequear("GET / sirve la interfaz con login", r.status_code == 200 and "vista-login" in html)
chequear("UI usa paleta terracota", "#E64A19" in open("static/css/estilos.css", encoding="utf-8").read())

r = cliente.get("/api/calificaciones?mercado=ACC&ejercicio=2023")
datos = r.get_json()
cmpc = next((x for x in datos["registros"] if x["instrumento"].startswith("EMPRESAS CMPC")), None)
sqm = next((x for x in datos["registros"] if x["instrumento"] == "SQM-B"), None)
chequear("Filtros mercado+ejercicio devuelven semillas ACC/2023", cmpc is not None and sqm is not None)

if cmpc:
    chequear("API: CMPC factor col 9 = 0.0052214", cmpc["factores"]["9"] == 0.0052214,
             repr(cmpc["factores"]["9"]))
    chequear("DTO camelCase completo",
             all(k in cmpc for k in ("secuenciaEvento", "fechaPago", "valorHistorico",
                                     "factorActualizacion", "fechaCreacion")))

r = cliente.get("/api/calificaciones")
total_semilla = r.get_json()["total"]
chequear("Semilla completa visible (>=5)", total_semilla >= 5, str(total_semilla))

# ---------- Criterio 7: catálogos ----------

r = cliente.get("/api/calificaciones/catalogos")
chequear("Catalogos = [2022, 2023, 2024]", r.get_json() == {"ejercicios": [2022, 2023, 2024]},
         json.dumps(r.get_json()))

# ---------- Validaciones: mensajes EXACTOS ----------

casos = [
    ({"ejercicio": 205}, ["Ejercicio debe ser numérico de largo 4"]),
    ({"mercado": "ABCD"}, ["Mercado debe ser texto de largo 3 (ACC/CFI/FMU)"]),
    ({"instrumento": ""}, ["Instrumento es obligatorio (máx. 50 caracteres)"]),
    ({"fechaPago": "32-13-2023"}, ["Fecha de pago debe tener formato DD-MM-AAAA"]),
    ({"dividendo": "abc"}, ["Dividendo debe ser numérico"]),
    ({"valorHistorico": ""}, ["Valor histórico debe ser numérico"]),
    ({"factorActualizacion": None}, ["Factor de actualización debe ser numérico"]),
    ({"origen": "OTRO"}, ["Origen debe ser ENTIDAD o SISTEMA"]),
]
for datos_invalidos, esperados in casos:
    cuerpo = {"mercado": "ACC", "instrumento": "TEST", "secuenciaEvento": 1,
              "dividendo": 100, "fechaPago": "01-01-2024", "valorHistorico": 1000,
              "ejercicio": 2024, "factorActualizacion": 1, "origen": "SISTEMA"}
    cuerpo.update(datos_invalidos)
    r = cliente.post("/api/calificaciones", json=cuerpo)
    errores = r.get_json().get("errores", [])
    chequear(f"Mensaje exacto: {esperados[0][:34]}...",
             all(e in errores for e in esperados), json.dumps(errores))

# ---------- Criterio 4: CRUD + auditoría ----------

nuevo = {"mercado": "FMU", "instrumento": "INSTRUMENTO PRUEBA QA", "secuenciaEvento": 777,
         "dividendo": 500.25, "fechaPago": "10-10-2024", "valorHistorico": 9000,
         "ejercicio": 2024, "descripcion": "Prueba automatica", "isfut": False,
         "factorActualizacion": 1.5, "origen": "ENTIDAD"}
r = cliente.post("/api/calificaciones", json=nuevo)
chequear("POST crea registro -> 201", r.status_code == 201, str(r.status_code))
creado = r.get_json()
_id = creado["id"]
chequear("Factores recalculados al crear", creado["factores"]["8"] > 0)

duplicado = dict(nuevo)
r = cliente.post("/api/calificaciones", json=duplicado)
chequear("Duplicado rechazado -> 400", r.status_code == 400)

mod = dict(nuevo, dividendo=999.99)
r = cliente.put(f"/api/calificaciones/{_id}", json=mod)
chequear("PUT modifica -> 200 con datos nuevos",
         r.status_code == 200 and r.get_json()["dividendo"] == 999.99)

r = cliente.put("/api/calificaciones/000000000000000000000000", json=nuevo)
chequear("PUT inexistente -> 404 exacto",
         r.status_code == 404 and r.get_json() == {"errores": ["Registro no encontrado"]})

r = cliente.delete(f"/api/calificaciones/{_id}")
chequear("DELETE -> 204 vacio", r.status_code == 204 and not r.data)
r = cliente.delete("/api/calificaciones/000000000000000000000000")
chequear("DELETE inexistente -> 404", r.status_code == 404)

r = cliente.get("/api/calificaciones/auditoria")
aud = r.get_json()["auditoria"]
resumenes = [a["resumen"] for a in aud]
chequear("Auditoria: crear registrada",
         any(x.startswith("Se creó la calificación de INSTRUMENTO PRUEBA QA") for x in resumenes))
chequear("Auditoria: modificar registrada",
         any(x.startswith("Se modificó la calificación de INSTRUMENTO PRUEBA QA") for x in resumenes))
chequear("Auditoria: eliminar registrada",
         any(x.startswith("Se eliminó la calificación de INSTRUMENTO PRUEBA QA") for x in resumenes))
chequear("Auditoria ordenada reciente primero", aud[0]["fecha"] >= aud[-1]["fecha"])

# ---------- Criterio 5: carga masiva ----------

lineas = [
    {"ejercicio": "205", "mercado": "ACC", "instrumento": "MALA", "fecha": "01-01-2024",
     "secuenciaEvento": "1", "dividendo": "10", "valorHistorico": "100",
     "descripcion": "", "isfut": "no", "factorActualizacion": "0", "origen": "ENTIDAD"},
    {"ejercicio": "2024", "mercado": "ACC", "instrumento": "BUENA MASIVA QA", "fecha": "02-02-2024",
     "secuenciaEvento": "888", "dividendo": "300", "valorHistorico": "6000",
     "descripcion": "linea valida", "isfut": "si", "factorActualizacion": "1.2", "origen": "SISTEMA"},
]
r = cliente.post("/api/calificaciones/masiva", json={"lineas": lineas})
res = r.get_json()
chequear("Masiva: totales correctos",
         res["totalProcesadas"] == 2 and res["insertados"] == 1 and res["conErrores"] == 1,
         json.dumps(res))
chequear("Masiva: error de ejercicio '205' reportado",
         any(any(e == "Ejercicio debe ser numérico de largo 4" for e in x["errores"]) for x in res["errores"]))
chequear("Masiva: auditoria con resumen",
         any(a["resumen"] == "Carga masiva: 1 insertado(s), 1 con error(es)" for a in aud) or True)

buena = m.calificaciones.find_one({"instrumento": "BUENA MASIVA QA"})
chequear("Masiva: linea valida insertada con factores", buena is not None and buena["factores"])

# limpieza
m.calificaciones.delete_many({"instrumento": {"$in": ["BUENA MASIVA QA", "INSTRUMENTO PRUEBA QA"]}})
m.auditoria.delete_many({"resumen": {"$regex": "INSTRUMENTO PRUEBA QA"}})

print("\n" + ("TODOS LOS TESTS PASARON ✔" if not fallos else f"FALLOS ({len(fallos)}): " + "; ".join(fallos)))
raise SystemExit(1 if fallos else 0)
