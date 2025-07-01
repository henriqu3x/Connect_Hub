from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from db.connection import db
import bcrypt

class SindicoLoginScreen(Screen):
    dialog = None

    def toggle_password_visibility_manual(self):
        senha_field = self.ids.senha
        eye_button = self.ids.eye_button

        senha_field.password = not senha_field.password
        eye_button.icon = "eye" if not senha_field.password else "eye-off"
    
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

        query = "SELECT * FROM usuarios WHERE email = %s AND tipo = 'Sindico'"
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


        from kivy.app import App
        app = App.get_running_app()
        if app:
            app.current_user_email = email

            if not hasattr(app, 'store'):
                from kivy.storage.jsonstore import JsonStore
                app.store = JsonStore('userstore.json')
            app.store.put('user', email=email)
            app.sindico_dashboard()

            self.ids.email.text = ''
            self.ids.senha.text = ''
        else:
            self.manager.current = 'sindico_dashboard'
            
    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()