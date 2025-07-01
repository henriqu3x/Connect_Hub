from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.properties import BooleanProperty
from db.connection import db
import bcrypt
import re

class SindicoCadastroScreen(Screen):
    dialog = None
    senha_oculta = BooleanProperty(True)

    def toggle_visibilidade_senha(self):
        self.senha_oculta = not self.senha_oculta

    def verificar_campos(self):
        nome = self.ids.nome.text.strip()
        email = self.ids.email.text.strip()
        senha = self.ids.senha.text.strip()

        if not nome or not senha or not email:
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Por Favor, preencha todos os campos",
                    buttons=[
                        MDFlatButton(
                            text="Ok",
                            on_release=self.close_dialog
                        ),
                    ],
                )
            self.dialog.open()

            self.ids.nome.text = ''
            self.ids.email.text = ''
            self.ids.senha.text = ''
            return


        pattern = r'^[a-zA-Z0-9._%+-]+\.connect_hub\.sindico@gmail\.com$'
        if not re.match(pattern, email):
            if not self.dialog:
                self.dialog = MDDialog(
                    text="O e-mail deve estar no formato correto",
                    buttons=[
                        MDFlatButton(
                            text="Ok",
                            on_release=self.close_dialog
                        ),
                    ],
                )
            self.dialog.open()

            self.ids.nome.text = ''
            self.ids.email.text = ''
            self.ids.senha.text = ''
            return


        query_check = "SELECT * FROM usuarios WHERE email = %s"
        existing_user = db.execute_query(query_check, (email,))
        if existing_user:
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Este e-mail já está cadastrado.",
                    buttons=[
                        MDFlatButton(
                            text="Ok",
                            on_release=self.close_dialog
                        ),
                    ],
                )
            self.dialog.open()

            self.ids.nome.text = ''
            self.ids.email.text = ''
            self.ids.senha.text = ''
            return


        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


        query_insert = """
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (%s, %s, %s, 'Sindico')
            RETURNING id
        """
        result = db.execute_query(query_insert, (nome, email, hashed_password))
        if not result:
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Erro ao cadastrar usuário. Tente novamente.",
                    buttons=[
                        MDFlatButton(
                            text="Ok",
                            on_release=self.close_dialog
                        ),
                    ],
                )
            self.dialog.open()

            self.ids.nome.text = ''
            self.ids.email.text = ''
            self.ids.senha.text = ''
            return


        if isinstance(result, int):

            query_last_id = "SELECT id FROM usuarios WHERE email = %s"
            last_id_result = db.execute_query(query_last_id, (email,))
            if not last_id_result:
                if not self.dialog:
                    self.dialog = MDDialog(
                        text="Erro ao obter ID do usuário cadastrado.",
                        buttons=[
                            MDFlatButton(
                                text="Ok",
                                on_release=self.close_dialog
                            ),
                        ],
                    )
                self.dialog.open()

                self.ids.nome.text = ''
                self.ids.email.text = ''
                self.ids.senha.text = ''
                return
            usuario_id = last_id_result[0]['id']
        elif isinstance(result, dict):
            usuario_id = result['id']
        else:
            usuario_id = result[0]['id']


        query_insert_sindico = """
            INSERT INTO Sindico (usuarios_id)
            VALUES (%s)
        """
        try:
            result_sindico = db.execute_query(query_insert_sindico, (usuario_id,))
            if result_sindico is None:
                raise Exception("Falha ao inserir na tabela Sindico")
        except Exception as e:
            print(f"Erro ao associar usuário como Sindico: {e}")
            if not self.dialog:
                self.dialog = MDDialog(
                    text=f"Erro ao associar usuário como Sindico: {e}",
                    buttons=[
                        MDFlatButton(
                            text="Ok",
                            on_release=self.close_dialog
                        ),
                    ],
                )
            self.dialog.open()

            self.ids.nome.text = ''
            self.ids.email.text = ''
            self.ids.senha.text = ''
            return


        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None


        self.dialog = MDDialog(
            text="Cadastro realizado com sucesso!",
            buttons=[
                MDFlatButton(
                    text="Ok",
                    on_release=self.close_dialog
                ),
            ],
        )
        self.dialog.open()

        self.ids.nome.text = ''
        self.ids.email.text = ''
        self.ids.senha.text = ''

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
