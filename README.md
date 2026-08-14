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
python manage.py test users customer workorder notification
```

Los informes de bombeo, generales y eléctricos se implementarán cuando estén definidos sus campos y reglas particulares.
