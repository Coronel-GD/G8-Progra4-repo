# Guía de Solución - Errores de Login Social

## Errores Actuales

### 1. Google: "Error 401: invalid_client"
**Causa:** Las credenciales OAuth de Google no están correctamente configuradas o no coinciden.

### 2. GitHub: "Error 404"
**Causa:** La aplicación social de GitHub probablemente no está registrada en Django.

---

## Solución Paso a Paso

### Paso 1: Verificar Configuración Actual

1. Ve a: `http://127.0.0.1:8000/admin/socialaccount/socialapp/`
2. Inicia sesión con tu cuenta admin
3. Deberías ver una lista de "Social applications"

### Paso 2: Verificar Google

Si existe una aplicación de Google:

1. Haz click para editarla
2. Verifica estos campos:
   - **Provider:** Debe ser exactamente "Google"
   - **Name:** Puede ser cualquier cosa (ej: "Google Login")
   - **Client ID:** [tu_client_id].apps.googleusercontent.com
   - **Secret key:** [tu_secret]
   - **Sites:** Debe tener "example.com" seleccionado en "Chosen sites"

**Problemas comunes:**
- ✗ Espacios al inicio o final del Client ID o Secret
- ✗ Client ID incompleto
- ✗ Secret key incorrecta
- ✗ No tener "Sites" seleccionado

**Solución:**
1. Copia nuevamente el Client ID desde Google Cloud Console
2. Copia nuevamente el Secret
3. Asegúrate de NO tener espacios
4. Guarda

### Paso 3: Configurar GitHub

Si NO existe una aplicación de GitHub:

1. Click en "AGREGAR APLICACIÓN SOCIAL +" (o similar)
2. Completa el formulario:

```
Provider: GitHub
Name: GitHub (o cualquier nombre descriptivo)
Client ID: [tu_github_client_id]
Secret key: [tu_github_secret]
Key: (dejar vacío)
```

3. En "Sites available", mueve "example.com" a "Chosen sites"
4. Guarda

### Paso 4: Obtener Credenciales de GitHub

Si no tienes las credenciales de GitHub:

1. Ve a: https://github.com/settings/developers
2. Click "OAuth Apps" → "New OAuth App"
3. Completa:
   - **Application name:** E-commerce App
   - **Homepage URL:** `http://127.0.0.1:8000/`
   - **Authorization callback URL:** `http://127.0.0.1:8000/accounts/github/login/callback/`
4. Click "Register application"
5. Copia el "Client ID"
6. Click "Generate a new client secret"
7. Copia el "Client secret" (¡solo se muestra una vez!)
8. Pega ambos en Django admin

---

## Verificación Final

Después de configurar todo:

1. Cierra el navegador completamente
2. Abre de nuevo: `http://127.0.0.1:8000/accounts/google/login/`
3. Debería funcionar sin errores

---

## Comandos útiles

Si hiciste cambios en configuración, reinicia el servidor:

```bash
# Detener el servidor (Ctrl+C)
# Luego volver a iniciar:
python manage.py runserver
```

---

## Checklist Final

- [ ] Google está configurado en `/admin/socialaccount/socialapp/`
- [ ] GitHub está configurado en `/admin/socialaccount/socialapp/`
- [ ] Ambos tienen "Sites" seleccionado
- [ ] Client IDs no tienen espacios
- [ ] Secrets no tienen espacios
- [ ] Servidor Django reiniciado
- [ ] Probado en navegador limpio (modo incógnito)
