"""Pantalla de detalle de producto."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import threading


class ProductDetailScreen(Screen):
    """Pantalla que muestra el detalle de un producto."""
    
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        self.current_product = None
        
        # Layout principal con ScrollView
        main_layout = BoxLayout(orientation='vertical')
        
        scroll = ScrollView()
        self.content_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15,
            size_hint_y=None
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        scroll.add_widget(self.content_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def set_product(self, product):
        """
        Configurar el producto a mostrar.
        
        Args:
            product: Dict con los datos del producto
        """
        self.current_product = product
        self.display_product()
    
    def display_product(self):
        """Mostrar el producto en la pantalla."""
        self.content_layout.clear_widgets()
        
        if not self.current_product:
            self.content_layout.add_widget(
                Label(text='No hay producto seleccionado')
            )
            return
        
        p = self.current_product
        
        # Botón volver
        back_btn = Button(
            text='← Volver',
            size_hint=(1, None),
            height=50
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'products'))
        self.content_layout.add_widget(back_btn)
        
        # Título
        title = Label(
            text=p.get('title', 'Sin título'),
            font_size='24sp',
            bold=True,
            size_hint_y=None,
            height=60
        )
        self.content_layout.add_widget(title)
        
        # Categoría y etiqueta
        if p.get('category_display') or p.get('label_display'):
            info_line = f"📂 {p.get('category_display', 'N/A')}"
            if p.get('label_display'):
                info_line += f"  🏷️ {p.get('label_display')}"
            
            info = Label(
                text=info_line,
                size_hint_y=None,
                height=30,
                color=(0.7, 0.7, 0.7, 1)
            )
            self.content_layout.add_widget(info)
        
        # Precio
        price_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        if p.get('discount_price'):
            # Precio anterior tachado
            old_price = Label(
                text=f"${p.get('price')}",
                strikethrough=True,
                color=(0.5, 0.5, 0.5, 1),
                size_hint=(0.3, 1)
            )
            price_layout.add_widget(old_price)
            
            # Precio con descuento
            new_price = Label(
                text=f"${p.get('discount_price')}",
                font_size='22sp',
                bold=True,
                color=(0, 1, 0, 1),
                size_hint=(0.7, 1)
            )
            price_layout.add_widget(new_price)
        else:
            price = Label(
                text=f"${p.get('price')}",
                font_size='22sp',
                bold=True,
                color=(0, 1, 0, 1)
            )
            price_layout.add_widget(price)
        
        self.content_layout.add_widget(price_layout)
        
        # Descripción
        description = Label(
            text=p.get('description', 'Sin descripción disponible'),
            size_hint_y=None,
            text_size=(None, None)
        )
        description.bind(
            width=lambda *x: setattr(description, 'text_size', (description.width, None)),
            texture_size=lambda *x: setattr(description, 'height', description.texture_size[1])
        )
        self.content_layout.add_widget(description)
        
        # Espacio
        self.content_layout.add_widget(Label(size_hint_y=None, height=20))
        
        # Mensaje de status
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=40,
            color=(0, 1, 0, 1)
        )
        self.content_layout.add_widget(self.status_label)
        
        # Botón agregar al carrito
        if self.auth_manager.is_authenticated():
            self.add_to_cart_btn = Button(
                text='🛒 Agregar al Carrito',
                size_hint=(1, None),
                height=60,
                background_color=(0.2, 0.6, 1, 1)
            )
            self.add_to_cart_btn.bind(on_press=self.add_to_cart)
            self.content_layout.add_widget(self.add_to_cart_btn)
        else:
            login_info = Label(
                text='Inicia sesión para agregar al carrito',
                size_hint_y=None,
                height=60,
                color=(1, 0.5, 0, 1)
            )
            self.content_layout.add_widget(login_info)
            
            login_btn = Button(
                text='Iniciar Sesión',
                size_hint=(1, None),
                height=60
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
            self.status_label.color = (1, 0, 0, 1)
            return
        
        self.status_label.text = 'Agregando al carrito...'
        self.status_label.color = (0, 0, 1, 1)
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
            self.status_label.text = f"❌ {result['error']}"
            self.status_label.color = (1, 0, 0, 1)
        elif 'message' in result:
            self.status_label.text = f"✅ {result['message']}"
            self.status_label.color = (0, 1, 0, 1)
        else:
            self.status_label.text = 'Producto agregado'
            self.status_label.color = (0, 1, 0, 1)
