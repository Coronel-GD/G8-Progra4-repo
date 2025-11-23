from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import requests
import threading

# URL del backend (localhost desde el emulador/PC)
# Si corres esto en PC local: http://127.0.0.1:8000
# Si corres en Android Emulator: http://10.0.2.2:8000
API_URL = "http://127.0.0.1:8000/api/products/"

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import requests
import threading

# URL del backend
API_URL = "http://127.0.0.1:8000/api/products/"

class MobileApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        self.header = Label(text="E-commerce App", size_hint=(1, 0.1), font_size='20sp', bold=True)
        self.main_layout.add_widget(self.header)
        
        # Area de contenido (Lista de productos)
        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.product_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.product_list.bind(minimum_height=self.product_list.setter('height'))
        self.scroll_view.add_widget(self.product_list)
        self.main_layout.add_widget(self.scroll_view)
        
        # Botón de recarga
        self.refresh_button = Button(text="Cargar Productos", size_hint=(1, 0.1))
        self.refresh_button.bind(on_press=self.load_products)
        self.main_layout.add_widget(self.refresh_button)
        
        return self.main_layout

    def load_products(self, instance):
        self.refresh_button.text = "Cargando..."
        self.product_list.clear_widgets()
        threading.Thread(target=self._fetch_products).start()

    def _fetch_products(self):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    products = data
                else:
                    products = data.get('results', [])
                
                self.update_ui_with_products(products)
            else:
                self.update_error(f"Error: {response.status_code}")
        except Exception as e:
            self.update_error(f"Error de conexión: {str(e)}")

    def update_ui_with_products(self, products):
        # Esta función debería llamarse idealmente con Clock.schedule_once en una app real compleja
        # pero para este prototipo lo haremos directo, si falla usaremos Clock
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._populate_list(products))

    def _populate_list(self, products):
        self.refresh_button.text = "Recargar Productos"
        if not products:
            self.product_list.add_widget(Label(text="No hay productos disponibles", size_hint_y=None, height=40))
            return

        for product in products:
            # Crear un "card" simple para cada producto
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=5)
            
            # Nombre
            name = product.get('title', 'Sin nombre')
            lbl_name = Label(text=name, bold=True, size_hint_y=0.6)
            card.add_widget(lbl_name)
            
            # Precio
            price = product.get('price', '0.00')
            lbl_price = Label(text=f"${price}", color=(0, 1, 0, 1), size_hint_y=0.4)
            card.add_widget(lbl_price)
            
            self.product_list.add_widget(card)

    def update_error(self, error_msg):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._show_error(error_msg))

    def _show_error(self, error_msg):
        self.refresh_button.text = "Reintentar"
        self.product_list.clear_widgets()
        self.product_list.add_widget(Label(text=error_msg, color=(1, 0, 0, 1)))

if __name__ == '__main__':
    MobileApp().run()
