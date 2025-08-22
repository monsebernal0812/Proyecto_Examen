from flask import Flask, request, jsonify, render_template, g
import sqlite3
from datetime import datetime

DATABASE = "creditos.db" #Nombre del archivo de la base de datos 

app = Flask(__name__) #Inicialización de la aplicación Flask

# ---------- Base de datos ----------
def get_db():
    """
    Conexión con la base de datos SQLite. 
    Si no existe una conexión activa en el contexto 'g', se crea una nueva
    """
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row #Permite acceder a las columnas como diccionario 
        g.db = conn
    return g.db

@app.teardown_appcontext
def close_db(_exc):
    """
    Cierra la conexión a la base de datos al terminar la petición
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    """
    Inicializa la base de datos ejecutando el script 'schema.sql'.
    Solo debe ejecutarse la primera vez para crear la tabla.
    """   
    db = get_db()
    with app.open_resource("schema.sql", mode="r") as f:
        db.executescript(f.read())
    db.commit()

# Llama esto una vez para crear la base:
# if __name__ == "__main__":
#     with app.app_context():
#         init_db()


# ---------- Validaciones ----------
def validar_credito(payload, parcial=False):
    """
    Valida los datos enviados para crear/actualizar un crédito. 
    -cliente: debe ser texto no vacío
    -monto: numérico >=0
    -tasa_interes: numérico >=0 
    -plazo: entero > 0
    -fecha_otorgamiento: formato YYYY-MM-DD
    """
    campos = ["cliente", "monto", "tasa_interes", "plazo", "fecha_otorgamiento"]
    if not parcial:
        for c in campos:
            if c not in payload:
                return f"Falta el campo obligatorio: {c}"

    if "cliente" in payload:
        if not isinstance(payload["cliente"], str) or not payload["cliente"].strip():
            return "cliente inválido"

    if "monto" in payload:
        try:
            monto = float(payload["monto"])
            if monto < 0:
                return "monto no puede ser negativo"
        except:
            return "monto debe ser numérico"

    if "tasa_interes" in payload:
        try:
            tasa = float(payload["tasa_interes"])
            if tasa < 0:
                return "tasa_interes no puede ser negativa"
        except:
            return "tasa_interes debe ser numérica"

    if "plazo" in payload:
        try:
            plazo = int(payload["plazo"])
            if plazo <= 0:
                return "plazo debe ser un entero mayor a 0"
        except:
            return "plazo debe ser entero"

    if "fecha_otorgamiento" in payload:
        fecha = str(payload["fecha_otorgamiento"])
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except:
            return "fecha_otorgamiento debe tener formato YYYY-MM-DD"

    return None

# ---------- Rutas para el front ----------
@app.get("/")
def home():
    """
    Renderiza la página principal (index.html)
    """
    return render_template("index.html")


# ---------- API para CRUD ----------
@app.get("/api/creditos")
def listar_creditos():
    """
    Devuelve la lista de todos los créditos en formato JSON.
    """
    db = get_db()
    rows = db.execute("SELECT * FROM creditos ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/creditos")
def crear_credito():
    """
    Crea un nuevo crédito a partir de los datos recibidos (JSON o formulario)
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    error = validar_credito(data)
    if error:
        return jsonify({"error": error}), 400

    db = get_db()
    cur = db.execute(
        """
        INSERT INTO creditos (cliente, monto, tasa_interes, plazo, fecha_otorgamiento)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["cliente"].strip(),
            float(data["monto"]),
            float(data["tasa_interes"]),
            int(data["plazo"]),
            data["fecha_otorgamiento"],
        ),
    )
    db.commit()
    nuevo_id = cur.lastrowid
    row = db.execute("SELECT * FROM creditos WHERE id = ?", (nuevo_id,)).fetchone()
    return jsonify(dict(row)), 201

@app.put("/api/creditos/<int:credito_id>")
def actualizar_credito(credito_id):
    """
    Actualiza un crédito existente según su ID.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    error = validar_credito(data)
    if error:
        return jsonify({"error": error}), 400

    db = get_db()
    existe = db.execute("SELECT id FROM creditos WHERE id = ?", (credito_id,)).fetchone()
    if not existe:
        return jsonify({"error": "Crédito no encontrado"}), 404

    db.execute(
        """
        UPDATE creditos
        SET cliente = ?, monto = ?, tasa_interes = ?, plazo = ?, fecha_otorgamiento = ?
        WHERE id = ?
        """,
        (
            data["cliente"].strip(),
            float(data["monto"]),
            float(data["tasa_interes"]),
            int(data["plazo"]),
            data["fecha_otorgamiento"],
            credito_id,
        ),
    )
    db.commit()
    row = db.execute("SELECT * FROM creditos WHERE id = ?", (credito_id,)).fetchone()
    return jsonify(dict(row))

@app.delete("/api/creditos/<int:credito_id>")
def eliminar_credito(credito_id):
    """
    Elimina un crédito por su ID
    """
    db = get_db()
    existe = db.execute("SELECT id FROM creditos WHERE id = ?", (credito_id,)).fetchone()
    if not existe:
        return jsonify({"error": "Crédito no encontrado"}), 404

    db.execute("DELETE FROM creditos WHERE id = ?", (credito_id,))
    db.commit()
    return jsonify({"ok": True})

# ---------- Agregado opcional: total y distribución ----------
@app.get("/api/creditos/total")
def total_creditos():
    """
    Devuelve la suma total de todos los créditos registrados
    """
    db = get_db()
    row = db.execute("SELECT COALESCE(SUM(monto), 0) as total FROM creditos").fetchone()
    return jsonify({"total": float(row["total"])})

@app.get("/api/creditos/por_cliente")
def distribucion_por_cliente():
    """
    Devuelve el total de créditos agrupados por cliente.
    """
    db = get_db()
    rows = db.execute("""
        SELECT cliente, SUM(monto) as total
        FROM creditos
        GROUP BY cliente
        ORDER BY total DESC
    """).fetchall()
    return jsonify([{"cliente": r["cliente"], "total": float(r["total"])} for r in rows])

if __name__ == "__main__":
    # Ejecutar init_db() solo la primera vez para crear la base.
    # Después comentar estas dos líneas para no borrar datos: 
    # with app.app_context():
    #     init_db()

    #Arrancar la aplicación en modo debug (recarga automática y errores detallados)
    app.run(debug=True)

