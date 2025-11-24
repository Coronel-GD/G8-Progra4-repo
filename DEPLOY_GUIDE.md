# 🚀 Guía de Deploy: Render + UptimeRobot

Esta guía te permitirá desplegar tu aplicación Django en Render de forma **gratuita** y mantenerla activa 24/7 usando UptimeRobot.

## 1. Preparación (Ya realizada ✅)
Hemos creado los siguientes archivos necesarios:
- `requirements.txt`: Lista de dependencias para producción.
- `build.sh`: Script de instalación y migración.
- `render.yaml`: Configuración automática de infraestructura.
- `djecommerce/settings/production.py`: Configuración de Django para Render.

Solo necesitas hacer push de estos cambios a GitHub:
```bash
git add .
git commit -m "Configuración de deploy para Render"
git push
```

## 2. Configurar Render

1.  Ve a [dashboard.render.com](https://dashboard.render.com/) y regístrate con tu cuenta de **GitHub**.
2.  Haz click en **"New +"** y selecciona **"Blueprint"**.
3.  Conecta tu repositorio `django-ecommerce-master`.
4.  Render detectará automáticamente el archivo `render.yaml`.
5.  Verás que va a crear:
    - Un **Web Service** (tu app Django).
    - Una **Database** (PostgreSQL).
6.  Haz click en **"Apply Blueprint"**.
7.  ¡Listo! Render comenzará a construir tu aplicación. Esto puede tardar unos 5-10 minutos.

### Variables de Entorno Adicionales
El `render.yaml` ya configura la base de datos y la secret key automáticamente.
Si necesitas configurar MercadoPago o Google OAuth, ve a:
**Dashboard > Tu Web Service > Environment > Add Environment Variable**

Agrega estas variables:
- `MERCADOPAGO_PUBLIC_KEY`: Tu clave pública.
- `MERCADOPAGO_ACCESS_TOKEN`: Tu access token.
- `GOOGLE_CLIENT_ID`: Tu ID de cliente de Google.
- `GOOGLE_SECRET`: Tu secreto de Google.
- `RENDER_EXTERNAL_HOSTNAME`: (Automático) Render lo pone solo, pero asegúrate de que esté.

## 3. Configurar Google OAuth (Producción)

Una vez que tengas tu URL de Render (ej: `https://mi-tienda.onrender.com`), necesitas actualizar Google Cloud Console:

1.  Ve a [Google Cloud Console](https://console.cloud.google.com/).
2.  Edita tus credenciales de OAuth.
3.  Agrega tu dominio de Render a **"Orígenes autorizados de JavaScript"**:
    - `https://mi-tienda.onrender.com`
4.  Agrega la URL de callback a **"URI de redireccionamiento autorizados"**:
    - `https://mi-tienda.onrender.com/accounts/google/login/callback/`

## 4. Configurar MercadoPago (Webhooks)

1.  Ve a [Tu Dashboard de MercadoPago](https://www.mercadopago.com.ar/developers/panel/app).
2.  Edita tu aplicación o crea una nueva.
3.  En **Webhooks**, configura la URL de producción:
    - `https://mi-tienda.onrender.com/mercadopago/webhook/`
4.  Selecciona los eventos `payment`.

## 5. Evitar que se "duerma" (UptimeRobot)

Para que tu app no se apague después de 15 minutos de inactividad:

1.  Ve a [uptimerobot.com](https://uptimerobot.com/) y regístrate (gratis).
2.  Haz click en **"Add New Monitor"**.
3.  Configura:
    - **Monitor Type**: HTTP(s)
    - **Friendly Name**: Mi Ecommerce
    - **URL (or IP)**: `https://mi-tienda.onrender.com/` (Tu URL de Render)
    - **Monitoring Interval**: 5 minutes
4.  Haz click en **"Create Monitor"**.

¡Listo! UptimeRobot visitará tu sitio cada 5 minutos, manteniéndolo despierto y rápido siempre. 🚀
