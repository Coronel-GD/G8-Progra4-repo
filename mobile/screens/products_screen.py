"""Pantalla de lista de productos."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
import threading


class ProductsScreen(Screen):
    """Pantalla que muestra la lista de productos."""
    
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        self.products = []
        
        # Layout principal
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header con título y botones (se creará dinámicamente)
        self.header = BoxLayout(size_hint=(1, None), height=60, spacing=10)
        self.main_layout.add_widget(self.header)
        
        # Botón de recargar
        self.refresh_button = Button(
            text='🔄 Cargar Productos',
            size_hint=(1, None),
            height=50
        )
        self.refresh_button.bind(on_press=self.load_products)
        self.main_layout.add_widget(self.refresh_button)
        
        # Área de productos (ScrollView)
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.product_list = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5
        )
        self.product_list.bind(minimum_height=self.product_list.setter('height'))
        self.scroll_view.add_widget(self.product_list)
        self.main_layout.add_widget(self.scroll_view)
        
        self.add_widget(self.main_layout)
    
    def _update_header(self):
        """Actualizar el header según el estado de autenticación."""
        self.header.clear_widgets()
        
        title = Label(
            text='Productos',
            font_size='20sp',
            bold=True,
            size_hint=(0.4, 1)
        )
        self.header.add_widget(title)
        
        # Botones de navegación
        nav_buttons = BoxLayout(size_hint=(0.6, 1), spacing=5)
        
        if self.auth_manager.is_authenticated():
            # Botón de carrito
            cart_btn = Button(text='🛒', size_hint=(0.2, 1))
            cart_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'cart'))
            nav_buttons.add_widget(cart_btn)
            
            # Nombre de usuario
            user_label = Label(
                text=f'👤 {self.auth_manager.get_username()}',
                size_hint=(0.5, 1)
            )
            nav_buttons.add_widget(user_label)
            
            # Botón de logout
            logout_btn = Button(
                text='Salir',
                size_hint=(0.3, 1),
                background_color=(1, 0.3, 0.3, 1)
            )
            logout_btn.bind(on_press=self.do_logout)
            nav_buttons.add_widget(logout_btn)
        else:
            login_btn = Button(text='Iniciar Sesión')
            login_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
            nav_buttons.add_widget(login_btn)
        
        self.header.add_widget(nav_buttons)
    
    def do_logout(self, instance):
        """Mostrar confirmación antes de cerrar sesión."""
        # Crear contenido del popup
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Mensaje
        message = Label(
            text='¿Estás seguro que deseas\ncerrar sesión?',
            size_hint=(1, 0.6)
        )
        content.add_widget(message)
        
        # Botones
        buttons = BoxLayout(size_hint=(1, 0.4), spacing=10)
        
        # Botón Cancelar
        cancel_btn = Button(
            text='Cancelar',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        buttons.add_widget(cancel_btn)
        
        # Botón Salir
        logout_btn = Button(
            text='Salir',
            background_color=(1, 0.3, 0.3, 1)
        )
        buttons.add_widget(logout_btn)
        
        content.add_widget(buttons)
        
        # Crear popup
        popup = Popup(
            title='Confirmar cierre de sesión',
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False
        )
        
        # Vincular acciones
        cancel_btn.bind(on_press=popup.dismiss)
        logout_btn.bind(on_press=lambda x: self._confirm_logout(popup))
        
        popup.open()
    
    def _confirm_logout(self, popup):
        """Ejecutar logout después de confirmación."""
        popup.dismiss()
        
        # Limpiar tokens
        self.auth_manager.clear_tokens()
        
        # Actualizar header
        self._update_header()
        
        # Navegar a login
        self.manager.current = 'login'
    
    def on_pre_enter(self):
        """Llamado antes de entrar a la pantalla."""
        # Actualizar header según estado de autenticación
        self._update_header()
        # Cargar productos automáticamente
        self.load_products()
    
    def load_products(self, instance=None):
        """Cargar productos desde la API."""
        self.refresh_button.text = 'Cargando...'
        self.refresh_button.disabled = True
        self.product_list.clear_widgets()
        
        threading.Thread(target=self._fetch_products).start()
    
    def _fetch_products(self):
        """Thread para obtener productos."""
        result = self.api_service.get_products()
        Clock.schedule_once(lambda dt: self._display_products(result))
    
    def _display_products(self, result):
        """Mostrar productos en la UI."""
        self.refresh_button.text = '🔄 Recargar'
        self.refresh_button.disabled = False
        
        if 'error' in result:
            error_label = Label(
                text=f"❌ {result['error']}",
                size_hint_y=None,
                height=100,
                color=(1, 0, 0, 1)
            )
            self.product_list.add_widget(error_label)
            return
        
        # result es una lista de productos
        if isinstance(result, list):
            self.products = result
            
            if not self.products:
                no_products = Label(
                    text='No hay productos disponibles',
                    size_hint_y=None,
                    height=100
                )
                self.product_list.add_widget(no_products)
                return
            
            for product in self.products:
                card = self._create_product_card(product)
                self.product_list.add_widget(card)
        else:
            error_label = Label(
                text='Error al cargar productos',
                size_hint_y=None,
                height=100,
                color=(1, 0, 0, 1)
            )
            self.product_list.add_widget(error_label)
    
    def _create_product_card(self, product):
        """Crear card para un producto."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=150,
            padding=10
        )
        
        # Título
        title = Label(
            text=product.get('title', 'Sin título'),
            bold=True,
            size_hint_y=0.4,
            font_size='16sp'
        )
        card.add_widget(title)
        
        # Descripción
        description = Label(
            text=product.get('description', '')[:100] + '...' if len(product.get('description', '')) > 100 else product.get('description', ''),
            size_hint_y=0.3,
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        card.add_widget(description)
        
        # Precio y botón
        bottom = BoxLayout(size_hint_y=0.3, spacing=10)
        
        price_text = f"${product.get('price', 0)}"
        if product.get('discount_price'):
            price_text = f"${product.get('discount_price')} (antes: ${product.get('price')})"
        
        price = Label(
            text=price_text,
            color=(0, 1, 0, 1),
            bold=True,
            size_hint=(0.5, 1)
        )
        bottom.add_widget(price)
        
        view_btn = Button(
            text='Ver Detalle',
            size_hint=(0.5, 1)
        )
        view_btn.bind(on_press=lambda x: self.view_product_detail(product))
        bottom.add_widget(view_btn)
        
        card.add_widget(bottom)
        
        # Línea separadora
        separator = Label(size_hint_y=None, height=2)
        card.add_widget(separator)
        
        return card
    
    def view_product_detail(self, product):
        """Navegar al detalle del producto."""
        # Pasar datos del producto a la pantalla de detalle
        detail_screen = self.manager.get_screen('product_detail')
        detail_screen.set_product(product)
        self.manager.current = 'product_detail'
