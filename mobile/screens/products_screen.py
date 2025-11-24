"""Pantalla de lista de productos con estilo Kickboxing."""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDRectangleFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivy.metrics import dp
import threading

class ProductsScreen(MDScreen):
    """Pantalla que muestra la lista de productos."""
    
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        self.products = []
        self.dialog = None
        
        # Layout principal
        self.main_layout = MDBoxLayout(
            orientation='vertical',
            md_bg_color=(0.1, 0.1, 0.1, 1)
        )
        
        # Header
        self.header = MDBoxLayout(
            size_hint=(1, None),
            height=dp(60),
            padding=[10, 0],
            spacing=10,
            md_bg_color=(0.15, 0.15, 0.15, 1)
        )
        self.main_layout.add_widget(self.header)
        
        # Botón de recargar (temporal, luego será parte del header o refresh layout)
        # Por ahora lo ponemos como un botón flotante o en el header si cabe
        
        # Área de productos (ScrollView)
        self.scroll_view = MDScrollView(size_hint=(1, 1))
        self.product_list = MDGridLayout(
            cols=1,
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10),
            adaptive_height=True
        )
        self.scroll_view.add_widget(self.product_list)
        self.main_layout.add_widget(self.scroll_view)
        
        self.add_widget(self.main_layout)
    
    def _update_header(self):
        """Actualizar el header según el estado de autenticación."""
        self.header.clear_widgets()
        
        # Título
        title = MDLabel(
            text='PRODUCTOS',
            font_style='H6',
            theme_text_color='Custom',
            text_color=(1, 0, 0, 1),
            bold=True,
            size_hint_x=0.4,
            pos_hint={'center_y': 0.5}
        )
        self.header.add_widget(title)
        
        # Botones de navegación
        nav_buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=5,
            adaptive_width=True,
            pos_hint={'center_y': 0.5}
        )
        
        # Botón Recargar
        refresh_btn = MDIconButton(
            icon="refresh",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_press=self.load_products
        )
        nav_buttons.add_widget(refresh_btn)
        
        if self.auth_manager.is_authenticated():
            # Botón de carrito
            cart_btn = MDIconButton(
                icon="cart",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                on_press=lambda x: setattr(self.manager, 'current', 'cart')
            )
            nav_buttons.add_widget(cart_btn)
            
            # Nombre de usuario (corto)
            username = self.auth_manager.get_username()
            user_label = MDLabel(
                text=username[:10],
                theme_text_color='Secondary',
                size_hint_x=None,
                width=dp(80),
                halign='right',
                pos_hint={'center_y': 0.5}
            )
            nav_buttons.add_widget(user_label)
            
            # Botón de logout
            logout_btn = MDIconButton(
                icon="logout",
                theme_text_color="Custom",
                text_color=(1, 0.3, 0.3, 1),
                on_press=self.do_logout
            )
            nav_buttons.add_widget(logout_btn)
        else:
            login_btn = MDRectangleFlatButton(
                text='LOGIN',
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                line_color=(1, 0, 0, 1),
                on_press=lambda x: setattr(self.manager, 'current', 'login')
            )
            nav_buttons.add_widget(login_btn)
        
        self.header.add_widget(nav_buttons)
    
    def do_logout(self, instance):
        """Mostrar confirmación antes de cerrar sesión."""
        if not self.dialog:
            self.dialog = MDDialog(
                title="Cerrar Sesión",
                text="¿Estás seguro que deseas salir?",
                buttons=[
                    MDRectangleFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="SALIR",
                        md_bg_color=(1, 0, 0, 1),
                        on_release=lambda x: self._confirm_logout()
                    ),
                ],
            )
        self.dialog.open()
    
    def _confirm_logout(self):
        """Ejecutar logout después de confirmación."""
        self.dialog.dismiss()
        self.auth_manager.clear_tokens()
        self._update_header()
        self.manager.current = 'login'
    
    def on_pre_enter(self):
        """Llamado antes de entrar a la pantalla."""
        self._update_header()
        self.load_products()
    
    def load_products(self, instance=None):
        """Cargar productos desde la API."""
        self.product_list.clear_widgets()
        
        # Spinner de carga
        loading = MDLabel(
            text="Cargando productos...",
            halign="center",
            theme_text_color="Secondary"
        )
        self.product_list.add_widget(loading)
        
        threading.Thread(target=self._fetch_products).start()
    
    def _fetch_products(self):
        """Thread para obtener productos."""
        result = self.api_service.get_products()
        Clock.schedule_once(lambda dt: self._display_products(result))
    
    def _display_products(self, result):
        """Mostrar productos en la UI."""
        self.product_list.clear_widgets()
        
        if 'error' in result:
            error_label = MDLabel(
                text=f"Error: {result['error']}",
                halign="center",
                theme_text_color="Error"
            )
            self.product_list.add_widget(error_label)
            return
        
        if isinstance(result, list):
            self.products = result
            
            if not self.products:
                no_products = MDLabel(
                    text='No hay productos disponibles',
                    halign="center",
                    theme_text_color="Secondary"
                )
                self.product_list.add_widget(no_products)
                return
            
            for product in self.products:
                card = self._create_product_card(product)
                self.product_list.add_widget(card)
        else:
            error_label = MDLabel(
                text='Error al cargar productos',
                halign="center",
                theme_text_color="Error"
            )
            self.product_list.add_widget(error_label)
    
    def _create_product_card(self, product):
        """Crear card para un producto."""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(200),
            padding=dp(10),
            spacing=dp(5),
            radius=[15],
            elevation=4,
            md_bg_color=(0.2, 0.2, 0.2, 1)
        )
        
        # Título
        title = MDLabel(
            text=product.get('title', 'Sin título'),
            bold=True,
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            font_style='H6',
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title)
        
        # Descripción
        desc_text = product.get('description', '')
        if len(desc_text) > 80:
            desc_text = desc_text[:80] + '...'
            
        description = MDLabel(
            text=desc_text,
            theme_text_color='Secondary',
            font_style='Body2',
            size_hint_y=None,
            height=dp(40)
        )
        card.add_widget(description)
        
        # Espacio flexible
        card.add_widget(MDLabel(size_hint_y=1))
        
        # Precio y botón
        bottom = MDBoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        price_text = f"${product.get('price', 0)}"
        if product.get('discount_price'):
            price_text = f"${product.get('discount_price')}"
        
        price = MDLabel(
            text=price_text,
            theme_text_color='Custom',
            text_color=(0, 1, 0, 1), # Verde para precio
            bold=True,
            font_style='H5',
            halign='left'
        )
        bottom.add_widget(price)
        
        view_btn = MDRaisedButton(
            text='VER DETALLE',
            md_bg_color=(0.8, 0, 0, 1), # Rojo
            on_press=lambda x: self.view_product_detail(product)
        )
        bottom.add_widget(view_btn)
        
        card.add_widget(bottom)
        
        return card
    
    def view_product_detail(self, product):
        """Navegar al detalle del producto."""
        detail_screen = self.manager.get_screen('product_detail')
        detail_screen.set_product(product)
        self.manager.current = 'product_detail'
