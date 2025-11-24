import requests
import json
from typing import Optional, Dict, Any


class APIService:
    """Servicio centralizado para todas las llamadas a la API del backend."""
    
    BASE_URL = "http://127.0.0.1:8000/api"
    
    def __init__(self, auth_manager=None):
        """
        Inicializar el servicio de API.
        
        Args:
            auth_manager: Instancia de AuthManager para manejar tokens
        """
        self.auth_manager = auth_manager
        self.session = requests.Session()
    
    def _get_headers(self, authenticated: bool = False) -> Dict[str, str]:
        """
        Obtener headers para las peticiones.
        
        Args:
            authenticated: Si requiere token de autenticación
            
        Returns:
            Dict con los headers necesarios
        """
        headers = {"Content-Type": "application/json"}
        
        if authenticated and self.auth_manager:
            token = self.auth_manager.get_access_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def _make_request(self, method: str, endpoint: str, authenticated: bool = False, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Realizar una petición HTTP.
        
        Args:
            method: Método HTTP (GET, POST, PUT, etc.)
            endpoint: Endpoint de la API
            authenticated: Si requiere autenticación
            data: Datos a enviar (para POST/PUT)
            
        Returns:
            Dict con la respuesta JSON o error
        """
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self._get_headers(authenticated)
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=data)
            elif method == "PATCH":
                response = self.session.patch(url, headers=headers, json=data)
            else:
                return {"error": f"Método {method} no soportado"}
            
            # Intentar parsear JSON
            try:
                return response.json()
            except:
                # Si no es JSON, devolver el texto
                return {"status_code": response.status_code, "text": response.text}
                
        except requests.exceptions.ConnectionError:
            return {"error": "No se puede conectar al servidor. Asegúrate de que el backend esté corriendo."}
        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}
    
    # === AUTENTICACIÓN ===
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login con username y password.
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Dict con access y refresh tokens
        """
        # El endpoint de token está en /api/token/, no /api/api/token/
        url = "http://127.0.0.1:8000/api/token/"
        headers = {"Content-Type": "application/json"}
        data = {"username": username, "password": password}
        
        try:
            response = self.session.post(url, headers=headers, json=data)
            return response.json()
        except Exception as e:
            return {"error": f"Error en login: {str(e)}"}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refrescar el access token.
        
        Args:
            refresh_token: Token de refresh
            
        Returns:
            Dict con el nuevo access token
        """
        url = "http://127.0.0.1:8000/api/token/refresh/"
        headers = {"Content-Type": "application/json"}
        data = {"refresh": refresh_token}
        
        try:
            response = self.session.post(url, headers=headers, json=data)
            return response.json()
        except Exception as e:
            return {"error": f"Error al refrescar token: {str(e)}"}
    
    # === PRODUCTOS ===
    
    def get_products(self) -> Dict[str, Any]:
        """
        Obtener lista de todos los productos.
        
        Returns:
            Lista de productos o error
        """
        return self._make_request("GET", "products/")
    
    def get_product_detail(self, slug: str) -> Dict[str, Any]:
        """
        Obtener detalle de un producto específico.
        
        Args:
            slug: Slug del producto
            
        Returns:
            Detalles del producto o error
        """
        return self._make_request("GET", f"products/{slug}/")
    
    # === USUARIO ===
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Obtener perfil del usuario autenticado.
        
        Returns:
            Datos del usuario o error
        """
        return self._make_request("GET", "user/", authenticated=True)
    
    def update_user_profile(self, data: Dict) -> Dict[str, Any]:
        """
        Actualizar perfil del usuario.
        
        Args:
            data: Datos a actualizar
            
        Returns:
            Usuario actualizado o error
        """
        return self._make_request("PATCH", "user/", authenticated=True, data=data)
    
    # === CARRITO ===
    
    def add_to_cart(self, slug: str) -> Dict[str, Any]:
        """
        Agregar un producto al carrito.
        
        Args:
            slug: Slug del producto
            
        Returns:
            Mensaje de confirmación o error
        """
        return self._make_request("POST", "add-to-cart/", authenticated=True, 
                                 data={"slug": slug})
    
    def get_cart_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen del carrito actual.
        
        Returns:
            Datos del carrito o error
        """
        return self._make_request("GET", "order-summary/", authenticated=True)
    
    def remove_single_item_from_cart(self, slug: str) -> Dict[str, Any]:
        """
        Quitar una unidad de un producto del carrito.
        
        Args:
            slug: Slug del producto
            
        Returns:
            Mensaje de confirmación o error
        """
        return self._make_request("POST", "remove-single-item/", authenticated=True, 
                                 data={"slug": slug})
    
    def remove_from_cart(self, slug: str) -> Dict[str, Any]:
        """
        Eliminar completamente un producto del carrito.
        
        Args:
            slug: Slug del producto
            
        Returns:
            Mensaje de confirmación o error
        """
        return self._make_request("POST", "remove-item/", authenticated=True, 
                                 data={"slug": slug})
    
    # === CHECKOUT ===
    
    def checkout(self) -> Dict[str, Any]:
        """
        Crear preferencia de pago en MercadoPago.
        
        Returns:
            Datos de la preferencia (URLs de pago) o error
        """
        return self._make_request("POST", "checkout/", authenticated=True)
