"""Pantalla de login con estilo Kickboxing."""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.uix.image import Image
import threading
import webbrowser

class LoginScreen(MDScreen):
    """Pantalla de login con username y password."""
    
    def __init__(self, api_service, auth_manager, **kwargs):
        super().__init__(**kwargs)
        self.api_service = api_service
        self.auth_manager = auth_manager
        
        # Layout principal
        layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            md_bg_color=(0.1, 0.1, 0.1, 1)  # Fondo oscuro
        )
        
        # Espaciador superior
        layout.add_widget(MDLabel(size_hint_y=0.1))
        
        # Título / Logo
        title_box = MDBoxLayout(orientation='vertical', size_hint_y=0.2, spacing=5)
        title = MDLabel(
            text='KICKBOXING SHOP',
            halign='center',
            theme_text_color='Custom',
            text_color=(1, 0, 0, 1), # Rojo intenso
            font_style='H4',
            bold=True
        )
        subtitle = MDLabel(
            text='Entrena como un campeón',
            halign='center',
            theme_text_color='Secondary',
            font_style='Subtitle1'
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)
        layout.add_widget(title_box)
        
        # Card de Login
        card = MDCard(
            orientation='vertical',
            size_hint=(0.9, None),
            height=400,
            pos_hint={'center_x': 0.5},
            padding=20,
            spacing=15,
            elevation=4,
            radius=[10]
        )
        
        # Username
        self.username_input = MDTextField(
            hint_text="Usuario",
            icon_right="account",
            mode="rectangle",
            size_hint_x=1
        )
        card.add_widget(self.username_input)
        
        # Password
        self.password_input = MDTextField(
            hint_text="Contraseña",
            icon_right="key",
            password=True,
            mode="rectangle",
            size_hint_x=1
        )
        card.add_widget(self.password_input)
        
        # Mensaje de status
        self.status_label = MDLabel(
            text='',
            halign='center',
            theme_text_color='Error',
            size_hint_y=None,
            height=30
        )
        card.add_widget(self.status_label)
        
        # Botón de login
        self.login_button = MDRaisedButton(
            text='INICIAR SESIÓN',
            size_hint_x=1,
            md_bg_color=(0.8, 0, 0, 1), # Rojo
            elevation=2
        )
        self.login_button.bind(on_press=self.do_login)
        card.add_widget(self.login_button)
        
        # Separador
        card.add_widget(MDLabel(
            text='- O -',
            halign='center',
            theme_text_color='Hint',
            size_hint_y=None,
            height=30
        ))
        
        # Botones sociales
        social_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint=(1, None),
            height=50,
            adaptive_width=True,
            pos_hint={'center_x': 0.5}
        )
        
        google_btn = MDRectangleFlatButton(
            text='Google',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            line_color=(0.8, 0.2, 0.2, 1)
        )
        google_btn.bind(on_press=self.login_with_google)
        social_layout.add_widget(google_btn)
        
        github_btn = MDRectangleFlatButton(
            text='GitHub',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            line_color=(0.5, 0.5, 0.5, 1)
        )
        github_btn.bind(on_press=self.login_with_github)
        social_layout.add_widget(github_btn)
        
        card.add_widget(social_layout)
        
        layout.add_widget(card)
        
        # Botón continuar sin login
        skip_btn = MDRectangleFlatButton(
            text='Continuar como invitado',
            pos_hint={'center_x': 0.5},
            theme_text_color="Custom",
            text_color=(0.7, 0.7, 0.7, 1),
            line_color=(0, 0, 0, 0)
        )
        skip_btn.bind(on_press=self.skip_login)
        layout.add_widget(skip_btn)
        
        # Espaciador inferior
        layout.add_widget(MDLabel(size_hint_y=0.1))
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        """Realizar login."""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.status_label.text = 'Por favor complete todos los campos'
            return
        
        self.status_label.text = 'Iniciando sesión...'
        self.status_label.theme_text_color = 'Primary'
        self.login_button.disabled = True
        
        # Hacer login en un hilo separado
        threading.Thread(target=self._login_thread, args=(username, password)).start()
    
    def _login_thread(self, username, password):
        """Thread para hacer login."""
        result = self.api_service.login(username, password)
        Clock.schedule_once(lambda dt: self._handle_login_result(result, username))
    
    def _handle_login_result(self, result, username):
        """Manejar resultado del login."""
        self.login_button.disabled = False
        
        if 'error' in result:
            self.status_label.text = f"Error: {result['error']}"
            self.status_label.theme_text_color = 'Error'
        elif 'access' in result:
            self.auth_manager.save_tokens(
                result['access'],
                result['refresh'],
                username
            )
            self.status_label.text = 'Login exitoso!'
            self.status_label.theme_text_color = 'Custom'
            self.status_label.text_color = (0, 1, 0, 1)
            
            Clock.schedule_once(lambda dt: self.go_to_products(), 1)
        else:
            self.status_label.text = 'Error: Credenciales inválidas'
            self.status_label.theme_text_color = 'Error'
    
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
        self.status_label.text = 'Abriendo Google...'
        self.status_label.theme_text_color = 'Primary'
        Clock.schedule_once(lambda dt: self._show_social_login_info(), 2)
    
    def login_with_github(self, instance):
        """Abrir navegador para login con GitHub."""
        url = "http://127.0.0.1:8000/accounts/github/login/"
        webbrowser.open(url)
        self.status_label.text = 'Abriendo GitHub...'
        self.status_label.theme_text_color = 'Primary'
        Clock.schedule_once(lambda dt: self._show_social_login_info(), 2)
    
    def _show_social_login_info(self):
        """Mostrar información sobre login social."""
        self.status_label.text = 'Completa el login en tu navegador'
        self.status_label.theme_text_color = 'Primary'
