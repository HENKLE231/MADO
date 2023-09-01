import tkinter as tk
from tkinter import font
from multiprocessing import Queue


class RootWindow:
    def __init__(self):
        # RootWindow.
        # Variáveis.
        self.window = tk.Tk()
        self.title = 'Mangá Downloader'
        self.window.title(self.title)
        self.browser_handle = 0
        self.queue = Queue()
        self.download_process = None
        self.default_padx = 2
        self.default_pady = 2
        self.previous_frame = ''
        self.current_frame = ''
        self.app_frames = {}
        self.config_fields = {}

        # Configuração de fonte.
        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family='Verdana', size=9)

    def switch_frame(self, next_frame):
        """
            Exibe o frame requerido.
        """
        if next_frame == 'confirmation_frame':
            self.previous_frame = self.current_frame

        # Esconde frame atualmente exibido.
        if self.current_frame:
            self.app_frames[self.current_frame].grid_forget()

        # Exibe o frame requerido.
        self.app_frames[next_frame].grid()

        # Salva o nome do frame atual.
        self.current_frame = next_frame

    def save_config_changes(self):
        """
            Salva variáveis de configuração.
        """
        # # Instancia a classe de Configurações.
        # config_ma = ConfigManager()
        #
        # # Varre os campos.
        # for config_name, widgets in self.config_fields.items():
        #     # Edita a configuração.
        #     config_ma.edit_config(config_name, widgets['var'].get())
        #
        # # Salva.
        # config_ma.save_configs()
        # TODO: ALTERAR
        pass

    def save_last_link(self, link):
        """
            :param link: (String) Link do último capítulo acessado.
            Salva o link do último capítulo acessado.
        """
        # Edita o campo.
        self.config_fields['last_link']['var'].set(link)

        # Salva as configurações.
        self.save_config_changes()

    def save_browser_handle(self, handle):
        """
            :param handle: (String) identificador da janela do navegador.
            Salva o identificador do navegador.
        """
        self.browser_handle = handle

    def highlight_fields(self, configs_and_warnings):
        """
            :param configs_and_warnings: (Dict) Dicionário com os nomes das variáveis como chaves e
            avisos como valores.
            Destaca campos com informações incorretas.
        """
        target_frame = 'home_frame'
        target_config_name = ''

        # Varre avisos.
        for config_name, warning in configs_and_warnings.items():
            # Seleciona campo.
            field = self.config_fields[config_name]

            # Verifica se o config_frame deverá ser exibido.
            if field['display_frame'] == 'config_frame':
                target_frame = 'config_frame'
                # Se for a primeira configação errada, salva para requisição de foco.
                if not target_config_name:
                    target_config_name = config_name

            # Destaca campo e exibe aviso.
            field['warning_label']['text'] = warning
            field['border']['bg'] = 'red'
            field['warning_label'].grid(row=0, column=0)

        # Se ainda não preechido, encontra o primeiro campo a receber aviso no home_frame.
        if not target_config_name:
            target_frame = 'home_frame'
            for config_name in configs_and_warnings.keys():
                # Seleciona campo.
                field = self.config_fields[config_name]
                if field['display_frame'] == 'home_frame':
                    target_config_name = config_name
                    break

        # Exibe o frame alvo.
        self.switch_frame(target_frame)

        # Seleciona campo.
        field = self.config_fields[target_config_name]

        # Foca no final do primeiro campo.
        field['entry'].focus_set()
        info_length = len(field['var'].get())
        field['entry'].icursor(info_length)

    def unhighlight(self):
        """
            Remove destaque de todos os campos.
        """
        # Varre os campos de configuração.
        for field in self.config_fields.values():
            # Remove destaque do campo.
            field['border']['bg'] = 'white'
            field['warning_label']['text'] = ''
            field['warning_label'].grid_forget()

    def update_all_fields(self):
        """
            Atualiza todos os campos de configurações.
        """
        # config_ma = ConfigManager()
        # for config_name, field in self.config_fields.items():
        #     field['var'].set(config_ma.config_list[config_name])
        # TODO: ALTERAR
        pass
