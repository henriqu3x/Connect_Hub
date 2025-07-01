from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from db.connection import db
import bcrypt

class MoradorLoginScreen(Screen):
    dialog = None

    def toggle_password_visibility(self):
        senha_input = self.ids.senha
        eye_icon = self.ids.eye_icon

        if senha_input.password:
            senha_input.password = False
            eye_icon.icon = "eye"
        else:
            senha_input.password = True
            eye_icon.icon = "eye-off"

    def verificacao(self):
        email = self.ids.email.text.strip()
        senha = self.ids.senha.text.strip()

        if not email or not senha:
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Por favor, preencha todos os campos.",
                    buttons=[
                        MDFlatButton(
                            text="OK",
                            on_release=self.close_dialog
                        ),
                    ],
                )
            self.dialog.open()

            self.ids.email.text = ''
            self.ids.senha.text = ''
            return

        query = "SELECT * FROM usuarios WHERE email = %s AND tipo = 'Morador'"
        result = db.execute_query(query, (email,))
        if not result:
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Usuário não encontrado ou tipo incorreto.",
                    buttons=[
                        MDFlatButton(
                            text="OK",
                            on_release=self.close_dialog
                        ),
                    ],
                )
            self.dialog.open()

            self.ids.email.text = ''
            self.ids.senha.text = ''
            return

        user = result[0]
        hashed_password = user['senha'].encode('utf-8')
        if not bcrypt.checkpw(senha.encode('utf-8'), hashed_password):
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Senha incorreta.",
                    buttons=[
                        MDFlatButton(
                            text="OK",
                            on_release=self.close_dialog
                        ),
                    ],
                )
            self.dialog.open()

            self.ids.email.text = ''
            self.ids.senha.text = ''
            return

        print(f"Login realizado para o email: {email}")

        from kivy.app import App

        app = App.get_running_app()
        if app:
            app.current_user_email = email
            if not hasattr(app, 'store'):
                from kivy.storage.jsonstore import JsonStore
                app.store = JsonStore('userstore.json')
            app.store.put('user', email=email)
            app.morador_dashboard()

            self.ids.email.text = ''
            self.ids.senha.text = ''
        else:
            self.manager.current = 'morador_dashboard'

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()