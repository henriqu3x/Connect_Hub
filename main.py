from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from screens.seletor_login_screen import SeletorLoginScreen
from screens.sindico_login_screen import SindicoLoginScreen
from screens.morador_login_screen import MoradorLoginScreen
from screens.sindico_cadastro_screen import SindicoCadastroScreen
from screens.esqueci_minha_senha_screen import EsqueciMinhaSenhaScreeen
from screens.redefina_sua_senha_screen import RedefinaSuaSenhaScreen
from screens.dashboard_morador_screen import DashboardMoradorScreen
from screens.dashboard_sindico_screen import DashboardSindicoScreen
from screens.dashboard_morador_screen import RegistrarOcorrenciaModal
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import bcrypt
from db.connection import db
from kivy.storage.jsonstore import JsonStore
import os
import sys
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivymd.uix.fitimage import FitImage
from kivy.uix.modalview import ModalView
from kivy.graphics import Line, Color
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton, MDTextButton, MDRaisedButton, MDFlatButton, MDRoundFlatButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

Window.maximize()

class MyApp(MDApp):
    def build(self):
        previous_screen = "seletor"
        previous_screen_redefinir_senha = 'seletor'
        previous_screen_morador_dashboard = 'seletor'
        previous_screen_sindico_dashboard = 'seletor'
        self.theme_cls.primary_palette = "DeepPurple"
        Builder.load_file(resource_path("screens/seletor_login.kv"))
        Builder.load_file(resource_path("screens/sindico_login.kv"))
        Builder.load_file(resource_path("screens/morador_login.kv"))
        Builder.load_file(resource_path("screens/sindico_cadastro.kv"))
        Builder.load_file(resource_path("screens/esqueci_senha.kv"))
        Builder.load_file(resource_path('screens/redefina_senha.kv'))
        Builder.load_file(resource_path('screens/dashboard_morador.kv'))
        Builder.load_file(resource_path('screens/dashboard_sindico.kv'))

        self.store = JsonStore('userstore.json')

        sm = ScreenManager()
        sm.add_widget(SeletorLoginScreen(name='seletor'))
        sm.add_widget(SindicoLoginScreen(name='sindico_login'))
        sm.add_widget(MoradorLoginScreen(name='morador_login'))
        sm.add_widget(SindicoCadastroScreen(name='sindico_cadastro'))
        sm.add_widget(EsqueciMinhaSenhaScreeen(name='esqueci_senha'))
        sm.add_widget(RedefinaSuaSenhaScreen(name='redefinir_senha'))
        sm.add_widget(DashboardMoradorScreen(name='morador_dashboard'))
        sm.add_widget(DashboardSindicoScreen(name='sindico_dashboard'))

        def reset_button_colors(dt):
            tela_cadastro = sm.get_screen('sindico_cadastro')
            tela_esqueci_senha = sm.get_screen('esqueci_senha')
            tela_redefinir_senha = sm.get_screen('redefinir_senha')
            btn1 = tela_cadastro.ids.btn_cadastrar
            btn2 = tela_cadastro.ids.btn_entrar
            btn3 = tela_esqueci_senha.ids.btn_recuperar
            btn4 = tela_redefinir_senha.ids.btn_redefinir
            btn1.reset_color()
            btn2.reset_color()
            btn3.reset_color()
            btn4.reset_color()
            
        Clock.schedule_once(reset_button_colors, 0)


        if self.store.exists('user'):
            user_email = self.store.get('user')['email']
            self.current_user_email = user_email
    
            query = "SELECT tipo FROM usuarios WHERE email = %s"
            result = db.execute_query(query, (user_email,))
            if result and len(result) > 0:
                user_type = result[0]['tipo'].lower()
                if user_type == 'morador':
                    sm.get_screen('morador_dashboard').set_user(user_email)
                    sm.current = 'morador_dashboard'
                elif user_type == 'sindico':
                    sm.get_screen('sindico_dashboard').set_user(user_email)
                    sm.current = 'sindico_dashboard'
                else:
                    sm.current = 'seletor'
            else:
                sm.current = 'seletor'
        else:
            sm.current = 'seletor'

        return sm

    def resource_path(self, rel_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, rel_path)



            

        
    
    def logout(self):
        if hasattr(self, 'current_user_email'):
            self.current_user_email = None
            if self.store.exists('user'):
                self.store.delete('user')

        if self.root:
            try:
                dashboard_screen = self.root.get_screen('morador_dashboard')
                dashboard_screen.new_notifications_count = 0
            except Exception:
                pass

        self.dialog = MDDialog(
            text="Você foi deslogado com sucesso.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=self.fechar_dialog_voltar_login
                ),
            ],
        )
        self.dialog.open()

    def fechar_dialog_voltar_login(self, *args):
        self.dialog.dismiss()
        self.root.current = 'seletor'

    def on_sindico(self):
        self.root.current = 'sindico_login'

    def on_morador(self):
        self.root.current = 'morador_login'

    def cadastro_sindico(self):
        self.root.current = 'sindico_cadastro'

    def esqueci_senha(self):
        self.previous_screen = self.root.current  
        self.root.current = 'esqueci_senha'
    
    def redefinir_senha(self):
        self.previous_screen_redefinir_senha = self.root.current 
        self.root.current = 'redefinir_senha'
        
    def morador_dashboard(self):
        self.previous_screen_morador_dashboard = self.root.current 

        dashboard_screen = self.root.get_screen('morador_dashboard')

        if hasattr(self, 'current_user_email') and self.current_user_email:
            dashboard_screen.set_user(self.current_user_email)
        self.root.current = 'morador_dashboard'
    
    def sindico_dashboard(self):
        self.previous_screen_sindico_dashboard = self.root.current 

        dashboard_screen = self.root.get_screen('sindico_dashboard')
        if hasattr(self, 'current_user_email') and self.current_user_email:
            dashboard_screen.set_user(self.current_user_email)
        self.root.current = 'sindico_dashboard'

    def enviar_codigo_recuperacao(self):

        email = self.root.get_screen('esqueci_senha').ids.email_input.text.strip()
        if not email:
            self.dialog = MDDialog(
                text="Por favor, insira um email válido.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            # Clear input after failure
            self.root.get_screen('esqueci_senha').ids.email_input.text = ''
            return


        query = "SELECT * FROM usuarios WHERE email = %s"
        result = db.execute_query(query, (email,))
        if not result:
            self.dialog = MDDialog(
                text="Email não cadastrado.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            # Clear input after failure
            self.root.get_screen('esqueci_senha').ids.email_input.text = ''
            return


        codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.codigo_recuperacao = codigo
        self.email_recuperacao = email


        remetente = "sistema.connecthub@gmail.com"
        senha = "wczn nyei bgkv tyux"  

        destinatario = email

        mensagem = MIMEMultipart()
        mensagem["From"] = "ConnectHub Condominio <sistema.connecthub@gmail.com>"
        mensagem["To"] = destinatario
        mensagem["Subject"] = "Código de recuperação de senha"

        corpo = f"Seu código de recuperação de senha é: {codigo}"
        mensagem.attach(MIMEText(corpo, "plain"))

        try:
            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()
            servidor.login(remetente, senha)
            servidor.sendmail(remetente, destinatario, mensagem.as_string())
            servidor.quit()

            self.dialog = MDDialog(
                text="Código enviado com sucesso para seu email.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()

    
            self.redefinir_senha()
    
            self.root.get_screen('esqueci_senha').ids.email_input.text = ''

        except Exception as e:
            self.dialog = MDDialog(
                text=f"Erro ao enviar e-mail: {str(e)}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()

    def enviar_ocorrencia(self):

        dashboard_screen = self.root.get_screen('morador_dashboard')

        modal = None

        if hasattr(dashboard_screen, 'registrar_ocorrencia_modal'):
            modal = dashboard_screen.registrar_ocorrencia_modal
        else:
            from screens.dashboard_morador_screen import RegistrarOcorrenciaModal
            modal = RegistrarOcorrenciaModal()
            dashboard_screen.registrar_ocorrencia_modal = modal


        if dashboard_screen.user_email:
            success = modal.salvar_ocorrencia(dashboard_screen.user_email)
            if success:
        
                dashboard_screen.load_ocorrencias()
                dashboard_screen.update_ui()
                modal.dismiss()
        else:
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.button import MDFlatButton
            dialog = MDDialog(
                text="Usuário não autenticado.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()

    def redefinir_senha_usuario(self):
        screen = self.root.get_screen('redefinir_senha')
        codigo_input = screen.ids.codigo_input.text.strip() if 'codigo_input' in screen.ids else ''
        nova_senha = screen.ids.nova_senha_input.text.strip() if 'nova_senha_input' in screen.ids else ''
        repetir_senha = screen.ids.repetir_senha_input.text.strip() if 'repetir_senha_input' in screen.ids else ''

        if not codigo_input or not nova_senha or not repetir_senha:
            self.dialog = MDDialog(
                text="Por favor, preencha todos os campos.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return

        if codigo_input != getattr(self, 'codigo_recuperacao', None):
            self.dialog = MDDialog(
                text="Código inválido.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return

        if nova_senha != repetir_senha:
            self.dialog = MDDialog(
                text="As senhas não coincidem.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return

        hashed_password = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        query = """
            UPDATE usuarios
            SET senha = %s
            WHERE email = %s
        """
        result = db.execute_query(query, (hashed_password, getattr(self, 'email_recuperacao', None)))

        if result is None:
            self.dialog = MDDialog(
                text="Erro ao atualizar a senha no banco de dados.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return

        self.dialog = MDDialog(
            text="Senha atualizada com sucesso!",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()
        self.root.current = 'seletor'
        
    def enviar_reserva(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton


        dashboard_screen = self.root.get_screen('morador_dashboard')


        modal = getattr(dashboard_screen, 'reserva_area_modal', None)
        if not modal:
            self.dialog = MDDialog(
                text="Erro: Modal de reserva não encontrado.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return


        nome_area = modal.ids.nome_area.text.strip() if 'nome_area' in modal.ids else ''
        data_reserva = modal.ids.data_reserva.text.strip() if 'data_reserva' in modal.ids else ''
        data_fim_reserva = modal.ids.data_fim_reserva.text.strip() if 'data_fim_reserva' in modal.ids else ''
        horario_reserva = modal.ids.horario_reserva.text.strip() if 'horario_reserva' in modal.ids else ''
        observacoes = modal.ids.observacoes.text.strip() if 'observacoes' in modal.ids else ''


        if not nome_area or not data_reserva or not data_fim_reserva or not horario_reserva:
            self.dialog = MDDialog(
                text="Por favor, preencha todos os campos obrigatórios.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return


        from datetime import datetime
        try:
            data_inicio_obj = datetime.strptime(data_reserva, "%d/%m/%Y")
            data_fim_obj = datetime.strptime(data_fim_reserva, "%d/%m/%Y")
        except ValueError:
            self.dialog = MDDialog(
                text="Data inválida. Use o formato DD/MM/AAAA.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return

        try:

            query_morador_id = """
                SELECT usuarios_id FROM Morador WHERE usuarios_id = (
                    SELECT id FROM usuarios WHERE email = %s
                )
            """
            result = db.execute_query(query_morador_id, (dashboard_screen.user_email,))
            if not result:
                raise Exception("Morador não encontrado para o usuário.")

            morador_id = result[0]['usuarios_id']


            query_insert = """
                INSERT INTO Reserva (area, data_inicio, data_fim, horario, observacoes, morador_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            horario_parts = horario_reserva.split("às")
            if len(horario_parts) == 2:
                hora_inicio = horario_parts[0].strip()
                hora_fim = horario_parts[1].strip()
            else:
                hora_inicio = None
                hora_fim = None

    
            from datetime import datetime as dt
            if hora_inicio:
                data_inicio = dt.strptime(f"{data_reserva} {hora_inicio}", "%d/%m/%Y %H:%M")
            else:
                data_inicio = data_inicio_obj
            if hora_fim:
                data_fim = dt.strptime(f"{data_fim_reserva} {hora_fim}", "%d/%m/%Y %H:%M")
            else:
                data_fim = data_fim_obj

            db.execute_query(query_insert, (nome_area, data_inicio, data_fim, horario_reserva, observacoes, morador_id, 'pendente'))

    
            self.dialog = MDDialog(
                text="Reserva enviada com sucesso.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()

    
            modal.dismiss()

    
            dashboard_screen.load_reservas()
            dashboard_screen.update_ui()

        except Exception as e:
            self.dialog = MDDialog(
                text=f"Erro ao enviar reserva: {str(e)}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()

if __name__ == '__main__':
    MyApp().run()