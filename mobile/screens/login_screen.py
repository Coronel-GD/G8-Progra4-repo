"""Pantalla de login."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
import threading
import webbrowser


class LoginScreen(Screen):
    """Pantalla de login con username y password."""
    
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        
        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        title = Label(text='Iniciar Sesión', font_size='24sp', size_hint=(1, 0.15), bold=True)
        layout.add_widget(title)
        
        # Username
        layout.add_widget(Label(text='Usuario:', size_hint=(1, None), height=30))
        self.username_input = TextInput(
            multiline=False,
            size_hint=(1, None),
            height=40
        )
        layout.add_widget(self.username_input)
        
        # Password
        layout.add_widget(Label(text='Contraseña:', size_hint=(1, None), height=30))
        self.password_input = TextInput(
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=40
        )
        layout.add_widget(self.password_input)
        
        # Mensaje de status
        self.status_label = Label(
            text='',
            size_hint=(1, None),
            height=40,
            color=(1, 0, 0, 1)
        )
        layout.add_widget(self.status_label)
        
        # Botón de login tradicional
        self.login_button = Button(
            text='Iniciar Sesión',
            size_hint=(1, None),
            height=50
        )
        self.login_button.bind(on_press=self.do_login)
        layout.add_widget(self.login_button)
        
        # Separador "O"
        layout.add_widget(Label(
            text='━━━━━ O ━━━━━',
            size_hint=(1, None),
            height=30,
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        # Botones de login social
        social_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        
        google_btn = Button(
            text='🔐 Google',
            background_color=(0.85, 0.25, 0.25, 1)
        )
        google_btn.bind(on_press=self.login_with_google)
        social_layout.add_widget(google_btn)
        
        github_btn = Button(
            text='🔐 GitHub',
            background_color=(0.15, 0.15, 0.15, 1)
        )
        github_btn.bind(on_press=self.login_with_github)
        social_layout.add_widget(github_btn)
        
        layout.add_widget(social_layout)
        
        # Botón continuar sin login
        skip_button = Button(
            text='Continuar sin login',
            size_hint=(1, None),
            height=50,
            background_color=(0.3, 0.3, 0.3, 1)
        )
        skip_button.bind(on_press=self.skip_login)
        layout.add_widget(skip_button)
        
        # Espacio vacío
        layout.add_widget(Label(size_hint=(1, 0.3)))
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        """Realizar login."""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.status_label.text = 'Por favor complete todos los campos'
            return
        
        self.status_label.text = 'Iniciando sesión...'
        self.status_label.color = (0, 0, 1, 1)
        self.login_button.disabled = True
        
        # Hacer login en un hilo separado
        threading.Thread(target=self._login_thread, args=(username, password)).start()
    
    def _login_thread(self, username, password):
        """Thread para hacer login."""
        result = self.api_service.login(username, password)
        
        # Programar actualización de UI en el hilo principal
        Clock.schedule_once(lambda dt: self._handle_login_result(result, username))
    
    def _handle_login_result(self, result, username):
        """Manejar resultado del login."""
        self.login_button.disabled = False
        
        if 'error' in result:
            self.status_label.text = f"Error: {result['error']}"
            self.status_label.color = (1, 0, 0, 1)
        elif 'access' in result:
            # Guardar tokens
            self.auth_manager.save_tokens(
                result['access'],
                result['refresh'],
                username
            )
            self.status_label.text = 'Login exitoso!'
            self.status_label.color = (0, 1, 0, 1)
            
            # Navegar a productos después de 1 segundo
            Clock.schedule_once(lambda dt: self.go_to_products(), 1)
        else:
            self.status_label.text = 'Error: Credenciales inválidas'
            self.status_label.color = (1, 0, 0, 1)
    
    def go_to_products(self):
        """Navegar a la pantalla de productos."""
        self.manager.current = 'products'
    
    def skip_login(self, instance):
        """Continuar sin login (solo ver productos)."""
        self.go_to_products()
    
    def login_with_google(self, instance):
        """Abrir navegador para login con Google."""
        url = "http://127.0.0.1:8000/accounts/google/login/"
        webbrowser.open(url)
        
        self.status_label.text = '✅ Abriendo Google en el navegador...\nCompleta el login allí'
        self.status_label.color = (0, 0.7, 1, 1)
        
        # Mensaje informativo
        Clock.schedule_once(lambda dt: self._show_social_login_info(), 2)
    
    def login_with_github(self, instance):
        """Abrir navegador para login con GitHub."""
        url = "http://127.0.0.1:8000/accounts/github/login/"
        webbrowser.open(url)
        
        self.status_label.text = '✅ Abriendo GitHub en el navegador...\nCompleta el login allí'
        self.status_label.color = (0, 0.7, 1, 1)
        
        # Mensaje informativo
        Clock.schedule_once(lambda dt: self._show_social_login_info(), 2)
    
    def _show_social_login_info(self):
        """Mostrar información sobre login social."""
        self.status_label.text = (
            'Completa el login en tu navegador.\n'
            'Luego podrás usar la app normalmente.'
        )
        self.status_label.color = (0, 1, 0, 1)
