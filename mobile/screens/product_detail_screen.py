"""Pantalla de detalle de producto con estilo Kickboxing."""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDRectangleFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.metrics import dp
import threading

class ProductDetailScreen(MDScreen):
    """Pantalla que muestra el detalle de un producto."""
    
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        self.current_product = None
        
        # Layout principal
        self.main_layout = MDBoxLayout(
            orientation='vertical',
            md_bg_color=(0.1, 0.1, 0.1, 1)
        )
        
        # Header
        header = MDBoxLayout(
            size_hint=(1, None),
            height=dp(60),
            padding=[10, 0],
            spacing=10,
            md_bg_color=(0.15, 0.15, 0.15, 1)
        )
        
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_press=lambda x: setattr(self.manager, 'current', 'products')
        )
        header.add_widget(back_btn)
        
        header_title = MDLabel(
            text="DETALLE",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True
        )
        header.add_widget(header_title)
        
        self.main_layout.add_widget(header)
        
        # ScrollView
        self.scroll_view = MDScrollView(size_hint=(1, 1))
        
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            adaptive_height=True
        )
        
        self.scroll_view.add_widget(self.content_layout)
        self.main_layout.add_widget(self.scroll_view)
        
        self.add_widget(self.main_layout)
    
    def set_product(self, product):
        """Configurar el producto a mostrar."""
        self.current_product = product
        self.display_product()
    
    def display_product(self):
        """Mostrar el producto en la pantalla."""
        self.content_layout.clear_widgets()
        
        if not self.current_product:
            self.content_layout.add_widget(
                MDLabel(
                    text='No hay producto seleccionado',
                    halign='center',
                    theme_text_color='Secondary'
                )
            )
            return
        
        p = self.current_product
        
        # Título
        title = MDLabel(
            text=p.get('title', 'Sin título'),
            font_style='H5',
            bold=True,
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            adaptive_height=True
        )
        self.content_layout.add_widget(title)
        
        # Categoría y etiquetas
        if p.get('category_display') or p.get('label_display'):
            info_line = f"{p.get('category_display', 'N/A')}"
            if p.get('label_display'):
                info_line += f" • {p.get('label_display')}"
            
            info = MDLabel(
                text=info_line,
                theme_text_color='Secondary',
                font_style='Caption',
                size_hint_y=None,
                height=dp(20)
            )
            self.content_layout.add_widget(info)
        
        # Espaciador
        self.content_layout.add_widget(MDLabel(size_hint_y=None, height=dp(10)))
        
        # Precio
        price_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            adaptive_height=True
        )
        
        if p.get('discount_price'):
            # Precio anterior
            old_price = MDLabel(
                text=f"${p.get('price')}",
                theme_text_color='Secondary',
                font_style='Body1',
                strikethrough=True,
                size_hint_x=None,
                width=dp(80)
            )
            price_layout.add_widget(old_price)
            
            # Precio nuevo
            new_price = MDLabel(
                text=f"${p.get('discount_price')}",
                theme_text_color='Custom',
                text_color=(0, 1, 0, 1),
                font_style='H4',
                bold=True
            )
            price_layout.add_widget(new_price)
        else:
            price = MDLabel(
                text=f"${p.get('price')}",
                theme_text_color='Custom',
                text_color=(0, 1, 0, 1),
                font_style='H4',
                bold=True
            )
            price_layout.add_widget(price)
        
        self.content_layout.add_widget(price_layout)
        
        # Descripción
        description = MDLabel(
            text=p.get('description', 'Sin descripción disponible'),
            theme_text_color='Primary',
            font_style='Body1',
            size_hint_y=None,
            adaptive_height=True
        )
        self.content_layout.add_widget(description)
        
        # Espacio flexible
        self.content_layout.add_widget(MDLabel(size_hint_y=None, height=dp(20)))
        
        # Mensaje de status
        self.status_label = MDLabel(
            text='',
            halign='center',
            theme_text_color='Error',
            size_hint_y=None,
            height=dp(30)
        )
        self.content_layout.add_widget(self.status_label)
        
        # Botón agregar al carrito
        if self.auth_manager.is_authenticated():
            self.add_to_cart_btn = MDRaisedButton(
                text='AGREGAR AL CARRITO',
                size_hint_x=1,
                height=dp(50),
                md_bg_color=(0.8, 0, 0, 1),
                elevation=2
            )
            self.add_to_cart_btn.bind(on_press=self.add_to_cart)
            self.content_layout.add_widget(self.add_to_cart_btn)
        else:
            login_info = MDLabel(
                text='Inicia sesión para comprar',
                halign='center',
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(30)
            )
            self.content_layout.add_widget(login_info)
            
            login_btn = MDRectangleFlatButton(
                text='INICIAR SESIÓN',
                pos_hint={'center_x': 0.5},
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1),
                line_color=(1, 0, 0, 1)
            )
            login_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
            self.content_layout.add_widget(login_btn)
    
    def add_to_cart(self, instance):
        """Agregar producto al carrito."""
        if not self.current_product:
            return
        
        slug = self.current_product.get('slug')
        if not slug:
            self.status_label.text = 'Error: producto sin slug'
            return
        
        self.status_label.text = 'Agregando al carrito...'
        self.status_label.theme_text_color = 'Primary'
        self.add_to_cart_btn.disabled = True
        
        threading.Thread(target=self._add_to_cart_thread, args=(slug,)).start()
    
    def _add_to_cart_thread(self, slug):
        """Thread para agregar al carrito."""
        result = self.api_service.add_to_cart(slug)
        Clock.schedule_once(lambda dt: self._handle_cart_result(result))
    
    def _handle_cart_result(self, result):
        """Manejar resultado de agregar al carrito."""
        self.add_to_cart_btn.disabled = False
        
        if 'error' in result:
            self.status_label.text = f"Error: {result['error']}"
            self.status_label.theme_text_color = 'Error'
        elif 'message' in result:
            self.status_label.text = f"{result['message']}"
            self.status_label.theme_text_color = 'Custom'
            self.status_label.text_color = (0, 1, 0, 1)
        else:
            self.status_label.text = 'Producto agregado'
            self.status_label.theme_text_color = 'Custom'
            self.status_label.text_color = (0, 1, 0, 1)
