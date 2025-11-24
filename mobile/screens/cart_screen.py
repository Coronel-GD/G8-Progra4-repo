"""Pantalla de carrito de compras con estilo Kickboxing."""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDRectangleFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.metrics import dp
import threading
import webbrowser

class CartScreen(MDScreen):
    """Pantalla que muestra el carrito de compras."""
    
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        self.cart_data = None
        
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
        
        title = MDLabel(
            text='MI CARRITO',
            font_style='H6',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            bold=True
        )
        header.add_widget(title)
        
        self.main_layout.add_widget(header)
        
        # ScrollView para items
        self.scroll_view = MDScrollView(size_hint=(1, 1))
        self.cart_list = MDGridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10),
            adaptive_height=True
        )
        self.scroll_view.add_widget(self.cart_list)
        self.main_layout.add_widget(self.scroll_view)
        
        # Footer con total y checkout
        self.footer = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(120),
            padding=dp(10),
            spacing=dp(10),
            md_bg_color=(0.15, 0.15, 0.15, 1)
        )
        
        self.total_label = MDLabel(
            text='Total: $0',
            font_style='H5',
            bold=True,
            theme_text_color='Custom',
            text_color=(0, 1, 0, 1),
            halign='right'
        )
        self.footer.add_widget(self.total_label)
        
        self.checkout_button = MDRaisedButton(
            text='PAGAR CON MERCADOPAGO',
            size_hint_x=1,
            height=dp(50),
            md_bg_color=(0, 0.7, 0.9, 1), # Azul MercadoPago
            disabled=True
        )
        self.checkout_button.bind(on_press=self.process_checkout)
        self.footer.add_widget(self.checkout_button)
        
        self.main_layout.add_widget(self.footer)
        
        # Mensaje de status
        self.status_label = MDLabel(
            text='',
            halign='center',
            theme_text_color='Error',
            size_hint_y=None,
            height=dp(30)
        )
        self.main_layout.add_widget(self.status_label)
        
        self.add_widget(self.main_layout)
    
    def on_pre_enter(self):
        """Llamado antes de entrar a la pantalla."""
        if not self.auth_manager.is_authenticated():
            self.manager.current = 'login'
            return
        
        self.load_cart()
    
    def load_cart(self, instance=None):
        """Cargar carrito desde la API."""
        self.cart_list.clear_widgets()
        self.checkout_button.disabled = True
        
        loading = MDLabel(
            text="Cargando carrito...",
            halign="center",
            theme_text_color="Secondary"
        )
        self.cart_list.add_widget(loading)
        
        threading.Thread(target=self._fetch_cart).start()
    
    def _fetch_cart(self):
        """Thread para obtener carrito."""
        result = self.api_service.get_cart_summary()
        Clock.schedule_once(lambda dt: self._display_cart(result))
    
    def _display_cart(self, result):
        """Mostrar carrito en la UI."""
        self.cart_list.clear_widgets()
        
        if 'error' in result:
            error_label = MDLabel(
                text=f"Error: {result['error']}",
                halign="center",
                theme_text_color="Error"
            )
            self.cart_list.add_widget(error_label)
            return
        
        if result is None or not result.get('order_items'):
            empty_label = MDLabel(
                text='Tu carrito está vacío\n\n¡Agrega algunos productos!',
                halign="center",
                theme_text_color="Secondary"
            )
            self.cart_list.add_widget(empty_label)
            self.total_label.text = 'Total: $0'
            return
        
        self.cart_data = result
        
        for item_data in result.get('order_items', []):
            card = self._create_cart_item_card(item_data)
            self.cart_list.add_widget(card)
        
        total = result.get('total', 0)
        self.total_label.text = f'Total: ${total}'
        
        if result.get('order_items'):
            self.checkout_button.disabled = False
    
    def _create_cart_item_card(self, item_data):
        """Crear card para un item del carrito."""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(160),
            padding=dp(10),
            spacing=dp(5),
            radius=[10],
            elevation=2,
            md_bg_color=(0.2, 0.2, 0.2, 1)
        )
        
        item = item_data.get('item', {})
        quantity = item_data.get('quantity', 1)
        final_price = item_data.get('final_price', 0)
        slug = item.get('slug')
        
        # Título
        title = MDLabel(
            text=item.get('title', 'Sin título'),
            bold=True,
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title)
        
        # Info
        info_layout = MDBoxLayout(size_hint_y=None, height=dp(30))
        
        qty_label = MDLabel(
            text=f'Cant: {quantity}',
            theme_text_color='Secondary'
        )
        info_layout.add_widget(qty_label)
        
        price_label = MDLabel(
            text=f'${final_price}',
            theme_text_color='Custom',
            text_color=(0, 1, 0, 1),
            bold=True,
            halign='right'
        )
        info_layout.add_widget(price_label)
        
        card.add_widget(info_layout)
        
        # Botones de acción
        actions = MDBoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # -1
        minus_btn = MDIconButton(
            icon="minus",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_press=lambda x: self.remove_single_item(slug)
        )
        actions.add_widget(minus_btn)
        
        # +1
        plus_btn = MDIconButton(
            icon="plus",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_press=lambda x: self.add_item(slug)
        )
        actions.add_widget(plus_btn)
        
        # Espaciador
        actions.add_widget(MDLabel(size_hint_x=1))
        
        # Eliminar
        delete_btn = MDIconButton(
            icon="trash-can",
            theme_text_color="Custom",
            text_color=(1, 0.3, 0.3, 1),
            on_press=lambda x: self.remove_item(slug)
        )
        actions.add_widget(delete_btn)
        
        card.add_widget(actions)
        
        return card
    
    def add_item(self, slug):
        """Agregar una unidad."""
        self.status_label.text = 'Actualizando...'
        threading.Thread(target=self._add_item_thread, args=(slug,)).start()
    
    def _add_item_thread(self, slug):
        """Thread para agregar item."""
        result = self.api_service.add_to_cart(slug)
        Clock.schedule_once(lambda dt: self._handle_modify_result(result))
    
    def remove_single_item(self, slug):
        """Quitar una unidad."""
        self.status_label.text = 'Actualizando...'
        threading.Thread(target=self._remove_single_thread, args=(slug,)).start()
    
    def _remove_single_thread(self, slug):
        """Thread para quitar una unidad."""
        result = self.api_service.remove_single_item_from_cart(slug)
        Clock.schedule_once(lambda dt: self._handle_modify_result(result))
    
    def remove_item(self, slug):
        """Eliminar item."""
        self.status_label.text = 'Eliminando...'
        threading.Thread(target=self._remove_item_thread, args=(slug,)).start()
    
    def _remove_item_thread(self, slug):
        """Thread para eliminar item."""
        result = self.api_service.remove_from_cart(slug)
        Clock.schedule_once(lambda dt: self._handle_modify_result(result))
    
    def _handle_modify_result(self, result):
        """Manejar resultado de modificar carrito."""
        if 'error' in result:
            self.status_label.text = f"Error: {result['error']}"
            self.status_label.theme_text_color = 'Error'
        else:
            self.status_label.text = 'Carrito actualizado'
            self.status_label.theme_text_color = 'Custom'
            self.status_label.text_color = (0, 1, 0, 1)
            Clock.schedule_once(lambda dt: self.load_cart(), 0.5)
    
    def process_checkout(self, instance):
        """Procesar el checkout."""
        self.status_label.text = 'Procesando checkout...'
        self.status_label.theme_text_color = 'Primary'
        self.checkout_button.disabled = True
        
        threading.Thread(target=self._checkout_thread).start()
    
    def _checkout_thread(self):
        """Thread para checkout."""
        result = self.api_service.checkout()
        Clock.schedule_once(lambda dt: self._handle_checkout_result(result))
    
    def _handle_checkout_result(self, result):
        """Manejar resultado del checkout."""
        self.checkout_button.disabled = False
        
        if 'error' in result:
            self.status_label.text = f"Error: {result['error']}"
            self.status_label.theme_text_color = 'Error'
        elif 'sandbox_init_point' in result or 'init_point' in result:
            payment_url = result.get('sandbox_init_point') or result.get('init_point')
            
            self.status_label.text = 'Abriendo MercadoPago...'
            self.status_label.theme_text_color = 'Custom'
            self.status_label.text_color = (0, 1, 0, 1)
            
            webbrowser.open(payment_url)
            
            Clock.schedule_once(
                lambda dt: setattr(self.status_label, 'text', 
                                 'Completa el pago en tu navegador'),
                2
            )
        else:
            self.status_label.text = 'Error al crear el pago'
            self.status_label.theme_text_color = 'Error'
