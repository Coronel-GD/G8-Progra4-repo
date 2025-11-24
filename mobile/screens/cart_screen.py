"""Pantalla de carrito de compras."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import threading
import webbrowser


class CartScreen(Screen):
    """Pantalla que muestra el carrito de compras."""
    
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        self.cart_data = None
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint=(1, None), height=60, spacing=10)
        
        back_btn = Button(text='← Volver', size_hint=(0.3, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'products'))
        header.add_widget(back_btn)
        
        title = Label(
            text='🛒 Mi Carrito',
            font_size='20sp',
            bold=True,
            size_hint=(0.7, 1)
        )
        header.add_widget(title)
        
        main_layout.add_widget(header)
        
        # Botón recargar
        self.refresh_button = Button(
            text='🔄 Actualizar Carrito',
            size_hint=(1, None),
            height=50
        )
        self.refresh_button.bind(on_press=self.load_cart)
        main_layout.add_widget(self.refresh_button)
        
        # Área de items (ScrollView)
        self.scroll_view = ScrollView(size_hint=(1, 0.7))
        self.cart_list = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5
        )
        self.cart_list.bind(minimum_height=self.cart_list.setter('height'))
        self.scroll_view.add_widget(self.cart_list)
        main_layout.add_widget(self.scroll_view)
        
        # Total y checkout
        self.total_label = Label(
            text='Total: $0',
            font_size='18sp',
            bold=True,
            size_hint=(1, None),
            height=40
        )
        main_layout.add_widget(self.total_label)
        
        self.checkout_button = Button(
            text='💳 Pagar con MercadoPago',
            size_hint=(1, None),
            height=60,
            background_color=(0.2, 0.8, 0.2, 1),
            disabled=True
        )
        self.checkout_button.bind(on_press=self.process_checkout)
        main_layout.add_widget(self.checkout_button)
        
        # Mensaje de status
        self.status_label = Label(
            text='',
            size_hint=(1, None),
            height=40
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def on_pre_enter(self):
        """Llamado antes de entrar a la pantalla."""
        if not self.auth_manager.is_authenticated():
            self.manager.current = 'login'
            return
        
        self.load_cart()
    
    def load_cart(self, instance=None):
        """Cargar carrito desde la API."""
        self.refresh_button.text = 'Cargando...'
        self.refresh_button.disabled = True
        self.cart_list.clear_widgets()
        self.checkout_button.disabled = True
        
        threading.Thread(target=self._fetch_cart).start()
    
    def _fetch_cart(self):
        """Thread para obtener carrito."""
        result = self.api_service.get_cart_summary()
        Clock.schedule_once(lambda dt: self._display_cart(result))
    
    def _display_cart(self, result):
        """Mostrar carrito en la UI."""
        self.refresh_button.text = '🔄 Actualizar'
        self.refresh_button.disabled = False
        
        if 'error' in result:
            error_label = Label(
                text=f"❌ {result['error']}",
                size_hint_y=None,
                height=100,
                color=(1, 0, 0, 1)
            )
            self.cart_list.add_widget(error_label)
            return
        
        # Si el carrito está vacío
        if result is None or not result.get('order_items'):
            empty_label = Label(
                text='Tu carrito está vacío\n\n¡Agrega algunos productos!',
                size_hint_y=None,
                height=150
            )
            self.cart_list.add_widget(empty_label)
            self.total_label.text = 'Total: $0'
            return
        
        self.cart_data = result
        
        # Mostrar items
        for item_data in result.get('order_items', []):
            card = self._create_cart_item_card(item_data)
            self.cart_list.add_widget(card)
        
        # Actualizar total
        total = result.get('total', 0)
        self.total_label.text = f'Total: ${total}'
        
        # Habilitar checkout si hay items
        if result.get('order_items'):
            self.checkout_button.disabled = False
    
    def _create_cart_item_card(self, item_data):
        """Crear card para un item del carrito."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=150,
            padding=10
        )
        
        item = item_data.get('item', {})
        quantity = item_data.get('quantity', 1)
        final_price = item_data.get('final_price', 0)
        slug = item.get('slug')
        
        # Título
        title = Label(
            text=item.get('title', 'Sin título'),
            bold=True,
            size_hint_y=0.3,
            font_size='14sp'
        )
        card.add_widget(title)
        
        # Cantidad y precio
        info = BoxLayout(size_hint_y=0.3)
        
        quantity_label = Label(
            text=f'Cantidad: {quantity}',
            size_hint=(0.5, 1)
        )
        info.add_widget(quantity_label)
        
        price_label = Label(
            text=f'${final_price}',
            bold=True,
            color=(0, 1, 0, 1),
            size_hint=(0.5, 1)
        )
        info.add_widget(price_label)
        
        card.add_widget(info)
        
        # Precio unitario
        unit_price = Label(
            text=f'Precio unit: ${item.get("price", 0)}',
            size_hint_y=0.2,
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        card.add_widget(unit_price)
        
        # Botones de acción
        buttons = BoxLayout(size_hint_y=0.2, spacing=5)
        
        # Botón -1
        minus_btn = Button(text='-1', size_hint=(0.25, 1))
        minus_btn.bind(on_press=lambda x: self.remove_single_item(slug))
        buttons.add_widget(minus_btn)
        
        # Botón +1
        plus_btn = Button(text='+1', size_hint=(0.25, 1))
        plus_btn.bind(on_press=lambda x: self.add_item(slug))
        buttons.add_widget(plus_btn)
        
        # Botón Eliminar
        delete_btn = Button(
            text='Eliminar',
            size_hint=(0.5, 1),
            background_color=(1, 0.3, 0.3, 1)
        )
        delete_btn.bind(on_press=lambda x: self.remove_item(slug))
        buttons.add_widget(delete_btn)
        
        card.add_widget(buttons)
        
        return card
    
    def add_item(self, slug):
        """Agregar una unidad del producto."""
        self.status_label.text = 'Agregando...'
        threading.Thread(target=self._add_item_thread, args=(slug,)).start()
    
    def _add_item_thread(self, slug):
        """Thread para agregar item."""
        result = self.api_service.add_to_cart(slug)
        Clock.schedule_once(lambda dt: self._handle_modify_result(result))
    
    def remove_single_item(self, slug):
        """Quitar una unidad del producto."""
        self.status_label.text = 'Quitando...'
        threading.Thread(target=self._remove_single_thread, args=(slug,)).start()
    
    def _remove_single_thread(self, slug):
        """Thread para quitar una unidad."""
        result = self.api_service.remove_single_item_from_cart(slug)
        Clock.schedule_once(lambda dt: self._handle_modify_result(result))
    
    def remove_item(self, slug):
        """Eliminar completamente el producto."""
        self.status_label.text = 'Eliminando...'
        threading.Thread(target=self._remove_item_thread, args=(slug,)).start()
    
    def _remove_item_thread(self, slug):
        """Thread para eliminar item."""
        result = self.api_service.remove_from_cart(slug)
        Clock.schedule_once(lambda dt: self._handle_modify_result(result))
    
    def _handle_modify_result(self, result):
        """Manejar resultado de modificar carrito."""
        if 'error' in result:
            self.status_label.text = f"❌ {result['error']}"
            self.status_label.color = (1, 0, 0, 1)
        else:
            self.status_label.text = '✅ Carrito actualizado'
            self.status_label.color = (0, 1, 0, 1)
            # Recargar el carrito automáticamente
            Clock.schedule_once(lambda dt: self.load_cart(), 0.5)
    
    def process_checkout(self, instance):
        """Procesar el checkout."""
        self.status_label.text = 'Procesando checkout...'
        self.status_label.color = (0, 0, 1, 1)
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
            self.status_label.text = f"❌ {result['error']}"
            self.status_label.color = (1, 0, 0, 1)
        elif 'sandbox_init_point' in result or 'init_point' in result:
            # Obtener URL de pago
            payment_url = result.get('sandbox_init_point') or result.get('init_point')
            
            self.status_label.text = '✅ Abriendo MercadoPago...'
            self.status_label.color = (0, 1, 0, 1)
            
            # Abrir en el navegador
            webbrowser.open(payment_url)
            
            # Actualizar mensaje después de 2 segundos
            Clock.schedule_once(
                lambda dt: setattr(self.status_label, 'text', 
                                 'Completa el pago en tu navegador'),
                2
            )
        else:
            self.status_label.text = 'Error al crear el pago'
            self.status_label.color = (1, 0, 0, 1)
