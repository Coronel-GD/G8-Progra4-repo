"""
Aplicación Móvil E-Commerce - Demo
===================================

Esta es una aplicación demo funcional que demuestra cómo consumir las APIs
del backend Django para un e-commerce.

Autor: Backend Team
Fecha: Noviembre 2023
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

# Importar utilidades
from utils.auth_manager import AuthManager
from api.api_service import APIService

# Importar pantallas
from screens.login_screen import LoginScreen
from screens.products_screen import ProductsScreen
from screens.product_detail_screen import ProductDetailScreen
from screens.cart_screen import CartScreen


class ECommerceApp(App):
    """App principal del e-commerce."""
    
    def build(self):
        """Construir la aplicación."""
        # Inicializar gestor de autenticación y servicio de API
        self.auth_manager = AuthManager()
        self.api_service = APIService(self.auth_manager)
        
        # Crear el Screen Manager
        sm = ScreenManager()
        
        # Agregar todas las pantallas
        sm.add_widget(
            LoginScreen(
                self.api_service,
                self.auth_manager,
                name='login'
            )
        )
        
        sm.add_widget(
            ProductsScreen(
                self.api_service,
                self.auth_manager,
                name='products'
            )
        )
        
        sm.add_widget(
            ProductDetailScreen(
                self.api_service,
                self.auth_manager,
                name='product_detail'
            )
        )
        
        sm.add_widget(
            CartScreen(
                self.api_service,
                self.auth_manager,
                name='cart'
            )
        )
        
        # Pantalla inicial: si está autenticado ir a productos, sino a login
        if self.auth_manager.is_authenticated():
            sm.current = 'products'
        else:
            sm.current = 'login'
        
        return sm


if __name__ == '__main__':
    ECommerceApp().run()
