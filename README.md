# AYC API

API Django para gestionar clientes, órdenes de trabajo, técnicos y notificaciones.

## Puesta en marcha

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
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

## Estados de una orden

`pendiente` → `asignado` → `en_labor` → `realizado` → `terminado`

El técnico puede avanzar hasta `realizado`. El cierre en `terminado` queda bajo control administrativo.

## Notificaciones en tiempo real

El historial funciona aunque Pusher esté desactivado. Para activar la publicación en tiempo real, configura las credenciales de Pusher en `.env` y añade:

```env
PUSHER_ENABLED=True
```

## Pruebas

```powershell
python manage.py test users customer workorder notification electricalreport
```

Los informes de bombeo, generales y eléctricos se implementarán cuando estén definidos sus campos y reglas particulares.
