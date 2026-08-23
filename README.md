# Biblioteca Digital

Sistema de gestión de biblioteca hecho con **Flask** (backend web) y **MySQL**
(persistencia), organizado en capas: rutas (Flask Blueprints) → capa de
acceso a datos (DAO) → base de datos.

Permite:

- Registrar, buscar, editar y eliminar **libros**.
- Registrar, buscar y eliminar **clientes**.
- Registrar **préstamos** (solo de libros disponibles, con bloqueo de fila
  para evitar prestar el mismo libro dos veces al mismo tiempo) y marcarlos
  como **devueltos**.
- Generar **multas** automáticamente cuando un préstamo se devuelve después
  de la fecha límite ($0.50 por día de atraso), y marcarlas como pagadas.
- Ver **reportes**: préstamos atrasados, libros más prestados y multas
  pendientes.

## Arquitectura

```
app/
  __init__.py         # application factory (crear_app)
  routes/              # un blueprint por sección (libros, clientes, préstamos, multas, reportes)
  templates/           # plantillas Jinja2 (base.html + una por sección)
  static/css/          # estilos
dao/                   # capa de acceso a datos (una clase por tabla)
database/
  schema.sql           # script de creación de tablas + datos de ejemplo
  conexion.py           # apertura/cierre de conexiones a MySQL
utils/
  excepciones.py        # jerarquía de excepciones propias del negocio
  logger.py              # configuración de logging (archivo + consola)
config.py               # constantes de negocio (días de préstamo, multa por día)
run.py                  # punto de entrada (arranca el servidor de desarrollo)
tests/                  # pruebas con pytest
```

Cada método de las clases DAO abre y cierra su propia conexión a MySQL (en
vez de compartir una conexión global), porque Flask puede atender varias
peticiones al mismo tiempo. Los errores de negocio (registro duplicado, libro
no disponible, etc.) se señalan con excepciones propias (`utils/excepciones.py`)
en vez de dejar pasar errores genéricos de MySQL hasta las rutas.

## Requisitos

- Python 3.10+ (recomendado 3.12; ver `.python-version`)
- MySQL 8+ o MariaDB 10.6+

## Instalación

1. Clonar el repositorio y entrar a la carpeta del proyecto.

2. Crear y activar un entorno virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # en Windows: .venv\Scripts\activate
   ```

3. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Crear la base de datos e importar el esquema (usa `utf8mb4` para que los
   acentos se guarden correctamente):

   ```bash
   mysql -u root -p -e "CREATE DATABASE biblioteca_digital CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   mysql -u root -p --default-character-set=utf8mb4 biblioteca_digital < database/schema.sql
   ```

   `schema.sql` crea las 4 tablas (`libros`, `usuarios`, `prestamos`,
   `multas`) e inserta algunos libros, clientes y un préstamo de ejemplo para
   poder probar la app de inmediato.

5. Copiar `.env.example` a `.env` y completar los datos de conexión:

   ```bash
   cp .env.example .env
   ```

   Editar `.env` con el usuario/contraseña de MySQL que se vaya a usar.
   **Este archivo no se sube a Git** (ya está en `.gitignore`).

## Ejecutar la aplicación

```bash
python run.py
```

Esto levanta el servidor de desarrollo de Flask en `http://127.0.0.1:5000/`.

También se puede usar el CLI de Flask:

```bash
export FLASK_APP=run.py      # en Windows (PowerShell): $env:FLASK_APP = "run.py"
flask run --debug
```

## Pruebas

```bash
pytest
```

Las pruebas usan la base de datos configurada en `.env`, así que hace falta
tener MySQL corriendo y el esquema importado antes de correrlas.

## Reglas de negocio

- Cada préstamo dura `DIAS_PRESTAMO = 7` días (ver `config.py`).
- La multa por atraso es `MULTA_POR_DIA = 0.50` dólares por cada día después
  de la fecha límite, y se genera automáticamente al registrar la devolución.
- No se puede eliminar un libro o un cliente que tenga préstamos asociados
  (para no perder ese historial).

## Equipo

| Nombre | Rol |
| --- | --- |
| _(completar)_ | _(completar)_ |
| _(completar)_ | _(completar)_ |
