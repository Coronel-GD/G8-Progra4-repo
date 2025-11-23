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

class MobileApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.label = Label(text="Presiona el botón para conectar a la API", size_hint=(1, 0.8))
        self.layout.add_widget(self.label)
        
        self.button = Button(text="Probar Conexión", size_hint=(1, 0.2))
        self.button.bind(on_press=self.check_connection)
        self.layout.add_widget(self.button)
        
        return self.layout

    def check_connection(self, instance):
        self.label.text = "Conectando..."
        # Ejecutar en hilo separado para no bloquear UI
        threading.Thread(target=self._make_request).start()

    def _make_request(self):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.update_label(f"¡Conexión Exitosa!\nProductos encontrados: {count}")
            else:
                self.update_label(f"Error: {response.status_code}")
        except Exception as e:
            self.update_label(f"Error de conexión:\n{str(e)}")

    def update_label(self, text):
        # Actualizar UI desde el hilo principal podría requerir Clock.schedule_once
        # pero para este ejemplo simple suele funcionar o se puede ajustar
        self.label.text = text

if __name__ == '__main__':
    MobileApp().run()
