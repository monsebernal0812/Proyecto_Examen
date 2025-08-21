# Sistema de Registro de Créditos

Aplicación web desarrollada en **Python (Flask)** con **SQLite** como base de datos.  
Permite registrar, listar, editar y eliminar créditos, además de mostrar gráficas del total otorgado y la distribución por cliente.

---

## Tecnologías utilizadas
- **Backend**: Python 3.12 + Flask 3.0.3
- **Base de datos**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Gráficas**: Chart.js

---

## Instalación
### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/creditos_app.git
cd creditos_app ´´´

python -m venv .venv
# Windows:
.\.venv\Scripts\Activate
# macOS/Linux:
source .venv/bin/activate

---

## Instalar dependencias 
pip install Flask==3.0.3

---

## Inicializar la base de datos por primera vez 
La primera vez que ejecutes el proyecto, deja activida la línea en app.py: 
with app.app_context():
    init_db()
Esto creará la base de datos "creditos.db"
Después comenta esas líneas para no borrar tus datos en siguientes ejecuciones 

---
## Activar el entorno 
Primero se colocara esto: 
cd Desktop\creditos_app
.venv\Scripts\activate

Una vez que en la misma terminal este activo (.ven) escribe: 
python app.py

---

## Ejecutar en el navegador

Al momento de poner el comando de "python", abriremos lo que es el siguiente enlace: 

http://127.0.0.1:5000/
