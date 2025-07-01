from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from datetime import datetime, timezone
import os
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivymd.uix.pickers import MDDatePicker
import tkinter as tk
from tkinter import filedialog
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.utils import get_color_from_hex
import bcrypt
import csv
from db.connection import db
from utils.exportador_pdf import exportar_relatórios_em_pdf
from utils.file_manager import save_file, delete_file
from kivy.clock import Clock

class MyOcorrenciasSindicoModal(ModalView):
    def __init__(self, ocorrencias=[], **kwargs):
        super().__init__(**kwargs)
        self.ocorrencias = ocorrencias

    def on_open(self):
        container = self.ids.ocorrencias_container
        container.clear_widgets()

        if not self.ocorrencias:
            container.add_widget(MDLabel(
                text="Nenhuma ocorrência no momento.",
                halign="center",
                theme_text_color="Secondary"
            ))
            return

        for ocorrencia in self.ocorrencias:
            card = MDCard(
                orientation='vertical',
                padding=(10),
                radius=[12],
                size_hint_y=None,
                height=(200),
                md_bg_color=(0.96, 0.96, 0.96, 1),
            )

            card.add_widget(MDLabel(
                text=f"Título: {ocorrencia['titulo']}",
                font_style="Subtitle1",
                theme_text_color="Primary"
            ))
            card.add_widget(MDLabel(
                text=f"Descrição: {ocorrencia['descricao']}",
                theme_text_color="Secondary"
            ))
            card.add_widget(MDLabel(
                text=f"Data: {ocorrencia['data']}",
                theme_text_color="Secondary",
                font_size="12sp"
            ))

            card.add_widget(MDLabel(
                text=f"Status atual: {ocorrencia['status']}",
                theme_text_color="Hint",
                font_style="Caption"
            ))

            def atualizar_status(ocorrencia, novo_status):

                try:
                    query_update = """
                        UPDATE Ocorrencia
                        SET status = %s
                        WHERE id = %s
                    """
                    db.execute_query(query_update, (novo_status, ocorrencia['id']))
                    ocorrencia["status"] = novo_status
                    self.on_open()
                except Exception as e:
                    dialog = MDDialog(
                        text=f"Erro ao atualizar status: {e}",
                        buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
                    )
                    dialog.open()

            def abrir_menu(instance, ocorrencia_local):
                menu_items = [
                    {
                        "text": status,
                        "on_release": lambda s=status, o=ocorrencia_local: atualizar_status(o, s)
                    }
                    for status in ["Pendente", "Em andamento", "Resolvida"]
                ]
                menu = MDDropdownMenu(
                    caller=instance,
                    items=menu_items,
                    width_mult=3
                )
                menu.open()
            
            box = BoxLayout(
                orientation="horizontal",
                spacing=5,
                size_hint_x=None,
                pos_hint={"center_x": 0.5}
            )
            card.add_widget(box)

            botao_status = MDRaisedButton(
                text="Atualizar Status",
            )
            botao_status.bind(on_release=lambda instance, oc=ocorrencia: abrir_menu(instance, oc))

            box.add_widget(botao_status)


            if 'fotos_id' in ocorrencia and ocorrencia['fotos_id']:
                def abrir_imagem(instance, fotos_ids=ocorrencia['fotos_id']):
                    modal = ModalView(size_hint=(0.8, 0.8))
                    box = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
                    for file_id in fotos_ids:
                        from utils.file_manager import get_file
                        import tempfile
                        from kivy.uix.image import Image

                        file_data = get_file(file_id)
                        if file_data and file_data['dados']:

                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_data['nome_arquivo'].split('.')[-1]}") as temp_file:
                                temp_file.write(file_data['dados'])
                                temp_path = temp_file.name
                            img = Image(source=temp_path, allow_stretch=True, keep_ratio=True)
                            box.add_widget(img)
                    btn_fechar = MDRaisedButton(text="Fechar", size_hint=(1, None), height=40)
                    btn_fechar.bind(on_release=modal.dismiss)
                    box.add_widget(btn_fechar)
                    modal.add_widget(box)
                    modal.open()

                botao_ver_imagem = MDRaisedButton(
                    text="Ver Imagem",
                )
                botao_ver_imagem.bind(on_release=abrir_imagem)
                box.add_widget(botao_ver_imagem)

            container.add_widget(card)

class MyNotificacoesModal(ModalView):
    def __init__(self, notificacoes=[], **kwargs):
        super().__init__(**kwargs)
        self.notificacoes = notificacoes

    def on_open(self):
        container = self.ids.notificacoes_container
        container.clear_widgets()

        if not self.notificacoes:
            container.add_widget(MDLabel(
                text="Nenhuma notificação no momento.",
                theme_text_color="Secondary",
                halign="center"
            ))
            return

        for notificacao in self.notificacoes:
            card = MDCard(
                orientation='vertical',
                padding=(10),
                radius=[12],
                size_hint_y=None,
                height=(100),
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )
            card.add_widget(MDLabel(
                text=str(notificacao.get("titulo", "")),
                theme_text_color="Custom",
                text_color=(0.4, 0.2, 0.8, 1),
                font_style="Subtitle1"
            ))
            card.add_widget(MDLabel(
                text=str(notificacao.get("mensagem", "")),
                theme_text_color="Secondary",
                font_size="12sp"
            ))
            card.add_widget(MDLabel(
                text=str(notificacao.get("data", "")),
                theme_text_color="Secondary",
                font_size="11sp"
            ))
            container.add_widget(card)

class MyPerfilModal(ModalView):
    def __init__(self, nome, email, tipo, apartamento=None, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.email = email
        self.tipo = tipo
        self.apartamento = apartamento

    def on_open(self):
        self.ids.nome_usuario.text = self.nome
        self.ids.email_usuario.text = f"E-mail: {self.email}"
        self.ids.tipo_usuario.text = f"Tipo: {self.tipo}"

        if self.tipo.lower() == "morador" and self.apartamento:
            self.ids.apartamento_usuario.text = f"Apartamento: {self.apartamento}"
            self.ids.apartamento_usuario.opacity = 1
        else:
            self.ids.apartamento_usuario.opacity = 0

class ExportarDadosModal(ModalView):
    def __init__(self, dados, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = True
        self.dados = dados


        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        scroll = MDScrollView()
        content = MDGridLayout(cols=1, spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))


        content.add_widget(MDLabel(
            text="Reservas do Mês",
            halign="left",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=40
        ))
        content.add_widget(MDLabel(
            text=f"Total de Reservas: {self.dados.get('total_reservas', 0)}",
            halign="left",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=40
        ))
        for reserva in self.dados.get('reservas', []):
            item_layout = MDBoxLayout(
                orientation="vertical",
                padding=10,
                spacing=5,
                size_hint_y=None,
                height=100,
                md_bg_color=(1, 1, 1, 0.05),
            )
            item_layout.add_widget(MDLabel(
                text=f"Morador: {reserva['morador']}",
                halign="left",
                theme_text_color="Primary"
            ))
            item_layout.add_widget(MDLabel(
                text=f"Espaço: {reserva['espaco']}",
                halign="left",
                theme_text_color="Secondary"
            ))
            item_layout.add_widget(MDLabel(
                text=f"Data: {reserva['data_inicio']}",
                halign="left",
                theme_text_color="Secondary"
            ))
            content.add_widget(item_layout)


        content.add_widget(MDLabel(
            text="Ocorrências do Mês",
            halign="left",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=40
        ))
        content.add_widget(MDLabel(
            text=f"Total de Ocorrências: {self.dados.get('total_ocorrencias', 0)}",
            halign="left",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=40
        ))
        for ocorrencia in self.dados.get('ocorrencias', []):
            item_layout = MDBoxLayout(
                orientation="vertical",
                padding=10,
                spacing=5,
                size_hint_y=None,
                height=120,
                md_bg_color=(1, 1, 1, 0.05),
            )
            item_layout.add_widget(MDLabel(
                text=f"Morador: {ocorrencia['morador']}",
                halign="left",
                theme_text_color="Primary"
            ))
            item_layout.add_widget(MDLabel(
                text=f"Título: {ocorrencia['titulo']}",
                halign="left",
                theme_text_color="Secondary"
            ))
            item_layout.add_widget(MDLabel(
                text=f"Descrição: {ocorrencia['descricao']}",
                halign="left",
                theme_text_color="Secondary"
            ))
            item_layout.add_widget(MDLabel(
                text=f"Data: {ocorrencia['data']}",
                halign="left",
                theme_text_color="Secondary"
            ))
            content.add_widget(item_layout)


        content.add_widget(MDLabel(
            text="Moradores por Bloco",
            halign="left",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=40
        ))
        content.add_widget(MDLabel(
            text=f"Total de Moradores: {self.dados.get('total_moradores', 0)}",
            halign="left",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=40
        ))
        for morador in self.dados.get('moradores', []):
            item_layout = MDBoxLayout(
                orientation="vertical",
                padding=10,
                spacing=5,
                size_hint_y=None,
                height=100,
                md_bg_color=(1, 1, 1, 0.05),
            ) 
            item_layout.add_widget(MDLabel(
                text=f"Bloco: {morador['bloco']}",
                halign="left",
                theme_text_color="Primary"
            ))
            item_layout.add_widget(MDLabel(
                text=f"Morador: {morador['nome']}",
                halign="left",
                theme_text_color="Secondary"
            ))
            item_layout.add_widget(MDLabel(
                text=f"Apartamento: {morador['apartamento']}",
                halign="left",
                theme_text_color="Secondary"
            ))
            content.add_widget(item_layout)

        scroll.add_widget(content)
        layout.add_widget(scroll)


        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={"center_x": 0.5}
        )


        btn_pdf = MDFlatButton(
            text="EXPORTAR EM PDF",
            size_hint=(0.5, None),
            height=40,
            on_release=self.exportar_pdf
        )
        buttons_layout.add_widget(btn_pdf)
        layout.add_widget(buttons_layout)

        self.add_widget(layout)

    def exportar_pdf(self, instance):
        try:
            dados_combinados = []
            for r in self.dados.get('reservas', []):
                dados_combinados.append({
                    'titulo': f"Reserva: {r['espaco']}",
                    'data': r['data_inicio'],
                    'descricao': f"Morador: {r['morador']}"
                })
            for o in self.dados.get('ocorrencias', []):
                dados_combinados.append({
                    'titulo': f"Ocorrência: {o['titulo']}",
                    'data': o['data'],
                    'descricao': f"Morador: {o['morador']} - {o['descricao']}"
                })
            for m in self.dados.get('moradores', []):
                dados_combinados.append({
                    'titulo': f"Morador: {m['nome']}",
                    'data': m['apartamento'],
                    'descricao': f"Bloco: {m['bloco']}"
                })
            dados_combinados.append({
                'titulo': 'Resumo Mensal',
                'data': datetime.now().strftime("%B/%Y"),
                'descricao': f"Reservas: {self.dados.get('total_reservas', 0)}, Ocorrências: {self.dados.get('total_ocorrencias', 0)}, Moradores: {self.dados.get('total_moradores', 0)}"
            })
            caminho = exportar_relatórios_em_pdf(dados_combinados)
            dialog = MDDialog(
                text=f"PDF gerado com sucesso: {caminho}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
        except Exception as e:
            dialog = MDDialog(
                text=f"Erro ao gerar PDF: {e}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
    
    def exportar_dados(self, instance):
        caminho_arquivo = "dados_exportados.csv"
        try:
            with open(caminho_arquivo, mode="w", newline='', encoding='utf-8') as arquivo:
                writer = csv.writer(arquivo)
                writer.writerow(["Seção", "Total", "Morador", "Espaço/Título/Bloco", "Data/Apartamento", "Descrição"])

                writer.writerow(["Reservas", self.dados.get('total_reservas', 0), "", "", "", ""])
                for r in self.dados.get('reservas', []):
                    writer.writerow(["", "", r["morador"], r["espaco"], r["data_inicio"], ""])

                writer.writerow(["Ocorrências", self.dados.get('total_ocorrencias', 0), "", "", "", ""])
                for o in self.dados.get('ocorrencias', []):
                    writer.writerow(["", "", o["morador"], o["titulo"], o["data"], o["descricao"]])

                writer.writerow(["Moradores", self.dados.get('total_moradores', 0), "", "", "", ""])
                for m in self.dados.get('moradores', []):
                    writer.writerow(["", "", m["nome"], m["bloco"], m["apartamento"], ""])

            print(f"Dados exportados para {caminho_arquivo}")
        except Exception as e:
             print(f"Erro ao exportar CSV: {e}")
        dialog = MDDialog(
            text=f"Erro ao exportar CSV: {e}",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def exportar_relatorios(self, instance):
        caminho_arquivo = "relatorios_exportados.csv"
        with open(caminho_arquivo, mode="w", newline='', encoding='utf-8') as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow(["Título", "Data", "Descrição"])
            for r in self.relatorios:
                writer.writerow([r["titulo"], r["data"], r["descricao"]])
        print(f"Relatórios exportados para {caminho_arquivo}")

class CriarComunicadoModal(ModalView):
    def abrir_seletor_foto(self):
        try:
            root = tk.Tk()
            root.withdraw() 
            caminho = filedialog.askopenfilename(
                title="Selecionar imagem",
                filetypes=[
                    ("Imagens", "*.png *.jpg *.jpeg"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            if caminho:
                self.definir_imagem_preview(caminho)
        except Exception as e:
            print(f"Erro ao selecionar arquivo: {e}")

    def definir_imagem_preview(self, caminho):
        self.ids.imagem_preview.source = caminho
        self.selected_image_path = caminho

    def criar_comunicado(self):
        from kivymd.app import MDApp
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from datetime import datetime, timezone
        from utils.file_manager import save_file, delete_file
        
        app = MDApp.get_running_app()
        dashboard_screen = app.root.get_screen('sindico_dashboard')
        
        titulo = self.ids.titulo_ocorrencia.text.strip() if 'titulo_ocorrencia' in self.ids else ''
        descricao = self.ids.descricao_ocorrencia.text.strip() if 'descricao_ocorrencia' in self.ids else ''
        imagem_path = getattr(self, 'selected_image_path', None)

        if not titulo or not descricao:
            dialog = MDDialog(
                text="Por favor, preencha o título e a descrição do comunicado.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            return

        query_user = "SELECT id FROM usuarios WHERE email = %s"
        result = db.execute_query(query_user, (dashboard_screen.user_email,))
        if not result:
            dialog = MDDialog(
                text="Usuário não encontrado.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            return
            
        user_id = result[0]['id']
        arquivos_ids = []
        
        if imagem_path and os.path.exists(imagem_path):
            file_id = save_file(imagem_path, user_id)
            if file_id:
                arquivos_ids.append(file_id)

        try:
            query_insert = """
                INSERT INTO Comunicado (titulo, mensagem, data_publicacao, usuario_id, arquivos_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            
            result = db.execute_query(
                query_insert, 
                (titulo, descricao, datetime.now(timezone.utc), user_id, arquivos_ids)
            )
            
            if not result:
                raise Exception("Falha ao inserir comunicado no banco de dados.")
                
            dialog = MDDialog(
                text="Comunicado criado com sucesso!",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            
            self.ids.titulo_ocorrencia.text = ''
            self.ids.descricao_ocorrencia.text = ''
            self.ids.imagem_preview.source = ''
            self.selected_image_path = None
            
            self.dismiss()
            
            if hasattr(dashboard_screen, 'refresh_comunicados'):
                dashboard_screen.refresh_comunicados()
                
        except Exception as e:
            for file_id in arquivos_ids:
                delete_file(file_id, user_id)
                
            dialog = MDDialog(
                text=f"Erro ao criar comunicado: {str(e)}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()

class CadastrarEditarMoradoresModal(ModalView):
    def __init__(self, moradores=[], **kwargs):
        super().__init__(**kwargs)
        self.moradores = moradores
        self.morador_em_edicao = None

    def on_open(self):
        self.atualizar_lista_moradores()

        menu_items = [
            {
                "text": tipo,
                "on_release": lambda x=tipo: self.definir_tipo(x)
            } for tipo in ["morador", "sindico"]
        ]
        self.tipo_menu = MDDropdownMenu(
            caller=self.ids.tipo_input,
            items=menu_items,
            width_mult=3
        )

        self.ids.tipo_input.on_release = self.tipo_menu.open

    def definir_tipo(self, tipo):
        self.ids.tipo_input.text = tipo
        self.tipo_menu.dismiss()

    def atualizar_lista_moradores(self):
        lista = self.ids.moradores_lista
        lista.clear_widgets()

        if not self.moradores:
            lista.add_widget(MDLabel(text="", theme_text_color="Secondary",))
            return

        for morador in self.moradores:
            card = MDCard(
                orientation='vertical',
                padding=10,
                size_hint_y=None,
                height=120,
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )
            card.add_widget(MDLabel(text=f"{morador['nome']} ({morador['tipo']})"))
            card.add_widget(MDLabel(text=f"Apartamento: {morador['apartamento']} - Email: {morador['email']}"))

            botoes = BoxLayout(size_hint_y=None, height=30)
            btn_editar = MDFlatButton(text="Editar", on_release=lambda x, m=morador: self.editar_morador(m))
            btn_excluir = MDFlatButton(text="Excluir", on_release=lambda x, m=morador: self.excluir_morador(m))
            botoes.add_widget(btn_editar)
            botoes.add_widget(btn_excluir)

            card.add_widget(botoes)
            lista.add_widget(card)

    def salvar_morador(self):
        nome = self.ids.nome_input.text
        email = self.ids.email_input.text
        senha = self.ids.senha_input.text
        tipo = self.ids.tipo_input.text
        apartamento = self.ids.apartamento_input.text

        if not all([nome, email, senha, tipo, apartamento]):
            self.dialog = MDDialog(text="Preencha todos os campos!", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
            self.dialog.open()
            return

        if self.morador_em_edicao:
            usuario_id = self.morador_em_edicao.get("id")
            if not usuario_id:
                self.dialog = MDDialog(text="Erro: Morador inválido para edição.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
                self.dialog.open()
                return

            hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            query_update_usuario = """
                UPDATE usuarios
                SET nome = %s, email = %s, senha = %s
                WHERE id = %s
            """
            result_usuario = db.execute_query(query_update_usuario, (nome, email, hashed_password, usuario_id))
            if result_usuario is None:
                self.dialog = MDDialog(text="Erro ao atualizar usuário. Tente novamente.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
                self.dialog.open()
                return

            query_update_morador = """
                UPDATE Morador
                SET apartamento = %s
                WHERE usuarios_id = %s
            """
            result_morador = db.execute_query(query_update_morador, (apartamento, usuario_id))
            if result_morador is None:
                self.dialog = MDDialog(text="Erro ao atualizar morador. Tente novamente.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
                self.dialog.open()
                return

            self.morador_em_edicao.update({
                "nome": nome,
                "email": email,
                "senha": senha,
                "tipo": tipo,
                "apartamento": apartamento
            })
            self.morador_em_edicao = None
        else:
            hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            query_check = "SELECT * FROM usuarios WHERE email = %s"
            existing_user = db.execute_query(query_check, (email,))
            if existing_user:
                self.dialog = MDDialog(text="Este e-mail já está cadastrado.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
                self.dialog.open()
                return

            query_insert_usuario = """
                INSERT INTO usuarios (nome, email, senha, tipo)
                VALUES (%s, %s, %s, 'Morador')
                RETURNING id
            """
            result = db.execute_query(query_insert_usuario, (nome, email, hashed_password))
            if not result:
                self.dialog = MDDialog(text="Erro ao cadastrar usuário. Tente novamente.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
                self.dialog.open()
                return
            if isinstance(result, int):
                usuario_id = result
            elif isinstance(result, dict):
                usuario_id = result['id']
            else:
                usuario_id = result[0]['id']

            query_insert_morador = """
                INSERT INTO Morador (usuarios_id, apartamento)
                VALUES (%s, %s)
            """
            try:
                result_morador = db.execute_query(query_insert_morador, (usuario_id, apartamento))
            except Exception as e:
                self.dialog = MDDialog(text=f"Erro ao associar usuário como Morador: {e}", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
                self.dialog.open()
                return
            if result_morador is None:
                self.dialog = MDDialog(text="Erro ao associar usuário como Morador. Tente novamente.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
                self.dialog.open()
                return

            self.moradores.append({
                "id": usuario_id,
                "nome": nome,
                "email": email,
                "senha": senha,
                "tipo": tipo,
                "apartamento": apartamento
            })

        self.limpar_campos()
        self.atualizar_lista_moradores()

    def editar_morador(self, morador):
        self.morador_em_edicao = morador
        self.ids.nome_input.text = morador["nome"]
        self.ids.email_input.text = morador["email"]
        self.ids.senha_input.text = morador["senha"]
        self.ids.apartamento_input.text = morador["apartamento"]
        self.ids.tipo_input.text = morador["tipo"]

    def excluir_morador(self, morador):
        usuario_id = morador.get("id")
        if not usuario_id:
            self.dialog = MDDialog(text="Erro: Morador inválido para exclusão.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
            self.dialog.open()
            return


        query_delete_reservas = "DELETE FROM Reserva WHERE morador_id = %s"
        result_reservas = db.execute_query(query_delete_reservas, (usuario_id,))
        if result_reservas is None:
            self.dialog = MDDialog(text="Erro ao excluir reservas relacionadas. Tente novamente.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
            self.dialog.open()
            return


        query_delete_ocorrencias = "DELETE FROM Ocorrencia WHERE morador_id = %s"
        result_ocorrencias = db.execute_query(query_delete_ocorrencias, (usuario_id,))
        if result_ocorrencias is None:
            self.dialog = MDDialog(text="Erro ao excluir ocorrências relacionadas. Tente novamente.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
            self.dialog.open()
            return


        query_delete_morador = "DELETE FROM Morador WHERE usuarios_id = %s"
        result_morador = db.execute_query(query_delete_morador, (usuario_id,))
        if result_morador is None:
            self.dialog = MDDialog(text="Erro ao excluir morador. Tente novamente.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
            self.dialog.open()
            return


        query_delete_usuario = "DELETE FROM usuarios WHERE id = %s"
        result_usuario = db.execute_query(query_delete_usuario, (usuario_id,))
        if result_usuario is None:
            self.dialog = MDDialog(text="Erro ao excluir usuário. Tente novamente.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
            self.dialog.open()
            return


        self.moradores.remove(morador)
        self.atualizar_lista_moradores()

    def limpar_campos(self):
        self.ids.nome_input.text = ""
        self.ids.email_input.text = ""
        self.ids.senha_input.text = ""
        self.ids.apartamento_input.text = ""
        self.ids.tipo_input.text = "Selecione o tipo"

class ReservasModal(ModalView):
    def __init__(self, reservas=[], **kwargs):
        super().__init__(**kwargs)
        self.reservas = reservas

    def on_open(self):
        container = self.ids.reservas_container
        container.clear_widgets()

        if not self.reservas:
            container.add_widget(MDLabel(
                text="Sem reservas no momento.",
                halign="center",
                theme_text_color="Secondary",
                font_style="Subtitle1"
            ))
            return

        for reserva in self.reservas:
            card = MDCard(
                orientation='vertical',
                padding=10,
                spacing=10,
                size_hint_y=None,
                height=240,
                radius=[12],
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )

            card.add_widget(MDLabel(
                text=f"Morador: {reserva['morador']}",
                font_style="Subtitle1"
            ))
            card.add_widget(MDLabel(
                text=f"Espaço: {reserva['espaco']}  |  Data e Hora: {reserva['data_inicio']} - {reserva['data_fim']}",
                theme_text_color="Secondary"
            ))
            card.add_widget(MDLabel(
                text=f"Horário: {reserva['horario']}",
                theme_text_color="Secondary"
            ))
            card.add_widget(MDLabel(
                text=f"Observações: {reserva.get('observacoes', '')}",
                theme_text_color="Secondary"
            ))

            status = reserva.get("status", "pendente")

            if status == "pendente":
                motivo_input = MDTextField(
                    hint_text="Motivo da decisão (opcional)",
                    multiline=True,
                    mode="rectangle",
                    size_hint_y=None,
                    height=80
                )
                card.add_widget(motivo_input)

                botoes = MDBoxLayout(
                    orientation='horizontal',
                    spacing=10,
                    size_hint_y=None,
                    height=40
                )

                aprovar_btn = MDRaisedButton(
                    text="Aprovar",
                    on_release=lambda inst, r=reserva, m=motivo_input: self.atualizar_status(r, "aprovada", m.text)
                )
                rejeitar_btn = MDRaisedButton(
                    text="Rejeitar",
                    on_release=lambda inst, r=reserva, m=motivo_input: self.atualizar_status(r, "rejeitada", m.text)
                )

                botoes.add_widget(aprovar_btn)
                botoes.add_widget(rejeitar_btn)
                card.add_widget(botoes)

            else:
                status_label = "Aprovada" if status == "aprovada" else "Rejeitada"
                card.add_widget(MDLabel(
                    text=f"Status: {status_label}",
                    theme_text_color="Custom",
                    text_color=(0.2, 0.7, 0.3, 1) if status == "aprovada" else (0.9, 0.2, 0.2, 1),
                    font_style="Subtitle2"
                ))
                card.add_widget(MDLabel(
                    text=f"Motivo: {reserva.get('motivo', 'Não informado')}",
                    theme_text_color="Secondary",
                    font_style="Caption"
                ))

            container.add_widget(card)

    def atualizar_status(self, reserva, novo_status, motivo):
        try:
            query_update = """
                UPDATE Reserva
                SET status = %s, motivo = %s
                WHERE id = %s
            """
            db.execute_query(query_update, (novo_status, motivo or "Sem motivo informado", reserva["id"]))
            db.connection.commit()
            pass

            reserva["status"] = novo_status
            reserva["motivo"] = motivo or "Sem motivo informado"

            self.on_open()

            if hasattr(self.parent, 'parent') and hasattr(self.parent.parent, 'refresh_reservas'):
                self.parent.parent.refresh_reservas()

        except Exception as e:
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.button import MDFlatButton
            dialog = MDDialog(
                text=f"Erro ao atualizar status da reserva: {e}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()

class DashboardSindicoScreen(Screen):
    new_notifications_count = NumericProperty(0)
    last_occurrence_label = StringProperty("Carregando última ocorrência...")
    last_reservation_label = StringProperty("Carregando última reserva...")

    def __init__(self, **kw):
        super().__init__(**kw)
        self.reservas = []
        self.ocorrencias = []
        self.moradores = []
        self.comunicados = []
        self.relatorios = []
        self.user_data = None
        self.user_email = None
        self.refresh_event = None

    def set_user(self, email):
        self.user_email = email
        self.load_user_data()
        self.load_comunicados()
        self.update_ui()
        self.atualizar_badge_notificacoes()

    def on_enter(self, *args):
        super().on_enter(*args)
        self.refresh_dashboard()
        if not self.refresh_event:
            self.refresh_event = Clock.schedule_interval(self.refresh_dashboard, 10)

    def on_leave(self, *args):
        super().on_leave(*args)
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None

    def refresh_dashboard(self, *args):
        self.update_last_occurrence_label()
        self.update_last_reservation_label()
        self.atualizar_badge_notificacoes()

    def on_pre_enter(self):
        self.update_last_occurrence_label()
        self.update_last_reservation_label()

    def update_last_occurrence_label(self):
        query = """
            SELECT titulo
            FROM Ocorrencia
            ORDER BY data DESC
            LIMIT 1
        """
        result = db.execute_query(query)
        if result and len(result) > 0:
            self.last_occurrence_label = result[0]['titulo']
        else:
            self.last_occurrence_label = "Nenhuma ocorrência encontrada"

    def update_last_reservation_label(self):
        query = """
            SELECT area, to_char(data_inicio, 'DD/MM') as data_inicio
            FROM Reserva
            ORDER BY data_inicio DESC
            LIMIT 1
        """
        result = db.execute_query(query)
        if result and len(result) > 0:
            self.last_reservation_label = f"{result[0]['area']} – {result[0]['data_inicio']}"
        else:
            self.last_reservation_label = "Nenhuma reserva encontrada"

    def open_modal(self):
        query_ocorrencias = """
            SELECT id, titulo, descricao, to_char(data, 'DD/MM/YYYY') as data, status, fotos_id
            FROM Ocorrencia
            ORDER BY data DESC
            LIMIT 10
        """
        self.ocorrencias = db.execute_query(query_ocorrencias) or []
        modal = MyOcorrenciasSindicoModal(ocorrencias=self.ocorrencias)
        modal.open()

    def open_modal_reservas(self):
        query_reservas = """
            SELECT r.id, u.nome as morador, r.area as espaco, to_char(r.data_inicio, 'DD/MM/YYYY') as data_inicio,
                   to_char(r.data_fim, 'DD/MM/YYYY') as data_fim, r.horario, r.status, r.observacoes
            FROM Reserva r
            JOIN Morador m ON r.morador_id = m.usuarios_id
            JOIN usuarios u ON m.usuarios_id = u.id
            ORDER BY r.data_inicio DESC
            LIMIT 10
        """
        self.reservas = db.execute_query(query_reservas) or []
        for r in self.reservas:
            print(f"DEBUG: Reserva: {r}")
        modal = ReservasModal(reservas=self.reservas)
        modal.open()

    def refresh_reservas(self):
        self.open_modal_reservas()

    def open_modal_cadastrar_editar_moradores(self):
        query_moradores = """
            SELECT u.id, u.nome, u.email, u.senha, u.tipo, m.apartamento
            FROM usuarios u
            JOIN Morador m ON u.id = m.usuarios_id
            WHERE u.tipo = 'Morador'
            ORDER BY u.nome
        """
        self.moradores = db.execute_query(query_moradores) or []
        modal = CadastrarEditarMoradoresModal(moradores=self.moradores)
        modal.open()

    def open_modal_criar_comunicado(self):
        if not hasattr(self, 'criar_comunicado_modal'):
            self.criar_comunicado_modal = CriarComunicadoModal()
        self.criar_comunicado_modal.open()

    def open_modal_exportar_dados(self):
        reservas = []
        total_reservas = 0
        ocorrencias = []
        total_ocorrencias = 0
        moradores = []
        total_moradores = 0
    
        query_reservas = """
            SELECT COUNT(*) AS total_reservas,
                u.nome AS morador,
                r.area AS espaco,
                to_char(r.data_inicio, 'DD/MM/YYYY') AS data_inicio
            FROM Reserva r
            JOIN Morador m ON r.morador_id = m.usuarios_id
            JOIN usuarios u ON m.usuarios_id = u.id
            WHERE EXTRACT(MONTH FROM r.data_inicio) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM r.data_inicio) = EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY u.nome, r.area, r.data_inicio
            ORDER BY r.data_inicio DESC;
        """
        try:
            reservas = db.execute_query(query_reservas) or []
            total_reservas = sum([r['total_reservas'] for r in reservas]) if reservas else 0
        except Exception as e:
            print(f"Erro ao consultar reservas: {e}")
            reservas = []
            total_reservas = 0

        query_ocorrencias = """
            SELECT COUNT(*) AS total_ocorrencias,
                u.nome AS morador,
                o.titulo,
                o.descricao,
                to_char(o.data, 'DD/MM/YYYY') AS data
            FROM Ocorrencia o
            JOIN Morador m ON o.morador_id = m.usuarios_id
            JOIN usuarios u ON m.usuarios_id = u.id
            WHERE EXTRACT(MONTH FROM o.data) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM o.data) = EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY u.nome, o.titulo, o.descricao, o.data
            ORDER BY o.data DESC;
        """
        try:
            ocorrencias = db.execute_query(query_ocorrencias) or []
            total_ocorrencias = sum([o['total_ocorrencias'] for o in ocorrencias]) if ocorrencias else 0
        except Exception as e:
            print(f"Erro ao consultar ocorrências: {e}")
            ocorrencias = []
            total_ocorrencias = 0

        query_moradores = """
            SELECT COUNT(*) AS total_moradores,
                CASE
                    WHEN m.apartamento LIKE 'Bloco A%' THEN 'Bloco A'
                    WHEN m.apartamento LIKE 'Bloco B%' THEN 'Bloco B'
                    ELSE 'Outros'
                END AS bloco,
                u.nome,
                m.apartamento
            FROM usuarios u
            JOIN Morador m ON u.id = m.usuarios_id
            WHERE u.tipo = 'Morador'
            GROUP BY bloco, u.nome, m.apartamento
            ORDER BY bloco, u.nome;
        """
        try:
            moradores = db.execute_query(query_moradores) or []
            total_moradores = sum([m['total_moradores'] for m in moradores]) if moradores else 0
        except Exception as e:
            print(f"Erro ao consultar moradores: {e}")
            moradores = []
            total_moradores = 0

        dados = {
            'reservas': reservas,
            'total_reservas': total_reservas,
            'ocorrencias': ocorrencias,
            'total_ocorrencias': total_ocorrencias,
            'moradores': moradores,
            'total_moradores': total_moradores
        }
        modal = ExportarDadosModal(dados=dados)
        modal.open()

    def load_comunicados(self):
        query = """
            SELECT c.id, c.titulo, c.mensagem, c.arquivos_id,
                   to_char(c.data_publicacao, 'DD/MM/YYYY') as data_publicacao,
                   u.nome as autor
            FROM Comunicado c
            JOIN usuarios u ON c.usuario_id = u.id
            ORDER BY c.data_publicacao DESC
            LIMIT 10
        """
        result = db.execute_query(query)
        if result:
            self.comunicados = result
        else:
            self.comunicados = []

    def refresh_dashboard(self, *args):
        self.load_user_data()
        self.load_comunicados()
        self.update_ui()
        self.atualizar_badge_notificacoes()

    def load_user_data(self):
        query = """
            SELECT u.id, u.nome, u.email, u.tipo
            FROM usuarios u
            LEFT JOIN Sindico m ON u.id = m.usuarios_id
            WHERE u.email = %s
        """
        result = db.execute_query(query, (self.user_email,))
        if result:
            self.user_data = result[0]

    def update_ui(self):
        if not self.user_data:
            return

    def open_modal_perfil(self):
        if not self.user_data:
            return
        nome = self.user_data.get('nome', '')
        email = self.user_data.get('email', '')
        tipo = self.user_data.get('tipo', '')
        apartamento = self.user_data.get('apartamento', None)

        modal = MyPerfilModal(nome, email, tipo, apartamento)
        modal.open()

    def open_modal_notificacoes(self):
        notificacoes = []
        user_id = self.user_data['id'] if self.user_data and 'id' in self.user_data else None
        query = """
            SELECT n.titulo, n.mensagem, n.arquivos, n.data, n.tipo, n.id as notificacao_id
            FROM (
                SELECT
                    CONCAT('Reserva Pendente - ', u.nome) as titulo,
                    CONCAT('A reserva para ', r.area, ' está pendente.') as mensagem,
                    NULL as arquivos,
                    r.data_inicio as data,
                    'reserva' as tipo,
                    r.id
                FROM Reserva r
                JOIN Morador m ON r.morador_id = m.usuarios_id
                JOIN usuarios u ON m.usuarios_id = u.id
                WHERE r.status = 'pendente'
                AND r.id NOT IN (
                    SELECT notification_id FROM NotificationReadStatus WHERE user_id = %s AND notification_type = 'reserva' AND read_status = TRUE
                )
                UNION ALL
                SELECT
                    CONCAT('Ocorrência em Aberto - ', u.nome) as titulo,
                    CONCAT('A ocorrência "', o.titulo, '" está em aberto.') as mensagem,
                    NULL as arquivos,
                    o.data as data,
                    'ocorrencia' as tipo,
                    o.id
                FROM Ocorrencia o
                JOIN Morador m ON o.morador_id = m.usuarios_id
                JOIN usuarios u ON m.usuarios_id = u.id
                WHERE o.status = 'aberta'
                AND o.id NOT IN (
                    SELECT notification_id FROM NotificationReadStatus WHERE user_id = %s AND notification_type = 'ocorrencia' AND read_status = TRUE
                )
            ) n
            ORDER BY n.data DESC
            LIMIT 10
        """
        notificacoes = db.execute_query(query, (user_id, user_id)) or []

        for notif in notificacoes:
            notif_id = notif['notificacao_id']
            upsert_query = """
                INSERT INTO NotificationReadStatus (user_id, notification_type, notification_id, read_status, read_timestamp)
                VALUES (%s, %s, %s, TRUE, NOW())
                ON CONFLICT (user_id, notification_type, notification_id) DO UPDATE
                SET read_status = TRUE, read_timestamp = NOW()
            """
            notif_type = notif['tipo']
            db.execute_query(upsert_query, (user_id, notif_type, notif_id))
        db.connection.commit()

        self.new_notifications_count = 0
        modal = MyNotificacoesModal(notificacoes=notificacoes)
        modal.open()

    def refresh_comunicados(self):
        self.load_comunicados()
        self.update_ui()

    def atualizar_badge_notificacoes(self):
        if not self.user_data or 'id' not in self.user_data:
                self.new_notifications_count = 0
                return

            user_id = self.user_data['id']
            query = """
                SELECT COUNT(*) as total
                FROM (
                    SELECT id
                    FROM Reserva
                    WHERE status = 'pendente'
                      AND id NOT IN (
                          SELECT notification_id
                          FROM NotificationReadStatus
                          WHERE user_id = %s AND notification_type = 'reserva' AND read_status = TRUE
                      )
                    UNION ALL
                    SELECT id
                    FROM Ocorrencia
                    WHERE status = 'aberta'
                      AND id NOT IN (
                          SELECT notification_id
                          FROM NotificationReadStatus
                          WHERE user_id = %s AND notification_type = 'ocorrencia' AND read_status = TRUE
                      )
                ) sub
            """
            result = db.execute_query(query, (user_id, user_id))
            self.new_notifications_count = result[0]['total'] if result else 0
        except Exception as e:
            self.new_notifications_count = 0

