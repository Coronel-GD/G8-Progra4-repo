# OAuth Social Login en App Móvil - Guía de Implementación

## Contexto

Los endpoints de login social ya están disponibles en el backend:
- `POST /api/auth/google/` - Login con Google
- `POST /api/auth/github/` - Login con GitHub

Sin embargo, implementar OAuth2 en una app móvil nativa (Kivy) requiere consideraciones especiales.

## El Desafío

OAuth2 en apps móviles es diferente que en web porque:

1. **No hay URLs de callback simples**: Las apps nativas no tienen URLs web tradicionales
2. **Flujo de autorización**: Requiere abrir navegador, que el usuario se autentique, y capturar el token de vuelta
3. **Configuración externa**: Necesitas registrar la app móvil en Google Cloud Console y GitHub

## Opciones de Implementación

### Opción 1: Implementación Completa (Producción)

Para una app móvil en producción, el flujo correcto sería:

#### Configuración en Google Cloud Console
1. Ir a https://console.cloud.google.com/
2. Crear un proyecto o usar uno existente
3. Habilitar "Google+ API"
4. Crear credenciales OAuth 2.0 para aplicación móvil
5. Configurar redirect URI (ej: `myapp://oauth2callback`)

#### Configuración en GitHub
1. Ir a Settings > Developer settings > OAuth Apps
2. Registrar nueva OAuth app
3. Configurar redirect URI

#### Implementación en la App
```python
# Ejemplo conceptual (requiere librerías adicionales)
import webbrowser
from urllib.parse import urlencode

# 1. Construir URL de autorización
auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode({
    'client_id': 'TU_CLIENT_ID',
    'redirect_uri': 'myapp://oauth2callback',
    'response_type': 'code',
    'scope': 'openid email profile'
})}"

# 2. Abrir navegador
webbrowser.open(auth_url)

# 3. Capturar el callback (requiere configuración especial)
# En Android: registrar deep link en AndroidManifest.xml
# En iOS: registrar URL scheme en Info.plist

# 4. Intercambiar código por token
# 5. Enviar token al backend Django
```

**Ventajas:**
- Experiencia de usuario profesional
- Flujo automático completo
- Seguro

**Desventajas:**
- Requiere configuración externa compleja
- Específico de plataforma (Android/iOS)
- Fuera del alcance de Kivy puro

---

### Opción 2: Demo Simplificada (Navegador Manual)

Esta es una implementación de prueba concepto que muestra cómo funcionaría.

#### Implementación
```python
# screens/login_screen.py

import webbrowser

class LoginScreen(Screen):
    # ... código existente ...
    
    def login_with_google(self, instance):
        """Abrir navegador para login con Google."""
        # URL de login de Django con allauth
        url = "http://127.0.0.1:8000/accounts/google/login/"
        webbrowser.open(url)
        
        self.status_label.text = (
            "Completa el login en tu navegador.\n"
            "Luego copia el token de acceso y pégalo aquí."
        )
        # Mostrar campo para pegar token manualmente
        
    def login_with_github(self, instance):
        """Abrir navegador para login con GitHub."""
        url = "http://127.0.0.1:8000/accounts/github/login/"
        webbrowser.open(url)
        
        self.status_label.text = (
            "Completa el login en tu navegador.\n"
            "Luego copia el token de acceso y pégalo aquí."
        )
```

**Ventajas:**
- Fácil de implementar
- Muestra el concepto
- No requiere configuración externa compleja

**Desventajas:**
- Requiere intervención manual del usuario
- No es automático
- No es ideal para producción

---

### Opción 3: Solo Documentación

Documentar en el código y README que los endpoints existen y cómo se usarían desde una app móvil real.

```python
# api_service.py

def login_with_google_token(self, google_access_token):
    """
    Login con Google usando un token de acceso.
    
    En una app móvil real, obtendrías este token usando:
    - Google Sign-In SDK para Android/iOS
    - OAuth2 nativo de la plataforma
    
    Args:
        google_access_token: Token de acceso de Google
        
    Returns:
        JWT tokens del backend Django
        
    Ejemplo de uso en producción:
        # Usando Google Sign-In SDK (pseudocódigo)
        google_user = await GoogleSignIn.signIn()
        google_token = google_user.auth_token
        
        # Enviar al backend
        result = api_service.login_with_google_token(google_token)
        auth_manager.save_tokens(result['access'], result['refresh'], ...)
    """
    return self._make_request("POST", "auth/google/", 
                             data={"access_token": google_access_token})
```

---

## Recomendación

Para esta demo de e-commerce:

1. **Mantener login tradicional** (username/password) funcional ✅
2. **Documentar** cómo funcionarían los logins sociales ✅
3. **Opcional**: Implementar Opción 2 solo para demostración

Para una app en producción:
- Usar Opción 1 con configuración completa
- Considerar frameworks como React Native o Flutter que tienen mejor soporte para OAuth
- O usar bibliotecas específicas como `kivy-ios` o `python-for-android` con plugins de OAuth

## Código de Referencia

Los endpoints ya están implementados en el backend:

```python
# core/api/views.py

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/"

class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://127.0.0.1:8000/accounts/github/login/callback/"
```

**Uso desde la API:**
```bash
# POST /api/auth/google/
{
    "access_token": "google_access_token_aqui"
}

# Respuesta:
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 1,
        "username": "usuario",
        "email": "email@gmail.com"
    }
}
```

## Conclusión

El login social está **completamente funcional en el backend** y puede ser usado:
- ✅ Desde la interfaz web de Django (funciona ahora)
- ✅ Desde cualquier cliente que pueda obtener tokens OAuth2 (apps móviles reales con SDKs nativos)
- ⚠️ Desde Kivy requiere implementación especial o intervención manual

Para el propósito de esta demo, el login tradicional con username/password es suficiente y profesional.
