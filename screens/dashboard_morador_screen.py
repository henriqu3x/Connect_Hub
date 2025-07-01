from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from datetime import datetime
import os
from kivy.properties import ObjectProperty
from kivymd.uix.pickers import MDDatePicker
from plyer import filechooser
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from db.connection import db
from utils.file_manager import save_file, delete_file
from kivy.metrics import dp

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


class MyReservasAreaModal(ModalView):
    def abrir_calendario(self, field_id):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=lambda instance, value, date_range: self.definir_data_reserva(instance, value, date_range, field_id))
        date_dialog.open()

    def definir_data_reserva(self, instance, value, date_range, field_id):
        formatted_date = value.strftime("%d/%m/%Y")
        if field_id in self.ids:
            self.ids[field_id].text = formatted_date

    def abrir_seletor_hora(self, field_id):

        if field_id in self.ids:
            self.ids[field_id].focus = True


class RegistrarOcorrenciaModal(ModalView):
    def __init__(self, **kwargs):
        self.on_save_callback = None
        super().__init__(**kwargs)

    def on_open(self):
        self.ids.imagem_preview.source = ''
        self.selected_image_path = None
        self.ids.imagem_preview.height = dp(0)  
        self.ids.imagem_preview.opacity = 0
        self.ids.titulo_ocorrencia.text = ''
        self.ids.descricao_ocorrencia.text = ''
        self.ids.data_ocorrencia.text = ''

    def abrir_calendario(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.definir_data_ocorrencia)
        date_dialog.open()

    def definir_data_ocorrencia(self, instance, value, date_range):
        formatted_date = value.strftime("%d/%m/%Y")
        self.ids.data_ocorrencia.text = formatted_date

    def abrir_seletor_foto(self):
        try:
            import tkinter as tk
            from tkinter import filedialog
            
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
        self.ids.imagem_preview.height = self.ids.imagem_preview.width  
        self.ids.imagem_preview.opacity = 1

    def salvar_ocorrencia(self, user_email):
        
        titulo = self.ids.titulo_ocorrencia.text.strip() if 'titulo_ocorrencia' in self.ids else ''
        descricao = self.ids.descricao_ocorrencia.text.strip() if 'descricao_ocorrencia' in self.ids else ''
        data_str = self.ids.data_ocorrencia.text.strip() if 'data_ocorrencia' in self.ids else ''
        imagem_path = getattr(self, 'selected_image_path', None)

        if not titulo or not descricao or not data_str:
            dialog = MDDialog(
                text="Por favor, preencha todos os campos obrigatórios.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            return False

        try:
            data = datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            dialog = MDDialog(
                text="Data inválida. Use o formato DD/MM/AAAA.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            return False

        query_user_id = "SELECT id FROM usuarios WHERE email = %s"
        result = db.execute_query(query_user_id, (user_email,))
        if not result:
            dialog = MDDialog(
                text="Usuário não encontrado.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            return False
            
        user_id = result[0]['id']
        
        query_morador_id = """
            SELECT usuarios_id FROM Morador WHERE usuarios_id = %s
        """
        result = db.execute_query(query_morador_id, (user_id,))
        if not result:
            dialog = MDDialog(
                text="Morador não encontrado para o usuário.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            return False

        morador_id = result[0]['usuarios_id']
        fotos_ids = []
        
        if imagem_path and os.path.exists(imagem_path):
            file_id = save_file(imagem_path, user_id)
            if file_id:
                fotos_ids.append(file_id)

        try:
            query_insert = """
                INSERT INTO Ocorrencia (titulo, descricao, status, data, morador_id, fotos_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            result = db.execute_query(
                query_insert, 
                (titulo, descricao, 'aberta', data, morador_id, fotos_ids)
            )
            
            if not result:
                raise Exception("Falha ao inserir ocorrência no banco de dados.")
                
            if self.on_save_callback:
                self.on_save_callback()
                
            dialog = MDDialog(
                text="Ocorrência registrada com sucesso!",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            
            self.ids.titulo_ocorrencia.text = ''
            self.ids.descricao_ocorrencia.text = ''
            self.ids.data_ocorrencia.text = ''
            self.ids.imagem_preview.source = ''
            self.selected_image_path = None
            self.ids.imagem_preview.height = dp(0)  
            self.ids.imagem_preview.opacity = 0
            
            return True
            
        except Exception as e:
            for file_id in fotos_ids:
                delete_file(file_id, user_id)
                
            dialog = MDDialog(
                text=f"Erro ao salvar ocorrência: {str(e)}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
            return False

class MyOcorrenciasModal(ModalView):
    pass

class MyReservasModal(ModalView):
    pass

class MyModalView(ModalView):
    pass

class FileChooserContent(BoxLayout):
    file_chooser = ObjectProperty(None)

    def __init__(self, modal, **kwargs):
        super().__init__(**kwargs)
        self.modal = modal
        self.orientation = "vertical"

        self.file_chooser = FileChooserListView(filters=["*.png", "*.jpg", "*.jpeg"])
        self.add_widget(self.file_chooser)

        from kivymd.uix.button import MDRaisedButton
        botao = MDRaisedButton(
            text="Selecionar",
            pos_hint={"center_x": 0.5},
            on_release=self.selecionar_arquivo,
        )
        self.add_widget(botao)

    def selecionar_arquivo(self, *args):
        selected = self.file_chooser.selection
        if selected:
            self.modal.definir_imagem_preview(selected[0])

from kivy.properties import NumericProperty
from kivy.clock import Clock

class DashboardMoradorScreen(Screen):
    new_notifications_count = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_email = None
        self.user_data = None
        self.ocorrencias = []
        self.reservas = []
        self.notificacoes = []
        self.comunicados = []
        self.registrar_ocorrencia_modal = RegistrarOcorrenciaModal()
        self.refresh_event = None

    def on_enter(self, *args):
        super().on_enter(*args)
        if self.user_email:
            self.refresh_event = Clock.schedule_interval(self.refresh_data, 10)
            self.refresh_data()  

    def on_leave(self, *args):
        super().on_leave(*args)
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None

    def refresh_data(self, *args):
        self.load_ocorrencias()
        self.load_reservas()
        self.load_comunicados()
        self.load_notificacoes()
        self.update_ui()

    def open_modal(self):

        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDRaisedButton
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.uix.modalview import ModalView

        class MyComunicadosModal(ModalView):
            def __init__(self, comunicados=[], **kwargs):
                super().__init__(**kwargs)
                self.comunicados = comunicados

            def on_open(self):
                container = self.ids.comunicados_container
                container.clear_widgets()

                if not self.comunicados:
                    container.add_widget(MDLabel(
                        text="Nenhum comunicado no momento.",
                        halign="center",
                        theme_text_color="Secondary"
                    ))
                    return

                for comunicado in self.comunicados:
                    card = MDCard(
                        orientation='vertical',
                        padding=10,
                        radius=[12],
                        size_hint_y=None,
                        height=160,
                        md_bg_color=(0.95, 0.95, 0.95, 1)
                    )
                    card.add_widget(MDLabel(
                        text=f"{comunicado.get('titulo', '')}",
                        font_style="Subtitle1",
                        theme_text_color="Custom",
                        text_color=(0.4, 0.2, 0.8, 1)
                    ))
                    card.add_widget(MDLabel(
                        text=f"Data: {comunicado.get('data', '')}",
                        theme_text_color="Secondary",
                        font_size="12sp"
                    ))
                    card.add_widget(MDLabel(
                        text=f"{comunicado.get('mensagem', '')}",
                        theme_text_color="Secondary",
                        font_size="13sp"
                    ))


                    arquivos_ids = comunicado.get('arquivos_id', [])
                    if arquivos_ids:
                        from kivymd.uix.button import MDRaisedButton
                        from kivy.uix.modalview import ModalView
                        from kivymd.uix.boxlayout import MDBoxLayout
                        from kivy.uix.image import Image
                        from utils.file_manager import get_file
                        import tempfile

                        def abrir_imagem(instance, arquivos_ids=[]):
                            modal = ModalView(size_hint=(0.8, 0.8))
                            box = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
                            for file_id in arquivos_ids:
                                file_data = get_file(file_id)
                                if file_data and file_data['dados']:
            
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_data['nome_arquivo'].split('.')[-1]}") as temp_file:
                                        temp_file.write(file_data['dados'])
                                        temp_path = temp_file.name
                                    img = Image(source=temp_path, allow_stretch=True, keep_ratio=True)
                                    box.add_widget(img)
                            from kivymd.uix.button import MDRaisedButton
                            btn_fechar = MDRaisedButton(text="Fechar", size_hint=(1, None), height=40)
                            btn_fechar.bind(on_release=modal.dismiss)
                            box.add_widget(btn_fechar)
                            modal.add_widget(box)
                            modal.open()

                        botao_ver_imagem = MDRaisedButton(
                            text="Ver Imagem",
                            pos_hint={'center_x': 0.5}
                        )
                        botao_ver_imagem.bind(on_release=lambda instance: abrir_imagem(instance, arquivos_ids))
                        card.add_widget(botao_ver_imagem)

                    container.add_widget(card)

        if not hasattr(self, 'comunicados_modal'):
            self.comunicados_modal = MyComunicadosModal()
        self.comunicados_modal.comunicados = self.comunicados


        if hasattr(self.comunicados_modal, 'ids') and 'comunicados_container' in self.comunicados_modal.ids:
            self.comunicados_modal.ids.comunicados_container.clear_widgets()

        self.comunicados_modal.open()

    def load_comunicados(self):
        if not self.user_data:
            self.comunicados = []
            return

        user_id = self.user_data['id']
        query_user_creation = """
            SELECT created_at FROM Morador WHERE usuarios_id = %s
        """
        result_creation = db.execute_query(query_user_creation, (user_id,))
        if result_creation and 'created_at' in result_creation[0]:
            user_creation_date = result_creation[0]['created_at']
        else:
            user_creation_date = None

        query = """
            SELECT titulo, mensagem as mensagem, arquivos_id, to_char(data_publicacao, 'DD/MM/YYYY') as data
            FROM Comunicado
            WHERE usuario_id IN (
                SELECT usuarios_id FROM Sindico
            )
        """
        if user_creation_date:
            query += " AND data_publicacao >= %s "

        query += """
            ORDER BY data_publicacao DESC
            LIMIT 10
        """

        params = []
        if user_creation_date:
            params.append(user_creation_date)

        result = db.execute_query(query, tuple(params))

        print(f"[DEBUG] Comunicados carregados: {len(result) if result else 0}")
        if result:
            self.comunicados = result
        else:
            self.comunicados = []


    def set_user(self, email):
        self.user_email = email
        self.load_user_data()
        self.load_ocorrencias()
        self.load_reservas()
        self.load_comunicados()
        self.load_notificacoes()
        self.update_ui()

    def open_modal_area_comum(self):
        modal = MyReservasAreaModal()
        self.reserva_area_modal = modal
        modal.open()

    def load_user_data(self):
        query = """
            SELECT u.id, u.nome, u.email, u.tipo, m.apartamento
            FROM usuarios u
            LEFT JOIN Morador m ON u.id = m.usuarios_id
            WHERE u.email = %s
        """
        result = db.execute_query(query, (self.user_email,))
        if result:
            self.user_data = result[0]

    def load_ocorrencias(self):
        if not self.user_data:
            return
        query = """
            SELECT o.titulo, o.descricao, o.status, to_char(o.data, 'DD/MM/YYYY') as data, o.fotos_id
            FROM Ocorrencia o
            WHERE o.morador_id = (
                SELECT m.usuarios_id FROM Morador m
                JOIN usuarios u ON m.usuarios_id = u.id
                WHERE u.email = %s
            )
        """
        result = db.execute_query(query, (self.user_email,))

        print(f"[DEBUG] Ocorrências carregadas: {len(result) if result else 0}")
        if result:
            self.ocorrencias = result
        else:
            self.ocorrencias = []

    def load_reservas(self):
        if not self.user_data:
            return
        query = """
            SELECT area, to_char(data_inicio, 'DD/MM/YYYY') as data_inicio, to_char(data_fim, 'DD/MM/YYYY') as data_fim, horario, status, motivo
            FROM Reserva
            WHERE morador_id = (
                SELECT usuarios_id FROM Morador WHERE usuarios_id = (
                    SELECT id FROM usuarios WHERE email = %s
                )
            )
        """
        result = db.execute_query(query, (self.user_email,))

        print(f"[DEBUG] Reservas carregadas: {len(result) if result else 0}")
        if result:
            self.reservas = [dict(row) for row in result]
        else:
            self.reservas = []

    def open_modal_suas_reservas(self):
        self.load_reservas()
        modal = MyReservasModal()
        container = modal.ids.reservas_container
        container.clear_widgets()
        if not self.reservas:
            from kivymd.uix.label import MDLabel
            container.add_widget(MDLabel(
                text="Nenhuma reserva no momento",
                halign="center",
                theme_text_color="Secondary"
            ))
        else:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            for reserva in self.reservas:
                card = MDCard(
                    orientation='vertical',
                    padding=10,
                    radius=[12],
                    size_hint_y=None,
                    height=160,
                    md_bg_color=(0.95, 0.95, 0.95, 1)
                )
                area = reserva.get('area', '')
                data_inicio = reserva.get('data_inicio', '')
                data_fim = reserva.get('data_fim', '')
                status = reserva.get('status', '')
                motivo = reserva.get('motivo', '')
                card.add_widget(MDLabel(
                    text=f"Área: {area}",
                    font_style="Subtitle1",
                    theme_text_color="Primary",
                ))
                card.add_widget(MDLabel(
                    text=f"Data Início: {data_inicio}",
                    theme_text_color="Secondary",
                ))
                card.add_widget(MDLabel(
                    text=f"Data Fim: {data_fim}",
                    theme_text_color="Secondary",
                ))
                if status.lower() in ['aprovada', 'rejeitada']:
                    from kivy.uix.widget import Widget
                    card.add_widget(Widget(size_hint_y=None, height=5))
                    card.add_widget(MDLabel(
                        text="Motivo:",
                        theme_text_color="Secondary",
                        font_style="Caption",
                        size_hint_y=None,
                        height=20,
                    ))
                    card.add_widget(MDLabel(
                        text=f"{motivo}",
                        theme_text_color="Secondary",
                        font_style="Caption",
                        size_hint_y=None,
                        height=20,
                    ))
                    card.add_widget(Widget(size_hint_y=None, height=5))
                card.add_widget(MDLabel(
                    text=f"Status: {status}",
                    theme_text_color="Hint",
                    font_style="Caption"
                ))
                container.add_widget(card)
        modal.open()

    def update_ui(self):

        if not self.user_data:
            return

        nome = self.user_data.get('nome', '')
        tipo = self.user_data.get('tipo', '')
        apartamento = self.user_data.get('apartamento', '')
        perfil_text = f"Nome: {nome}\\nTipo: {tipo}"
        if tipo.lower() == 'morador' and apartamento:
            perfil_text += f"\\nApartamento: {apartamento}"
        if 'profile_info' in self.ids:
            self.ids.profile_info.text = perfil_text


        if 'ocorrencias_summary' in self.ids:
            abertas = sum(1 for o in self.ocorrencias if o.get('status', '').lower() == 'aberta')
            ultima = self.ocorrencias[-1]['titulo'] if self.ocorrencias else 'Nenhuma'
            self.ids.ocorrencias_summary.text = f"Abertas: {abertas}    \\  Última: {ultima}"


        if 'reservas_summary' in self.ids:
            reservas_text = "\\n".join([f"{r['area']} – {r['data_inicio']}" for r in self.reservas]) if self.reservas else "Nenhuma reserva"
            self.ids.reservas_summary.text = reservas_text


        if 'reservas_container' in self.ids:
            container = self.ids.reservas_container
            container.clear_widgets()
            if not self.reservas:
                from kivymd.uix.label import MDLabel
                container.add_widget(MDLabel(
                    text="Nenhuma reserva no momento",
                    halign="center",
                    theme_text_color="Secondary"
                ))
            else:
                from kivymd.uix.card import MDCard
                from kivymd.uix.label import MDLabel
                for reserva in self.reservas:
                    card = MDCard(
                        orientation='vertical',
                        padding=10,
                        radius=[12],
                        size_hint_y=None,
                        height=120,
                        md_bg_color=(0.95, 0.95, 0.95, 1)
                    )
                    area = reserva.get('area', '')
                    data_inicio = reserva.get('data_inicio', '')
                    data_fim = reserva.get('data_fim', '')
                    horario = reserva.get('horario', '')
                    status = reserva.get('status', '')
                    card.add_widget(MDLabel(
                        text=f"Área: {area}",
                        font_style="Subtitle1",
                        theme_text_color="Primary"
                    ))
                    card.add_widget(MDLabel(
                        text=f"Data Início: {data_inicio}",
                        theme_text_color="Secondary"
                    ))
                    card.add_widget(MDLabel(
                        text=f"Data Fim: {data_fim}",
                        theme_text_color="Secondary"
                    ))
                    card.add_widget(MDLabel(
                        text=f"Horário: {horario}",
                        theme_text_color="Secondary"
                    ))
                    card.add_widget(MDLabel(
                        text=f"Status: {status}",
                        theme_text_color="Hint",
                        font_style="Caption"
                    ))
                    container.add_widget(card)

    def load_notificacoes(self):
        if not self.user_data:
            return

        user_id = self.user_data['id']
        query_user_creation = """
            SELECT created_at FROM Morador WHERE usuarios_id = %s
        """
        result_creation = db.execute_query(query_user_creation, (user_id,))
        if result_creation and 'created_at' in result_creation[0]:
            user_creation_date = result_creation[0]['created_at']
        else:
            user_creation_date = None

        base_query = """
            SELECT n.titulo, n.mensagem, n.arquivos_id, n.data, n.tipo, n.id as notificacao_id
            FROM (
                SELECT titulo, mensagem, arquivos_id, data_publicacao as data, 'comunicado' as tipo, id
                FROM comunicado
                WHERE usuario_id IN (
                    SELECT usuarios_id FROM sindico
                )
        """

        params = []
        if user_creation_date:
            base_query += " AND data_publicacao >= %s "
            params.append(user_creation_date)

        base_query += """
                UNION ALL
                SELECT
                    'Status da Reserva' as titulo,
                    CONCAT('Sua reserva para ', r.area, ' foi atualizada para: ', r.status) as mensagem,
                    NULL as arquivos,
                    r.data_inicio as data,
                    'reserva' as tipo,
                    r.id
                FROM Reserva r
                JOIN Morador m ON r.morador_id = m.usuarios_id
                WHERE m.usuarios_id = %s
                AND LOWER(r.status) NOT IN ('pendente')
                UNION ALL
                SELECT
                    'Status da Ocorrência' as titulo,
                    CONCAT('Sua ocorrência "', o.titulo, '" foi atualizada para: ', o.status) as mensagem,
                    NULL as arquivos,
                    o.data as data,
                    'ocorrencia' as tipo,
                    o.id
                FROM Ocorrencia o
                JOIN Morador m ON o.morador_id = m.usuarios_id
                WHERE m.usuarios_id = %s
                AND LOWER(o.status) NOT IN ('aberta', 'pendente')
            ) n
            LEFT JOIN NotificationReadStatus r ON r.user_id = %s AND r.notification_type = n.tipo AND r.notification_id = n.id
            WHERE r.read_status IS NULL OR r.read_status = FALSE
            ORDER BY n.data DESC
            LIMIT 10
        """

        params.extend([user_id, user_id, user_id])

        result = db.execute_query(base_query, tuple(params))

        print(f"[DEBUG] Notificações carregadas: {len(result) if result else 0}")
        if result:
            self.notificacoes = result
        else:
            self.notificacoes = []

        self.new_notifications_count = len(self.notificacoes)

    def refresh_comunicados(self):
        self.load_notificacoes()
        self.update_ui()

    def update_ui(self):

        if not self.user_data:
            return

        nome = self.user_data.get('nome', '')
        tipo = self.user_data.get('tipo', '')
        apartamento = self.user_data.get('apartamento', '')
        perfil_text = f"Nome: {nome}\\nTipo: {tipo}"
        if tipo.lower() == 'morador' and apartamento:
            perfil_text += f"\\nApartamento: {apartamento}"
        if 'profile_info' in self.ids:
            self.ids.profile_info.text = perfil_text


        if 'ocorrencias_summary' in self.ids:
            abertas = sum(1 for o in self.ocorrencias if o.get('status', '').lower() == 'aberta')
            ultima = self.ocorrencias[-1]['titulo'] if self.ocorrencias else 'Nenhuma'
            self.ids.ocorrencias_summary.text = f"Abertas: {abertas}    \\  Última: {ultima}"


        if 'reservas_summary' in self.ids:
            reservas_text = "\\n".join([f"{r['area']} – {r['data_inicio']}" for r in self.reservas]) if self.reservas else "Nenhuma reserva"
            self.ids.reservas_summary.text = reservas_text


        if 'reservas_container' in self.ids:
            container = self.ids.reservas_container
            container.clear_widgets()
            if not self.reservas:
                from kivymd.uix.label import MDLabel
                container.add_widget(MDLabel(
                    text="Nenhuma reserva no momento",
                    halign="center",
                    theme_text_color="Secondary"
                ))
            else:
                from kivymd.uix.card import MDCard
                from kivymd.uix.label import MDLabel
                for reserva in self.reservas:
                    card = MDCard(
                        orientation='vertical',
                        padding=10,
                        radius=[12],
                        size_hint_y=None,
                        height=120,
                        md_bg_color=(0.95, 0.95, 0.95, 1)
                    )
                    area = reserva.get('area', '')
                    data_inicio = reserva.get('data_inicio', '')
                    data_fim = reserva.get('data_fim', '')
                    status = reserva.get('status', '')
                    card.add_widget(MDLabel(
                        text=f"Área: {area}",
                        font_style="Subtitle1",
                        theme_text_color="Primary"
                    ))
                    card.add_widget(MDLabel(
                        text=f"Data Início: {data_inicio}",
                        theme_text_color="Secondary"
                    ))
                    card.add_widget(MDLabel(
                        text=f"Data Fim: {data_fim}",
                        theme_text_color="Secondary"
                    ))
                    card.add_widget(MDLabel(
                        text=f"Status: {status}",
                        theme_text_color="Hint",
                        font_style="Caption"
                    ))
                    container.add_widget(card)


        if 'comunicados_summary' in self.ids:
            if self.notificacoes and len(self.notificacoes) > 0:
                latest = self.notificacoes[0]
                comunicados_text = f"Último comunicado: {latest['titulo']} - {latest['data']}"
            else:
                comunicados_text = "Nenhum comunicado"
            self.ids.comunicados_summary.text = comunicados_text

    def open_modal_perfil(self):
        import logging
        logging.info("Attempting to open profile modal")
        try:
            if not self.user_data:
                logging.warning("User data not loaded, cannot open profile modal")
                return
            nome = self.user_data.get('nome', '')
            email = self.user_data.get('email', '')
            tipo = self.user_data.get('tipo', '')
            apartamento = self.user_data.get('apartamento', None)

            modal = MyPerfilModal(nome, email, tipo, apartamento)
            modal.open()
            logging.info("Profile modal opened")
        except Exception as e:
            logging.error(f"Error opening profile modal: {e}")

    def open_modal_notificacoes(self):
        if not self.user_data:
            return


        modal = MyNotificacoesModal(notificacoes=self.notificacoes)
        modal.open()


        user_id = self.user_data['id']


        try:
            if self.notificacoes:
                for notif in self.notificacoes:
                    notif_id = notif['notificacao_id']
                    notif_type = notif['tipo']
                    

                    upsert_query = """
                        INSERT INTO NotificationReadStatus (user_id, notification_type, notification_id, read_status, read_timestamp)
                        VALUES (%s, %s, %s, TRUE, NOW())
                        ON CONFLICT (user_id, notification_type, notification_id) DO UPDATE
                        SET read_status = TRUE, read_timestamp = NOW();
                    """
                    db.execute_query(upsert_query, (user_id, notif_type, notif_id))
                

                db.connection.commit()
        except Exception as e:
            print(f"Error marking notifications as read: {e}")
            db.connection.rollback()


        self.new_notifications_count = 0

    def open_modal_minhas_ocorrencias(self):

        modal = MyOcorrenciasModal(ocorrencias=self.ocorrencias)
        modal.open()

    def open_modal_registrar_ocorrencias(self):

        if not hasattr(self, 'registrar_ocorrencia_modal'):
            self.registrar_ocorrencia_modal = RegistrarOcorrenciaModal()
        

        self.registrar_ocorrencia_modal.ids.imagem_preview.source = ''
        self.registrar_ocorrencia_modal.selected_image_path = None
        

        self.registrar_ocorrencia_modal.ids.titulo_ocorrencia.text = ''
        self.registrar_ocorrencia_modal.ids.descricao_ocorrencia.text = ''
        self.registrar_ocorrencia_modal.ids.data_ocorrencia.text = ''

        self.registrar_ocorrencia_modal.open()


class MyOcorrenciasModal(ModalView):
    ocorrencias = []

    def __init__(self, ocorrencias=None, **kwargs):
        super().__init__(**kwargs)
        if ocorrencias is None:
            self.ocorrencias = []
        else:
            self.ocorrencias = ocorrencias

    def on_open(self):
        container = self.ids.ocorrencias_container
        container.clear_widgets()

        if not self.ocorrencias:
            from kivymd.uix.label import MDLabel
            container.add_widget(MDLabel(
                text="Nenhuma ocorrência registrada.",
                halign="center",
                theme_text_color="Secondary"
            ))
            return

        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel

        for ocorrencia in self.ocorrencias:
            card = MDCard(
                orientation='vertical',
                padding=10,
                radius=[12],
                size_hint_y=None,
                height=150,
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )

            card.add_widget(MDLabel(
                text=f"Título: {ocorrencia.get('titulo', '')}",
                font_style="Subtitle1",
                theme_text_color="Primary"
            ))
            card.add_widget(MDLabel(
                text=f"Descrição: {ocorrencia.get('descricao', '')}",
                theme_text_color="Secondary"
            ))
            card.add_widget(MDLabel(
                text=f"Data: {ocorrencia.get('data', '')}",
                theme_text_color="Secondary",
                font_size="12sp"
            ))
            card.add_widget(MDLabel(
                text=f"Status: {ocorrencia.get('status', '')}",
                theme_text_color="Hint",
                font_style="Caption"
            ))

            container.add_widget(card)


    def open_modal_registrar_ocorrencias(self):
        modal = RegistrarOcorrenciaModal()
        modal.open()

    def open_modal_area_comum(self):
        modal = MyReservasAreaModal()
        modal.open()

    def open_modal(self):
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDRaisedButton
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.uix.modalview import ModalView

        class MyComunicadosModal(ModalView):
            def __init__(self, comunicados=[], **kwargs):
                super().__init__(**kwargs)
                self.comunicados = comunicados

            def on_open(self):
                container = self.ids.comunicados_container
                container.clear_widgets()

                if not self.comunicados:
                    container.add_widget(MDLabel(
                        text="Nenhum comunicado no momento.",
                        halign="center",
                        theme_text_color="Secondary"
                    ))
                    return

                for comunicado in self.comunicados:
                    card = MDCard(
                        orientation='vertical',
                        padding=10,
                        radius=[12],
                        size_hint_y=None,
                        height=140,
                        md_bg_color=(0.95, 0.95, 0.95, 1)
                    )
                    card.add_widget(MDLabel(
                        text=f"{comunicado.get('titulo', '')}",
                        font_style="Subtitle1",
                        theme_text_color="Primary"
                    ))
                    card.add_widget(MDLabel(
                        text=f"Data: {comunicado.get('data', '')}",
                        theme_text_color="Secondary",
                        font_size="12sp"
                    ))
                    card.add_widget(MDLabel(
                        text=f"{comunicado.get('mensagem', '')}",
                        theme_text_color="Secondary",
                        font_size="13sp"
                    ))
                    container.add_widget(card)

        if not hasattr(self, 'comunicados_modal'):
            self.comunicados_modal = MyComunicadosModal()
        self.comunicados_modal.comunicados = self.comunicados
        self.comunicados_modal.open()

        