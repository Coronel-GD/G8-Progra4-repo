from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
from kivy.clock import Clock
import requests
import threading

from kivy.utils import platform

# URL del backend
# Si corres esto en PC local: http://127.0.0.1:8000
# Si corres en Android Emulator: http://10.0.2.2:8000
if platform == "android":
    API_URL = "http://10.0.2.2:8000/api/products/"
else:
    API_URL = "http://127.0.0.1:8000/api/products/"

class ProductCard(MDCard):
    def __init__(self, title, price, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(15)
        self.spacing = dp(10)
        self.radius = [15]
        self.elevation = 4
        self.ripple_behavior = True
        
        # Title
        self.add_widget(MDLabel(
            text=title,
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=0.6,
            bold=True
        ))
        
        # Price
        self.add_widget(MDLabel(
            text=f"${price}",
            theme_text_color="Secondary",
            font_style="Subtitle1",
            size_hint_y=0.4
        ))

class MobileApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Orange"
        self.theme_cls.theme_style = "Light"
        
        # Main Screen
        screen = MDScreen()
        
        # Main Layout
        main_layout = MDBoxLayout(orientation='vertical')
        
        # App Bar
        self.toolbar = MDTopAppBar(
            title="E-commerce App",
            elevation=4,
            pos_hint={"top": 1}
        )
        self.toolbar.right_action_items = [["reload", lambda x: self.load_products()]]
        main_layout.add_widget(self.toolbar)
        
        # Content Area
        self.scroll_view = MDScrollView()
        self.product_list = MDList(padding=dp(10), spacing=dp(10))
        self.scroll_view.add_widget(self.product_list)
        main_layout.add_widget(self.scroll_view)
        
        screen.add_widget(main_layout)
        
        # Load initial data
        self.load_products()
        
        return screen

    def load_products(self, instance=None):
        # Show loading state if possible, or just clear list
        self.product_list.clear_widgets()
        loading_label = MDLabel(
            text="Cargando productos...",
            halign="center",
            theme_text_color="Hint"
        )
        self.product_list.add_widget(loading_label)
        
        threading.Thread(target=self._fetch_products).start()

    def _fetch_products(self):
        try:
            response = requests.get(API_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    products = data
                else:
                    products = data.get('results', [])
                
                Clock.schedule_once(lambda dt: self.update_ui_with_products(products))
            else:
                Clock.schedule_once(lambda dt: self.show_error(f"Error del servidor: {response.status_code}"))
        except requests.exceptions.ConnectionError:
            Clock.schedule_once(lambda dt: self.show_error("No se pudo conectar al servidor.\nVerifique que el backend esté corriendo."))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Error inesperado: {str(e)}"))

    def update_ui_with_products(self, products):
        self.product_list.clear_widgets()
        
        if not products:
            self.product_list.add_widget(MDLabel(
                text="No hay productos disponibles",
                halign="center",
                theme_text_color="Secondary"
            ))
            return

        for product in products:
            name = product.get('title', 'Sin nombre')
            price = product.get('price', '0.00')
            
            card = ProductCard(title=name, price=price)
            self.product_list.add_widget(card)

    def show_error(self, error_msg):
        self.product_list.clear_widgets()
        
        error_box = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=dp(20), size_hint_y=None, height=dp(200))
        
        lbl = MDLabel(
            text=error_msg,
            halign="center",
            theme_text_color="Error"
        )
        error_box.add_widget(lbl)
        
        btn = MDRaisedButton(
            text="Reintentar",
            pos_hint={"center_x": 0.5},
            on_release=self.load_products
        )
        error_box.add_widget(btn)
        
        self.product_list.add_widget(error_box)

if __name__ == '__main__':
    MobileApp().run()
