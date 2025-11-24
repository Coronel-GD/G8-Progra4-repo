from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from mobile.api.api_service import APIService
from mobile.utils.auth_manager import AuthManager
from mobile.screens.login_screen import LoginScreen
from mobile.screens.products_screen import ProductsScreen
from mobile.screens.product_detail_screen import ProductDetailScreen
from mobile.screens.cart_screen import CartScreen

class ECommerceApp(MDApp):
    def build(self):
        # Configuración del tema (Kickboxing Style)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.accent_palette = "Red"
        
        # Servicios
        self.api_service = APIService()
        self.auth_manager = AuthManager()
        
        # Screen Manager
        sm = ScreenManager()
        
        # Instanciar pantallas
        login_screen = LoginScreen(
            name='login',
            api_service=self.api_service,
            auth_manager=self.auth_manager
        )
        
        products_screen = ProductsScreen(
            name='products',
            api_service=self.api_service,
            auth_manager=self.auth_manager
        )
        
        product_detail_screen = ProductDetailScreen(
            name='product_detail',
            api_service=self.api_service,
            auth_manager=self.auth_manager
        )
        
        cart_screen = CartScreen(
            name='cart',
            api_service=self.api_service,
            auth_manager=self.auth_manager
        )
        
        # Agregar pantallas al manager
        sm.add_widget(login_screen)
        sm.add_widget(products_screen)
        sm.add_widget(product_detail_screen)
        sm.add_widget(cart_screen)
        
        # Decidir pantalla inicial
        if self.auth_manager.is_authenticated():
            sm.current = 'products'
        else:
            sm.current = 'login'
            
        return sm

if __name__ == '__main__':
    ECommerceApp().run()

