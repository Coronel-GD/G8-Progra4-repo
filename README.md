# Django E-commerce

Este es un proyecto de comercio electrónico completo construido con Django. Incluye una API REST robusta, integración con pasarela de pagos MercadoPago, autenticación social y una aplicación móvil complementaria desarrollada en Kivy.

## Características Principales

*   **Backend:** Django
*   **Base de Datos:** PostgreSQL (Configuración en desarrollo y producción).
*   **API REST:** Implementada con Django REST Framework (DRF) y autenticación segura vía JWT (JSON Web Tokens).
*   **Autenticación de Usuarios:**
    *   Registro y login tradicional por correo electrónico.
    *   Login social con Google y GitHub (vía `django-allauth`).
*   **Pagos:** Integración completa con MercadoPago para procesamiento de transacciones.
*   **Frontend Web:** Interfaz responsiva utilizando plantillas de Django y Bootstrap 5 (`crispy-bootstrap5`).
*   **Aplicación Móvil:** Demo funcional construida con Kivy (ubicada en `mobile/`) que consume la API del backend.
*   **Despliegue:** Configuración lista para despliegue en Render (`render.yaml` y `build.sh`).

## Requisitos Previos

*   Python 3.10 o superior
*   PostgreSQL
*   Git

## Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu entorno local:

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd django-ecommerce-master
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto (al mismo nivel que `manage.py`) y define las siguientes variables. Puedes ajustar los valores según tu configuración local:

    ```env
    # Django
    SECRET_KEY=tu_clave_secreta_generada
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost

    # Base de Datos (PostgreSQL)
    DB_NAME=ecommerce_db
    DB_USER=postgres
    DB_PASSWORD=tu_password_db
    DB_HOST=localhost
    DB_PORT=5432

    # MercadoPago (Credenciales de prueba/producción)
    MERCADOPAGO_PUBLIC_KEY=tu_public_key
    MERCADOPAGO_ACCESS_TOKEN=tu_access_token
    MERCADOPAGO_SANDBOX=True
    ```

5.  **Aplicar migraciones a la base de datos:**
    ```bash
    python manage.py migrate
    ```

6.  **Crear un superusuario (opcional, para acceder al admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Ejecutar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```
    El sitio estará disponible en `http://127.0.0.1:8000/`.

## Aplicación Móvil (Kivy)

El proyecto incluye una aplicación móvil en la carpeta `mobile/` que interactúa con el backend.

**Para ejecutar la app móvil:**

1.  Asegúrate de que el servidor Django esté corriendo.
2.  Navega a la carpeta `mobile` o ejecuta desde la raíz:
    ```bash
    python mobile/main.py
    ```
    *Nota: Asegúrate de tener las dependencias de Kivy instaladas en tu entorno.*

## Estructura del Proyecto

*   `core/`: Aplicación principal con la lógica de negocio (Items, Ordenes, etc.).
*   `djecommerce/`: Configuración del proyecto Django (settings, urls, wsgi).
*   `mobile/`: Código fuente de la aplicación móvil Kivy.
*   `templates/`: Archivos HTML para el frontend web.
*   `static_in_env/`: Archivos estáticos (CSS, JS, imágenes).
