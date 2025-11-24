"""Gestión de autenticación y tokens JWT."""
import json
import os
from typing import Optional


class AuthManager:
    """Maneja el almacenamiento y validación de tokens JWT."""
    
    TOKEN_FILE = "tokens.json"
    
    def __init__(self):
        """Inicializar el gestor de autenticación."""
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.username: Optional[str] = None
        self.load_tokens()
    
    def load_tokens(self):
        """Cargar tokens desde el archivo si existe."""
        if os.path.exists(self.TOKEN_FILE):
            try:
                with open(self.TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access')
                    self.refresh_token = data.get('refresh')
                    self.username = data.get('username')
            except Exception as e:
                print(f"Error al cargar tokens: {e}")
    
    def save_tokens(self, access: str, refresh: str, username: str):
        """
        Guardar tokens en archivo.
        
        Args:
            access: Access token
            refresh: Refresh token
            username: Nombre de usuario
        """
        self.access_token = access
        self.refresh_token = refresh
        self.username = username
        
        try:
            with open(self.TOKEN_FILE, 'w') as f:
                json.dump({
                    'access': access,
                    'refresh': refresh,
                    'username': username
                }, f)
        except Exception as e:
            print(f"Error al guardar tokens: {e}")
    
    def clear_tokens(self):
        """Limpiar tokens (logout)."""
        self.access_token = None
        self.refresh_token = None
        self.username = None
        
        if os.path.exists(self.TOKEN_FILE):
            try:
                os.remove(self.TOKEN_FILE)
            except Exception as e:
                print(f"Error al eliminar tokens: {e}")
    
    def get_access_token(self) -> Optional[str]:
        """
        Obtener el access token actual.
        
        Returns:
            Access token o None
        """
        return self.access_token
    
    def get_refresh_token(self) -> Optional[str]:
        """
        Obtener el refresh token actual.
        
        Returns:
            Refresh token o None
        """
        return self.refresh_token
    
    def is_authenticated(self) -> bool:
        """
        Verificar si el usuario está autenticado.
        
        Returns:
            True si tiene access token, False en caso contrario
        """
        return self.access_token is not None
    
    def get_username(self) -> Optional[str]:
        """
        Obtener el nombre de usuario actual.
        
        Returns:
            Nombre de usuario o None
        """
        return self.username
    
    def update_access_token(self, new_access: str):
        """
        Actualizar solo el access token (usado en refresh).
        
        Args:
            new_access: Nuevo access token
        """
        self.access_token = new_access
        
        # Actualizar el archivo
        if self.refresh_token and self.username:
            self.save_tokens(new_access, self.refresh_token, self.username)
