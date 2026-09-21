# Sistema de reservas de un club deportivo

API REST en Flask para gestionar deportes, canchas, socios y reservas de un club deportivo.

## Estado actual

Actualmente el proyecto incluye:

- la estructura de la API y sus rutas;
- respuestas provisorias para probar los endpoints;
- scripts para crear y cargar una base de datos MySQL local;
- la especificación del contrato esperado en `docs/swagger.yaml`.

La API todavía no se conecta a MySQL y no tiene implementadas las validaciones ni la lógica de negocio. Por ese motivo, los endpoints devuelven respuestas fijas y los datos creados con los scripts SQL se comprueban directamente desde MySQL.

## Requisitos

- Python 3.9 o superior;
- Docker con Docker Compose;
- `curl` o un cliente HTTP equivalente para probar la API.

MySQL 8.4 se ejecuta dentro de un contenedor, por lo que no es necesario instalar MySQL ni su cliente en la computadora.

## Preparar el entorno de Python

Desde la raíz del proyecto, crear y activar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell, la activación se realiza con:

```powershell
.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Levantar la base de datos local

### 1. Configurar las variables locales

Desde la raíz del proyecto, crear el archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Cada desarrollador debe definir sus propias contraseñas locales en `DB_PASSWORD` y `DB_ROOT_PASSWORD` dentro de `.env`. Estas credenciales sirven únicamente para acceder al contenedor MySQL que se ejecuta en su computadora: no permiten acceder a los contenedores de los demás integrantes y no es necesario que todos utilicen los mismos valores.

El archivo `.env` está ignorado por Git y no debe subirse al repositorio. Solo se comparte `.env.example`, que funciona como plantilla y no debe contener credenciales reales.

### 2. Iniciar MySQL

Ejecutar:

```bash
docker compose up -d db
```

MySQL 8.4 queda disponible únicamente en `127.0.0.1:3306`. En el primer inicio, Docker ejecuta automáticamente `db/init_db.sql` y `db/seed_data.sql`; estos archivos crean la base, sus tablas y los datos ficticios de desarrollo.

Comprobar el estado del contenedor:

```bash
docker compose ps
```

Para revisar el proceso de inicio y esperar hasta que aparezca el mensaje `ready for connections`:

```bash
docker compose logs -f db
```

Salir de la vista de logs con `Ctrl+C`; esto no detiene el contenedor.

### 3. Consideraciones sobre el volumen

Los scripts de inicialización automática solo se ejecutan cuando Docker crea un volumen de datos vacío. Si la base existe pero `SHOW TABLES` devuelve `Empty set`, aplicar los scripts manualmente sin borrar el volumen:

```bash
docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' < db/init_db.sql
docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' < db/seed_data.sql
```

Las credenciales definidas en `.env` también se aplican únicamente al crear un volumen nuevo. Para reiniciar completamente la base con la configuración actual se puede eliminar el volumen y volver a levantar el servicio. **Este procedimiento borra todos los datos locales de MySQL:**

```bash
docker compose down -v
docker compose up -d db
```

## Verificar la base de datos

Abrir el cliente de MySQL instalado dentro del contenedor:

```bash
docker compose exec db sh -c 'mysql -u"$MYSQL_USER" -p "$MYSQL_DATABASE"'
```

Cuando se solicite la contraseña, ingresar el valor de `DB_PASSWORD` definido en `.env`. Dentro de la consola de MySQL se pueden ejecutar las siguientes consultas:

```sql
SHOW TABLES;
SELECT * FROM deportes;
SELECT * FROM canchas;
SELECT * FROM socios;
SELECT * FROM reservas;
```

Para salir, ejecutar `exit`.

Para detener los contenedores sin borrar los datos:

```bash
docker compose down
```

## Ejecutar la API

Con el entorno virtual activado:

```bash
python app.py
```

La aplicación queda disponible en `http://127.0.0.1:5000`. El servidor se inicia en modo de desarrollo y se detiene con `Ctrl+C`.

## Probar el funcionamiento actual

Con la API en ejecución, abrir otra terminal y realizar algunas solicitudes:

```bash
curl http://127.0.0.1:5000/deportes
curl http://127.0.0.1:5000/canchas
curl http://127.0.0.1:5000/canchas/1
curl http://127.0.0.1:5000/canchas/disponibles
curl http://127.0.0.1:5000/socios
curl http://127.0.0.1:5000/socios/1
curl http://127.0.0.1:5000/reservas
curl http://127.0.0.1:5000/reservas/1
```

También se pueden comprobar las rutas que modifican recursos. En el estado actual no persisten cambios, pero permiten verificar el método HTTP y el código de respuesta:

```bash
curl -i -X POST http://127.0.0.1:5000/canchas
curl -i -X PATCH http://127.0.0.1:5000/canchas/1
curl -i -X DELETE http://127.0.0.1:5000/canchas/1

curl -i -X POST http://127.0.0.1:5000/socios
curl -i -X PATCH http://127.0.0.1:5000/socios/1

curl -i -X POST http://127.0.0.1:5000/reservas
curl -i -X PUT http://127.0.0.1:5000/reservas/1/estado
```

El contrato completo previsto para la API se encuentra en `docs/swagger.yaml`. Todavía no hay una suite de pruebas automatizadas en el proyecto; por ahora, la verificación se realiza con estas solicitudes y con las consultas SQL anteriores.
