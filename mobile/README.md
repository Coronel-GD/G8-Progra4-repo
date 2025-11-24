# Aplicación Móvil E-Commerce - Documentación para Frontend Developer

## Descripción General

Esta es una aplicación móvil demo desarrollada con **Kivy** que consume las APIs REST del backend Django. El código está estructurado de forma profesional y modular para facilitar su extensión y mantenimiento.

## 🏗️ Arquitectura

```
mobile/
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias Python
├── api/
│   ├── __init__.py
│   └── api_service.py     # Servicio centralizado de API
├── utils/
│   ├── __init__.py
│   └── auth_manager.py    # Gestión de autenticación JWT
├── screens/
│   ├── __init__.py
│   ├── login_screen.py           # Pantalla de inicio de sesión
│   ├── products_screen.py        # Lista de productos
│   ├── product_detail_screen.py  # Detalle de un producto
│   └── cart_screen.py            # Carrito de compras
└── README.md              # Este archivo
```

## 🚀 Instalación y Ejecución

### Prerrequisitos

- Python 3.8+
- Backend Django corriendo en `http://127.0.0.1:8000`

### Instalar Dependencias

```bash
cd mobile
pip install -r requirements.txt
```

### Ejecutar la Aplicación

```bash
python main.py
```

## 📱 Funcionalidades Implementadas

### ✅ Autenticación
- Login con username/password
- Almacenamiento persistente de tokens JWT
- Opción de continuar sin login (solo ver productos)

### ✅ Productos
- Lista de todos los productos
- Scroll infinito
- Navegación a detalle de producto
- Muestra: título, descripción, precio, descuento

### ✅ Detalle de Producto
- Información completa del producto
- Categoría y etiqueta
- Precio con/sin descuento
- Botón "Agregar al Carrito" (requiere login)

### ✅ Carrito
- Lista de items agregados
- Cantidad y precio total por item
- Total general de la compra
- Botón de checkout con MercadoPago

### ✅ Checkout
- Crea preferencia de pago en MercadoPago
- Abre el navegador para completar el pago

## 🛠️ Componentes Principales

### 1. APIService (`api/api_service.py`)

Servicio centralizado para todas las llamadas HTTP al backend.

**Métodos disponibles:**

```python
# Autenticación
api_service.login(username, password)              # Login JWT
api_service.refresh_token(refresh_token)           # Refresh token

# Productos
api_service.get_products()                         # Lista de productos
api_service.get_product_detail(slug)              # Detalle de producto

# Usuario
api_service.get_user_profile()                    # Perfil del usuario
api_service.update_user_profile(data)             # Actualizar perfil

# Carrito
api_service.add_to_cart(slug)                     # Agregar producto
api_service.get_cart_summary()                    # Ver carrito

# Checkout
api_service.checkout()                             # Crear pago MercadoPago
```

**Ejemplo de uso:**

```python
from api.api_service import APIService

api = APIService(auth_manager)

# Obtener productos
products = api.get_products()
if 'error' not in products:
    for product in products:
        print(product['title'], product['price'])

# Agregar al carrito (requiere autenticación)
result = api.add_to_cart('producto-slug')
if 'message' in result:
    print(result['message'])
```

### 2. AuthManager (`utils/auth_manager.py`)

Gestiona tokens JWT y estado de autenticación.

**Métodos disponibles:**

```python
# Guardar tokens después del login
auth_manager.save_tokens(access, refresh, username)

# Verificar si está autenticado
if auth_manager.is_authenticated():
    print("Usuario autenticado")

# Obtener token para requests
token = auth_manager.get_access_token()

# Logout
auth_manager.clear_tokens()
```

**Almacenamiento:**
Los tokens se guardan en `tokens.json` en el directorio actual.

### 3. Screens (Pantallas)

Cada pantalla hereda de `Screen` y recibe `api_service` y `auth_manager` en el constructor.

**Navegación entre pantallas:**

```python
# Desde cualquier pantalla
self.manager.current = 'nombre_pantalla'

# Pantallas disponibles:
# 'login'
# 'products'
# 'product_detail'
# 'cart'
```

## 🎨 Cómo Extender la App

### Agregar una Nueva Pantalla

1. **Crear el archivo de la pantalla:**

```python
# screens/nueva_pantalla.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class NuevaPantalla(Screen):
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        
        layout = BoxLayout()
        layout.add_widget(Label(text='Nueva Pantalla'))
        self.add_widget(layout)
```

2. **Registrar en main.py:**

```python
from screens.nueva_pantalla import NuevaPantalla

# En el método build() de ECommerceApp
sm.add_widget(
    NuevaPantalla(
        self.api_service,
        self.auth_manager,
        name='nueva_pantalla'
    )
)
```

### Agregar un Nuevo Endpoint de API

1. **Agregar método en `api_service.py`:**

```python
def mi_nuevo_endpoint(self, param):
    """Descripción del endpoint."""
    return self._make_request(
        "GET",  # o POST, PUT, etc.
        f"mi-endpoint/{param}/",
        authenticated=True  # si requiere auth
    )
```

2. **Usar desde cualquier pantalla:**

```python
result = self.api_service.mi_nuevo_endpoint('valor')
```

### Mejorar el UI

El código actual usa widgets básicos de Kivy. Puedes mejorar la UI:

1. **Agregar imágenes de productos:**
   - Usar `AsyncImage` de Kivy para cargar imágenes desde URLs
   - Las URLs vienen en el campo `image_url` de cada producto

2. **Mejorar estilos:**
   - Usar archivos `.kv` para definir la UI de forma declarativa
   - Aplicar colores personalizados con `background_color`
   - Usar `canvas` para efectos visuales

3. **Agregar animaciones:**
   - Usar `Animation` de Kivy para transiciones suaves
   - Animar cambios de pantalla con `sm.transition`

## 📋 TODO / Mejoras Sugeridas

### Funcionalidades Pendientes

- [ ] **Modificar cantidad en carrito**: Actualmente solo agrega +1
- [ ] **Eliminar items del carrito**: Endpoint existe pero no está implementado en la UI
- [ ] **Búsqueda de productos**: Agregar campo de búsqueda
- [ ] **Filtros por categoría**: Filtrar productos por categoría/etiqueta
- [ ] **Imágenes de productos**: Mostrar las imágenes reales (actualmente solo texto)
- [ ] **Gestión de perfil**: Pantalla para editar dirección de envío
- [ ] **Historial de órdenes**: Ver órdenes anteriores
- [ ] **Notificaciones**: Feedback visual mejorado (toast, snackbar)

### Mejoras Técnicas

- [ ] **Manejo de errores mejorado**: Mostrar mensajes más específicos
- [ ] **Refresh automático de tokens**: Detectar token expirado y refrescar automáticamente
- [ ] **Caché de datos**: Guardar productos en caché local
- [ ] **Modo offline**: Permitir ver productos sin conexión
- [ ] **Testing**: Agregar tests unitarios
- [ ] **Logging**: Sistema de logs para debugging
- [ ] **Configuración**: Archivo de configuración para URLs, etc.

### UI/UX

- [ ] **Loader animations**: Indicadores de carga más bonitos
- [ ] **Pull to refresh**: Recargar productos con gesto
- [ ] **Cards con sombra**: Efectos visuales profesionales
- [ ] **Dark mode**: Tema oscuro
- [ ] **Onboarding**: Tutorial inicial para nuevos usuarios

## 🔧 Troubleshooting

### La app no se conecta al backend

**Problema:** Error "No se puede conectar al servidor"

**Soluciones:**
1. Verificar que el backend Django esté corriendo: `python manage.py runserver`
2. Verificar la URL en `api_service.py` (debe ser `http://127.0.0.1:8000/api`)
3. Si usas emulador Android, cambiar a `http://10.0.2.2:8000/api`

### Error 401 Unauthorized

**Problema:** Peticiones autenticadas fallan con 401

**Soluciones:**
1. Verificar que el token no haya expirado
2. Hacer logout y login nuevamente
3. Eliminar `tokens.json` y volver a autenticarse

### Productos no aparecen después de login

**Problema:** Pantalla en blanco o "No hay productos"

**Soluciones:**
1. Verificar que hay productos en el backend admin
2. Revisar la consola para errores de API
3. Presionar el botón "🔄 Recargar"

## 📚 Recursos

### Documentación de APIs
Ver `API_DOCS.md` en la raíz del proyecto para documentación completa de todos los endpoints.

### Documentación de Kivy
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Kivy Widgets Guide](https://kivy.org/doc/stable/guide/widgets.html)
- [KV Language](https://kivy.org/doc/stable/guide/lang.html)

### Tutoriales Recomendados
- [Kivy Tutorial by Tech With Tim](https://www.youtube.com/playlist?list=PLzMcBGfZo4-kSJVMyYeOQ8CXJ3z1k7gHn)
- [Building Mobile Apps with Kivy](https://realpython.com/mobile-app-kivy-python/)

## 🤝 Contribuir

Si quieres extender o mejorar esta aplicación:

1. Mantén la estructura modular
2. Documenta tus cambios
3. Sigue el estilo de código existente
4. Agrega comentarios en español
5. Actualiza este README con tus cambios

## 📞 Contacto

Para preguntas sobre el backend o las APIs, contactar al equipo de backend.

Para preguntas sobre la app móvil, consultar este README o la documentación de Kivy.

---

**¡Happy Coding! 🚀**
