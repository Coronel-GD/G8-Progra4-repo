# Documentación de APIs - E-commerce Backend

## Tabla de Contenidos
- [Autenticación](#autenticación)
- [Productos](#productos)
- [Usuario](#usuario)
- [Carrito](#carrito)
- [Checkout y Pago](#checkout-y-pago)

---

## Base URL
```
http://127.0.0.1:8000/api/
```

---

## Autenticación

### 1. Login con JWT (Username/Password)

**Endpoint:** `POST /api/token/`

**Descripción:** Obtener token de acceso y refresh token usando credenciales.

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

**Respuesta exitosa (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 2. Refresh Token

**Endpoint:** `POST /api/token/refresh/`

**Descripción:** Obtener un nuevo access token usando el refresh token.

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Respuesta exitosa (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 3. Login con Google

**Endpoint:** `POST /api/auth/google/`

**Descripción:** Autenticación social con Google OAuth2.

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "access_token": "token_de_google"
}
```

**Respuesta exitosa (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "usuario_google",
    "email": "email@gmail.com"
  }
}
```

---

### 4. Login con GitHub

**Endpoint:** `POST /api/auth/github/`

**Descripción:** Autenticación social con GitHub OAuth2.

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "access_token": "token_de_github"
}
```

**Respuesta:** Similar a Google Login.

---

## Productos

### 5. Listar Productos

**Endpoint:** `GET /api/products/`

**Descripción:** Obtener lista de todos los productos disponibles.

**Autenticación:** No requerida

**Headers:**
```
Content-Type: application/json
```

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "title": "Guantes Proyect Negro",
    "price": 15000.0,
    "discount_price": null,
    "category": 1,
    "category_display": "Deportes",
    "label": 2,
    "label_display": "Nuevo",
    "slug": "guantes-proyect-negro",
    "description": "Guantes deportivos de alta calidad",
    "image_url": "/media/products/guantes_proyect.jpg"
  },
  {
    "id": 2,
    "title": "Camiseta Running",
    "price": 8000.0,
    "discount_price": 6500.0,
    "category": 1,
    "category_display": "Deportes",
    "label": 1,
    "label_display": "Descuento",
    "slug": "camiseta-running",
    "description": "Camiseta técnica para running",
    "image_url": "/media/products/camiseta.jpg"
  }
]
```

**Campos de respuesta:**
- `id`: ID del producto
- `title`: Nombre del producto
- `price`: Precio original
- `discount_price`: Precio con descuento (null si no hay)
- `category`: ID de la categoría
- `category_display`: Nombre de la categoría
- `label`: ID de la etiqueta
- `label_display`: Nombre de la etiqueta
- `slug`: Slug para URL
- `description`: Descripción del producto
- `image_url`: URL de la imagen

---

### 6. Detalle de Producto

**Endpoint:** `GET /api/products/<slug>/`

**Descripción:** Obtener detalles de un producto específico.

**Autenticación:** No requerida

**Parámetros de URL:**
- `slug`: Slug del producto (ej: `guantes-proyect-negro`)

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "title": "Guantes Proyect Negro",
  "price": 15000.0,
  "discount_price": null,
  "category": 1,
  "category_display": "Deportes",
  "label": 2,
  "label_display": "Nuevo",
  "slug": "guantes-proyect-negro",
  "description": "Guantes deportivos de alta calidad para entrenamientos intensivos",
  "image_url": "/media/products/guantes_proyect.jpg"
}
```

**Respuesta de error (404):**
```json
{
  "detail": "Not found."
}
```

---

## Usuario

### 7. Obtener/Actualizar Perfil de Usuario

**Endpoint:** `GET /api/user/` | `PUT /api/user/` | `PATCH /api/user/`

**Descripción:** Obtener o actualizar información del usuario autenticado.

**Autenticación:** ✅ Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

**GET - Respuesta exitosa (200):**
```json
{
  "id": 1,
  "username": "juan_perez",
  "email": "juan@example.com",
  "userprofile": {
    "one_click_purchasing": false,
    "street_address": "Av. Corrientes 1234",
    "apartment_address": "Piso 5 Dto A",
    "zip_code": "C1043AAZ",
    "city": "Buenos Aires",
    "country": "Argentina"
  }
}
```

**PUT/PATCH - Body para actualizar:**
```json
{
  "username": "juan_perez",
  "userprofile": {
    "street_address": "Nueva Dirección 5678",
    "apartment_address": "Piso 10",
    "zip_code": "C1050",
    "city": "CABA",
    "country": "Argentina"
  }
}
```

**PUT/PATCH - Respuesta exitosa (200):**
Devuelve el objeto actualizado (mismo formato que GET).

---

## Carrito

### 8. Agregar al Carrito

**Endpoint:** `POST /api/add-to-cart/`

**Descripción:** Agregar un producto al carrito del usuario autenticado.

**Autenticación:** ✅ Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

**Body:**
```json
{
  "slug": "guantes-proyect-negro"
}
```

**Respuesta exitosa - Primera vez (200):**
```json
{
  "message": "Item agregado al carrito"
}
```

**Respuesta exitosa - Ya existe (200):**
```json
{
  "message": "Cantidad actualizada"
}
```

**Respuesta de error (400):**
```json
{
  "message": "Invalid request"
}
```

**Respuesta de error (404):**
Producto no encontrado.

---

### 9. Ver Resumen del Carrito

**Endpoint:** `GET /api/order-summary/`

**Descripción:** Obtener el carrito actual del usuario con todos los items.

**Autenticación:** ✅ Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Respuesta exitosa (200):**
```json
{
  "id": 5,
  "order_items": [
    {
      "id": 12,
      "item": {
        "id": 1,
        "title": "Guantes Proyect Negro",
        "price": 15000.0,
        "discount_price": null,
        "category": 1,
        "category_display": "Deportes",
        "label": 2,
        "label_display": "Nuevo",
        "slug": "guantes-proyect-negro",
        "description": "Guantes deportivos de alta calidad",
        "image_url": "/media/products/guantes_proyect.jpg"
      },
      "quantity": 2,
      "final_price": 30000.0
    },
    {
      "id": 13,
      "item": {
        "id": 2,
        "title": "Camiseta Running",
        "price": 8000.0,
        "discount_price": 6500.0,
        "category": 1,
        "category_display": "Deportes",
        "label": 1,
        "label_display": "Descuento",
        "slug": "camiseta-running",
        "description": "Camiseta técnica para running",
        "image_url": "/media/products/camiseta.jpg"
      },
      "quantity": 1,
      "final_price": 6500.0
    }
  ],
  "total": 36500.0,
  "ordered": false,
  "ordered_date": null
}
```

**Campos de respuesta:**
- `id`: ID de la orden
- `order_items`: Array de items en el carrito
  - `item`: Detalles completos del producto
  - `quantity`: Cantidad de este producto
  - `final_price`: Precio total de este item (considera descuentos)
- `total`: Total de la orden (suma de todos los items)
- `ordered`: Si la orden ya fue procesada
- `ordered_date`: Fecha de la orden (null si no está procesada)

**Respuesta cuando el carrito está vacío (200):**
```json
null
```

---

## Checkout y Pago

### 10. Crear Preferencia de Pago (MercadoPago)

**Endpoint:** `POST /api/checkout/`

**Descripción:** Crear una preferencia de pago en MercadoPago para procesar el checkout.

**Autenticación:** ✅ Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

**Body:** No requiere body

**Respuesta exitosa (200):**
```json
{
  "preference_id": "123456789-abcd-1234-efgh-987654321",
  "init_point": "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=123456789-abcd-1234-efgh-987654321",
  "sandbox_init_point": "https://sandbox.mercadopago.com.ar/checkout/v1/redirect?pref_id=123456789-abcd-1234-efgh-987654321",
  "amount": 36500.0
}
```

**Campos de respuesta:**
- `preference_id`: ID de la preferencia de MercadoPago
- `init_point`: URL para redireccionar en producción
- `sandbox_init_point`: URL para redireccionar en sandbox/testing
- `amount`: Monto total a pagar

**Uso:**
1. Hacer POST a `/api/checkout/`
2. Recibir la respuesta con `sandbox_init_point` o `init_point`
3. Redireccionar al usuario a esa URL para completar el pago

**Respuesta de error (404):**
```json
{
  "message": "No tienes una orden activa"
}
```

**Respuesta de error (500):**
```json
{
  "message": "Error al crear la preferencia: [detalle del error]"
}
```

---

## Notas Importantes

### Autenticación JWT
Para endpoints protegidos, debes incluir el token en el header:
```
Authorization: Bearer <access_token>
```

### Expiración de Tokens
- **Access Token**: 60 minutos
- **Refresh Token**: 1 día

Cuando el access token expire, usa el endpoint `/api/token/refresh/` para obtener uno nuevo.

### Formato de Respuestas
Todas las respuestas son en formato JSON con `Content-Type: application/json`.

### Códigos de Estado HTTP
- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Error en los datos enviados
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: No autorizado
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

### URLs de Media
Las URLs de imágenes (`image_url`) son relativas. En producción, agregar el dominio:
```
https://tu-dominio.com/media/products/guantes_proyect.jpg
```

En desarrollo local:
```
http://127.0.0.1:8000/media/products/guantes_proyect.jpg
```

---

## Ejemplos de Uso con cURL

### Obtener lista de productos
```bash
curl -X GET http://127.0.0.1:8000/api/products/
```

### Login y obtener token
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tu_usuario","password":"tu_contraseña"}'
```

### Agregar producto al carrito (con token)
```bash
curl -X POST http://127.0.0.1:8000/api/add-to-cart/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -d '{"slug":"guantes-proyect-negro"}'
```

### Ver carrito (con token)
```bash
curl -X GET http://127.0.0.1:8000/api/order-summary/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

### Checkout (con token)
```bash
curl -X POST http://127.0.0.1:8000/api/checkout/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Flujo Completo de Compra

1. **Usuario navega productos**: `GET /api/products/`
2. **Usuario ve detalle**: `GET /api/products/<slug>/`
3. **Usuario se registra/loguea**: `POST /api/token/`
4. **Usuario agrega al carrito**: `POST /api/add-to-cart/` (con token)
5. **Usuario revisa carrito**: `GET /api/order-summary/` (con token)
6. **Usuario procede al pago**: `POST /api/checkout/` (con token)
7. **Usuario es redirigido a MercadoPago**: Usar `sandbox_init_point` de la respuesta
8. **Usuario completa el pago en MercadoPago**
9. **MercadoPago notifica al backend** (webhook, ya implementado)

---

## Para el Desarrollador Frontend

### Recomendaciones
1. **Manejo de Tokens**: Almacenar tokens de forma segura (localStorage o sessionStorage)
2. **Refresh de Tokens**: Implementar lógica para refrescar el access token automáticamente
3. **Error Handling**: Manejar todos los códigos de error apropiadamente
4. **Loading States**: Mostrar indicadores de carga durante las peticiones
5. **Validación**: Validar datos antes de enviarlos al backend

### Estructura Sugerida para Servicios
```javascript
// api.service.js
const BASE_URL = 'http://127.0.0.1:8000/api';

export const ProductService = {
  getAll: () => fetch(`${BASE_URL}/products/`),
  getBySlug: (slug) => fetch(`${BASE_URL}/products/${slug}/`)
};

export const AuthService = {
  login: (username, password) => 
    fetch(`${BASE_URL}/token/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password})
    }),
  refresh: (refreshToken) =>
    fetch(`${BASE_URL}/token/refresh/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({refresh: refreshToken})
    })
};

export const CartService = {
  addItem: (slug, token) =>
    fetch(`${BASE_URL}/add-to-cart/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({slug})
    }),
  getSummary: (token) =>
    fetch(`${BASE_URL}/order-summary/`, {
      headers: {'Authorization': `Bearer ${token}`}
    })
};

export const CheckoutService = {
  createPreference: (token) =>
    fetch(`${BASE_URL}/checkout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
};
```
