# AYC API

API Django para gestionar clientes, órdenes de trabajo, técnicos y notificaciones.

## Puesta en marcha

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

El usuario administrador debe crearse con un correo y una contraseña que cumpla las reglas de seguridad.

## Roles

- `admin`: administra técnicos, clientes y órdenes de trabajo.
- `tecnico`: consulta sus órdenes, cambia su estado y actualiza su perfil.

## Rutas principales

| Recurso | Ruta |
| --- | --- |
| Login | `POST /api/auth/login/` |
| Perfil | `GET/PATCH /api/auth/me/` |
| Cambio de contraseña | `POST /api/auth/change-password/` |
| Técnicos | `/api/auth/technicians/` |
| Clientes | `/api/customers/` |
| Órdenes | `/api/work-orders/` |
| Notificaciones | `/api/notifications/` |
| Informes de plantas eléctricas | `/api/electrical-reports/` |
| Informes de bombeo | `/api/pumping-reports/` |

## Informe de planta eléctrica

El informe conserva los 24 controles del formato físico. Cada control recibe un
estado obligatorio (`OK` o `NO`) y una observación opcional. La orden de trabajo
selecciona automáticamente la empresa, dirección, ciudad y teléfono del cliente.

Para crear un informe, autentícate y envía `POST /api/electrical-reports/` con
los campos generales del equipo (`report_date`, `responsible_name`, `generator`,
`brand`, `kva`, `motor`, `model_name`, `serial_number`), los 24 pares
`*_status`/`*_observation`, y los nombres de `technician_name` y `received_by`.

Las firmas se envían como imágenes Data URL, por ejemplo
`data:image/png;base64,...`. Para marcar el informe como `terminado` son
obligatorias la firma del técnico y la del recibido. El PDF se descarga con:

```text
GET /api/electrical-reports/{id}/pdf/
```

El envío directo al correo de la empresa se realiza con:

```text
POST /api/electrical-reports/{id}/send-email/
```

El informe debe estar terminado y firmado. El PDF se adjunta directamente
desde memoria, por lo que no queda almacenado en el servidor.

El informe de bombeo usa `POST /api/pumping-reports/`. Sus filas de equipos se
envían en `equipment_rows`, con presión, sumergibles, medida, placa, amperaje,
temperatura (`normal`/`recalentada`), ruidos (`normal`/`fallas`), humedad
(`si`/`no`) y conexiones eléctricas (`normal`/`fallas`). También incluye tanque
hidroneumático, controlador de velocidad, observaciones y firma del técnico.
Sus PDF y correo se generan con:

```text
GET /api/pumping-reports/{id}/pdf/
POST /api/pumping-reports/{id}/send-email/
```

## Estados de una orden

`pendiente` → `asignado` → `en_labor` → `realizado` → `terminado`

El técnico puede avanzar hasta `realizado`. El cierre en `terminado` queda bajo control administrativo.

## Notificaciones en tiempo real

El historial funciona aunque Pusher esté desactivado. Para activar la publicación en tiempo real, configura las credenciales de Pusher en `.env` y añade:

```env
PUSHER_ENABLED=True
```

## Ejecución con Docker

Requisitos: Docker Desktop iniciado.

1. Copia `.env.docker.example` como `.env.docker` y completa las claves de
   PostgreSQL, Django y correo.
2. Construye y levanta todos los servicios:

```powershell
docker compose --env-file .env.docker up --build -d
```

La API queda disponible en `http://localhost:8000`. La base de datos usa el
volumen `postgres_data`, Redis usa `redis_data` y los procesos de Celery se
levantan automáticamente. El contenedor `web` ejecuta las migraciones y
`collectstatic` al iniciar.

Comandos útiles:

```powershell
docker compose --env-file .env.docker logs -f web
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker down
```

Para borrar también los datos persistentes de PostgreSQL y Redis, ejecuta
`docker compose down -v` únicamente si deseas reiniciar la instalación desde
cero.

## Pruebas

```powershell
python manage.py test users customer workorder notification electricalreport pumpingreport
```

El informe general queda pendiente de definir sus campos y reglas particulares.

## Despliegue en Render con Docker

El archivo `render.yaml` define el despliegue completo: servicio web de Django,
worker de Celery, proceso beat, PostgreSQL y Redis administrado para las colas.
Render construye los servicios web y de Celery desde el mismo `Dockerfile`.

1. Sube el proyecto a un repositorio de GitHub o GitLab. No subas `.env`,
   `.env.docker` ni credenciales.
2. En Render abre **New > Blueprint**, conecta el repositorio y selecciona el
   archivo `render.yaml` de la raiz.
3. Completa los valores secretos que Render solicite: correo SMTP, URL del
   frontend, `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS`. Usa la misma
   `SECRET_KEY` para web, worker y beat cuando Render la solicite para esos
   servicios.
4. Espera a que el servicio web pase `GET /health/`. La respuesta esperada es
   `{"status":"ok"}`.
5. En el Shell del servicio web crea el primer administrador:

```text
python manage.py createsuperuser
```

El Blueprint usa PostgreSQL y conecta automaticamente la API y Celery a sus
servicios internos. Redis esta configurado con `noeviction` y persistencia,
porque se usa como broker de tareas. Los procesos web, worker, beat y Redis
persistente requieren el plan de Render correspondiente; la base de datos queda
en el plan gratuito para esta etapa de pruebas.

Los siguientes despliegues se hacen con un `push`. El Blueprint usa
`autoDeployTrigger: checksPass`, por lo que Render espera las pruebas de
GitHub antes de construir una nueva version. Las migraciones se ejecutan en
`preDeployCommand`; si se agrega una migracion que falla, el despliegue no debe
pasar a trafico.

Para probar la suite local sin depender del usuario PostgreSQL del `.env`:

```powershell
$env:URL_DB = "sqlite:///C:/ruta/ayc_api/ci-test.sqlite3"
\.venv\Scripts\python.exe manage.py test
```
