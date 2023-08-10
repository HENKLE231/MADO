import tkinter as tk
from tkinter import scrolledtext
from tkinter.filedialog import askdirectory
from functools import partial
from multiprocessing import Process, Queue
from Config import Config
from SystemManager import SystemManipulator as SystemMa
from PendingFunctionsManager import PendingFunctionsManager as PFM
from Core import Core


class RootWindow:
    def __init__(self, title):
        """
            :param title: (String) Título da janela.
        """

        # Cria janela principal.
        self.window = tk.Tk()
        self.window.title(title)
        self.title = title

        # Cria variáveis.
        self.subprocess_id = None
        self.default_padx = 2
        self.default_pady = 2
        self.previous_window = 'home_window'
        self.current_window = ''
        self.app_windows = {}
        self.widgets_with_warnings = {}
        self.all_config_widgets = {}

    def switch_to_window(self, next_window):
        """
            :param next_window: (String) Nome da próxima janela.
            Exibe a janela requerida.
        """

        # Salva o nome da página anterior caso seja necessário voltar.
        self.previous_window = self.current_window

        # Se há uma página sendo exibida, esconde ela.
        if self.current_window:
            self.app_windows[self.current_window].grid_forget()

        # Exibe a janela requerida.
        self.app_windows[next_window].grid()

        # Salva o nome da janela Atual
        self.current_window = next_window

    def update_all_fields(self):
        """
            Atualiza todos os campos de configurações.
        """
        config = Config()
        for key in self.all_config_widgets.keys():
            self.all_config_widgets[key].set(config.get_config(key))

    def highlight_fields(self, wrong_configs):
        """
            :param wrong_configs: (Dict) Dicionário com os nomes das variáveis dos campos como chaves e
            as frases de alerta como valores.
            Destaca campos com informações incorretas ou ausentes.
        """
        config = Config()
        missing_in_home = False
        widget = None
        first_widget = None
        first_wrong_config = ''

        for wrong_config in wrong_configs.keys():
            if wrong_config in self.widgets_with_warnings['home_window'].keys():
                # Salva que há informações faltando na home, para mostrar ela antes de outra janela.
                if not missing_in_home:
                    missing_in_home = True
                # Salva como campo com erro na home.
                widget = self.widgets_with_warnings['home_window'][wrong_config]
            elif wrong_config in self.widgets_with_warnings['config_window'].keys():
                # Salva como campo com erro na janela de configurações.
                widget = self.widgets_with_warnings['config_window'][wrong_config]

            # Exibe texto de aviso
            widget['warning_label']['text'] = wrong_configs[wrong_config]
            widget['border']['bg'] = 'red'
            widget['warning_label'].grid(row=0, column=0)

            # Se for o primeiro campo com erro, salva para requisição de foco.
            if not first_widget:
                first_widget = widget
                first_wrong_config = wrong_config

        # Se não há campos com erro na home, exibe a janela de configurações.
        if not missing_in_home:
            self.switch_to_window('config_window')

        # Foca no final do primeiro campo com erro.
        first_widget['entry'].focus_set()
        len_of_previous_info = len(config.get_config(first_wrong_config))
        first_widget['entry'].icursor(len_of_previous_info)

    def unhighlight(self):
        """
            Remove destaque de todos os campos.
        """

        # Seleciona todos os campos.
        widgets = []
        for key in self.widgets_with_warnings['home_window'].keys():
            widgets.append(self.widgets_with_warnings['home_window'][key])
        for key in self.widgets_with_warnings['config_window'].keys():
            widgets.append(self.widgets_with_warnings['config_window'][key])

        # Remove destaque dos campos
        for widget in widgets:
            widget['border']['bg'] = 'white'
            widget['warning_label']['text'] = ''
            widget['warning_label'].grid_forget()


class HomeWindow:
    def __init__(self, parent, queue, info_window):
        """
            :param parent: (RootWindow) Instância da RootWindow.
            :param queue: (Queue) Instância da Queue.
            :param info_window: (InfoWindow) Instância da InfoWindow.
        """

        # Instancia a classe de configurações.
        config = Config()

        # Cria o Home.
        self.window = tk.Frame(parent.window)

        # Cria variáveis simples.
        self.var_initial_chapter = tk.StringVar()
        self.var_final_chapter = tk.StringVar()

        # Atribui valores.
        self.var_initial_chapter.set(config.get_config('initial_chapter'))
        self.var_final_chapter.set(config.get_config('final_chapter'))

        # Cria variáveis de widgets marcáveis.
        self.var_download = tk.BooleanVar(value=config.get_config('download'))
        self.var_transfer = tk.BooleanVar(value=config.get_config('transfer'))
        self.var_delete_chapters = tk.BooleanVar(value=config.get_config('delete_chapters'))
        self.var_final_dir = tk.StringVar(value=config.get_config('final_dir'))

        # Cria widgets.
        # Linha 0.
        self.label_manga_name = tk.Label(self.window, text='Home', font=24)
        self.label_manga_name.grid(row=0, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

        # Linha 1.
        self.label_initial_chapter = tk.Label(self.window, text='Capítulo Inicial:', anchor='e')
        self.label_initial_chapter.grid(row=1, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_initial_chapter = tk.Frame(self.window)
        self.frame_initial_chapter.columnconfigure(0, weight=1)
        self.frame_initial_chapter.grid(row=1, column=1, columnspan=2, padx=5, sticky='we')
        self.label_initial_chapter_warning = tk.Label(self.frame_initial_chapter, text='', fg='red')
        self.border_initial_chapter = tk.Frame(self.frame_initial_chapter)
        self.border_initial_chapter.columnconfigure(0, weight=1)
        self.border_initial_chapter.grid(row=1, column=0, sticky='nswe')
        self.entry_initial_chapter = tk.Entry(self.border_initial_chapter, textvariable=self.var_initial_chapter)
        self.entry_initial_chapter.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')

        # Linha 2.
        self.label_final_chapter = tk.Label(self.window, text='Capítulo Final:', anchor='e')
        self.label_final_chapter.grid(row=2, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_final_chapter = tk.Frame(self.window)
        self.frame_final_chapter.columnconfigure(0, weight=1)
        self.frame_final_chapter.grid(row=2, column=1, columnspan=2, padx=5, sticky='we')
        self.label_final_chapter_warning = tk.Label(self.frame_final_chapter, text='', fg='red')
        self.border_final_chapter = tk.Frame(self.frame_final_chapter)
        self.border_final_chapter.columnconfigure(0, weight=1)
        self.border_final_chapter.grid(row=1, column=0, sticky='nswe')
        self.entry_final_chapter = tk.Entry(self.border_final_chapter, textvariable=self.var_final_chapter)
        self.entry_final_chapter.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')

        # Linha 3.
        self.checkbox_download = tk.Checkbutton(self.window, text='Baixar', variable=self.var_download)
        self.checkbox_download.grid(row=3, column=0)
        self.checkbox_transfer = tk.Checkbutton(
            self.window, text='Transferir', variable=self.var_transfer, command=self.manage_transfer_options
        )
        self.checkbox_transfer.grid(row=3, column=1)
        self.checkbox_delete_chapters = tk.Checkbutton(
            self.window, text='Excluir capítulos\nno Diretorio final', variable=self.var_delete_chapters
        )
        self.checkbox_delete_chapters.grid(row=3, column=2)

        # Linha 4.
        text = 'Obs: Exclusões realizadas no celular ou drive limpam a pasta.'
        self.label_delete_warning = tk.Label(self.window, text=text)
        self.label_delete_warning.grid(row=4, column=0, columnspan=3, padx=10, sticky='nswe')

        # Linha 5.
        self.label_final_dir = tk.Label(self.window, text='Diretorio Final')
        self.label_final_dir.grid(row=5, column=0, columnspan=3, padx=10, sticky='nswe')

        # Linha 6.
        self.radiobutton_phone_option = tk.Radiobutton(
            self.window, text='Celular', variable=self.var_final_dir, value='Celular'
        )
        self.radiobutton_phone_option.grid(row=6, column=0)
        self.radiobutton_pc_dir_option = tk.Radiobutton(
            self.window, text='Computador', variable=self.var_final_dir, value='PC'
        )
        self.radiobutton_pc_dir_option.grid(row=6, column=1)
        self.radiobutton_google_drive_option = tk.Radiobutton(
            self.window, text='Google Drive', variable=self.var_final_dir, value='Google Drive'
        )
        self.radiobutton_google_drive_option.grid(row=6, column=2)

        # Linha 7.
        command = partial(self.delete_downloaded_chapters, parent, info_window)
        self.button_config = tk.Button(
            self.window, text='Excluir capítulos\nbaixados', command=command
        )
        self.button_config.grid(row=7, column=0, padx=3, pady=3, sticky='nswe')
        command = partial(parent.switch_to_window, 'config_window')
        self.button_config = tk.Button(self.window, text='Configurações', command=command)
        self.button_config.grid(row=7, column=1, padx=3, pady=3, sticky='nswe')
        command = partial(self.verify_for_run, queue, parent, info_window)
        self.button_run = tk.Button(self.window, text='Executar', command=command)
        self.button_run.grid(row=7, column=2, padx=3, pady=3, sticky='nswe')

        # Atualiza a disponibilidade das opções de transferência.
        self.manage_transfer_options()

        # Adiciona a lista de widgets que podem ser destacados.
        parent.widgets_with_warnings['home_window'] = {
            'initial_chapter': {
                'warning_label': self.label_initial_chapter_warning,
                'border': self.border_initial_chapter,
                'entry': self.entry_initial_chapter,
                'var': self.var_initial_chapter
            },
            'final_chapter': {
                'warning_label': self.label_final_chapter_warning,
                'border': self.border_final_chapter,
                'entry': self.entry_final_chapter,
                'var': self.var_final_chapter
            }
        }

        # Salva como widget existente.
        parent.all_config_widgets['initial_chapter'] = self.var_initial_chapter
        parent.all_config_widgets['final_chapter'] = self.var_final_chapter
        parent.all_config_widgets['download'] = self.var_download
        parent.all_config_widgets['transfer'] = self.var_transfer
        parent.all_config_widgets['delete_chapters'] = self.var_delete_chapters
        parent.all_config_widgets['final_dir'] = self.var_final_dir

        # Adiciona à lista de janelas existentes.
        parent.app_windows['home_window'] = self.window

    def manage_transfer_options(self):
        """
            Atualiza disponibilidade das opções de transferência, habilitando ou desabilitando a marcação.
        """
        # Seleciona os widgets.
        widgets = [
            self.checkbox_delete_chapters,
            self.label_delete_warning,
            self.label_final_dir,
            self.radiobutton_phone_option,
            self.radiobutton_pc_dir_option,
            self.radiobutton_google_drive_option
        ]

        # Verifica se a transferencia foi selecionada.
        if self.var_transfer.get():
            new_state = 'normal'
        else:
            new_state = 'disable'

        # Muda o estado dos widgets.
        for widget in widgets:
            widget['state'] = new_state

    def save_config_changes(self):
        """
            Salva variáveis da janela.
        """

        # Instacia a classe de configurações.
        config = Config()

        # Seleciona os valores dos campos.
        configs_to_save = {
            'initial_chapter': self.var_initial_chapter.get(),
            'final_chapter': self.var_final_chapter.get(),
            'download': self.var_download.get(),
            'transfer': self.var_transfer.get(),
            'delete_chapters': self.var_delete_chapters.get(),
            'final_dir': self.var_final_dir.get()
        }

        # Edita as configurações.
        for key in configs_to_save.keys():
            config.edit_config(key, configs_to_save[key])

        # Salva as configurações.
        config.save_configs()

    @staticmethod
    def delete_downloaded_chapters(parent, info_window):
        """
            :param parent: (RootWindow) Instância da RootWindow.
            :param info_window: (InfoWindow) Instância da InfoWindow.
        """

        # Instancia a classe de Configurações.
        config = Config()

        # Verifica o número de capítulos armazenados.
        num_files = SystemMa.how_many_files(config.chapters_dir)

        if num_files == 0:
            # Monta frase de aviso, onde que não capítulos.
            deletion_status = ['Não há capítulos baixados para excluir.']
        else:
            # Deleta capítulos.
            SystemMa.clear_dirs([config.chapters_dir])

            if num_files == 1:
                # Monta frase de aviso, onde há 1 exclusão.
                deletion_status = [
                    'Exclusão de capítulo realizada com sucesso!',
                    'Foi excluído 1 arquivo.'
                ]
            else:
                # Monta frase de aviso, onde há várias exclusões.
                deletion_status = [
                    'Exclusão de capítulos realizada com sucesso!',
                    f'Foram excluídos {num_files} arquivos.'
                ]

        # Exibe página de informações com o estado da exclusão.
        parent.switch_to_window('info_window')
        info_window.show_info(deletion_status, 'Exclusão')

    def verify_for_run(self, queue, parent, info_window):
        """
            :param queue: (Queue) Instância da Queue.
            :param parent: (RootWindow) Instância da RootWindow.
            :param info_window: (InfoWindow) Instância da InfoWindow.
            Verifica se há as informações necessárias para realizar as funções selecionadas.
        """
        # Salva variáveis da janela.
        self.save_config_changes()

        # Instancia classes necessárias.
        config = Config()
        system_ma = SystemMa()

        # Carrega configurações salvas.
        configs_dict = config.get_configs_dict()
        wrong_configs = {}
        download = configs_dict['download']
        transfer = configs_dict['transfer']

        if download or transfer:
            # Verifica configurações necessárias para download.
            if download:
                # Nome do mangá
                if not configs_dict['manga_name']:
                    wrong_configs['manga_name'] = 'Informe o nome do mangá.'

                if not configs_dict['base_link']:
                    wrong_configs['base_link'] = 'Informe o link base.'

                # Capitulo inicial e final.
                are_numerical = True
                if not configs_dict['initial_chapter']:
                    wrong_configs['initial_chapter'] = 'Informe o nº do capítulo.'
                else:
                    if not configs_dict['initial_chapter'].isnumeric():
                        are_numerical = False
                        wrong_configs['initial_chapter'] = 'Informe apenas números.'

                if not configs_dict['final_chapter']:
                    wrong_configs['final_chapter'] = 'Informe o nº do capítulo.'
                else:
                    if not configs_dict['final_chapter'].isnumeric():
                        are_numerical = False
                        wrong_configs['final_chapter'] = 'Informe apenas números.'

                if configs_dict['initial_chapter'] and configs_dict['final_chapter'] and are_numerical:
                    if configs_dict['initial_chapter'] > configs_dict['final_chapter']:
                        wrong_configs['initial_chapter'] = 'Deve ser menor ou igual ao final.'

                # Pasta de imagens para reconhecimento na tela.
                if not configs_dict['imgs_dir']:
                    wrong_configs['imgs_dir'] = 'Informe a pasta de imagens para reconhecimento.'
                elif not system_ma.path_exist(configs_dict['imgs_dir']):
                    wrong_configs['imgs_dir'] = 'Informe uma pasta valida.'

                # Pasta de download quando usando chrome.
                if not configs_dict['download_dir']:
                    wrong_configs['download_dir'] = 'Informe a pasta de download do chrome.'
                elif not system_ma.path_exist(configs_dict['download_dir']):
                    wrong_configs['download_dir'] = 'Informe uma pasta valida.'

                # Pasta de para edição de arquivos.
                if not configs_dict['files_dir']:
                    wrong_configs['files_dir'] = 'Informe uma pasta para edição de imagens.'
                elif not system_ma.path_exist(configs_dict['files_dir']):
                    wrong_configs['files_dir'] = 'Informe uma pasta valida.'

                # Pasta onde serão compilados os capítulos.
                if not configs_dict['chapters_dir']:
                    wrong_configs['chapters_dir'] = 'Informe uma pasta para compilação dos capítulos.'
                elif not system_ma.path_exist(configs_dict['chapters_dir']):
                    wrong_configs['chapters_dir'] = 'Informe uma pasta valida.'

            # Verifica configurações necessárias para transferência.
            if transfer:
                # Diretório final da transferência e o seu respetivo caminho.
                if configs_dict['final_dir'] == 'Celular' and not configs_dict['phone_dir']:
                    wrong_configs['phone_dir'] = 'Informe uma pasta do celular.'
                elif configs_dict['final_dir'] == 'PC' and not configs_dict['pc_dir']:
                    wrong_configs['pc_dir'] = 'Informe uma pasta do computador.'
                elif configs_dict['final_dir'] == 'Google Drive' and not configs_dict['drive_url']:
                    wrong_configs['drive_url'] = 'Informe o link de uma pasta no Google drive.'

                # Pasta onde são compilados os capítulos.
                if not configs_dict['chapters_dir']:
                    wrong_configs['chapters_dir'] = 'Informe uma pasta para compilação dos capítulos.'
                elif not system_ma.path_exist(configs_dict['chapters_dir']):
                    wrong_configs['chapters_dir'] = 'Informe uma pasta valida.'
                elif not download and not system_ma.file_with_pattern_exists(configs_dict['chapters_dir']):
                    parent.switch_to_window('info_window')
                    warning = [
                        'Não há capítulos para transferir.',
                        'Baixe alguns.'
                    ]
                    info_window.clear_info()
                    info_window.show_info(warning, 'Erro!')
                    return

            # Tira o destaque dos campos.
            parent.unhighlight()

            if wrong_configs:
                # Destaca campos com erro.
                parent.highlight_fields(wrong_configs)
            else:
                # Salva posição da janela.
                set_gui_initial_point(get_current_gui_initial_point(parent.title))

                # Atribui a lista de funções pendentes a função de criar janela.
                PFM.add_pending_function(queue, ['create_gui', download, transfer])

                # Destrói janela atual.
                parent.window.destroy()


class ConfigWindow:
    def __init__(self, parent):
        """
            :param parent: (RootWindow) Instância da RootWindow.
        """

        # Importa a classe de configurações.
        config = Config()

        # Cria a janela de Configurações.
        self.window = tk.Frame(parent.window)

        # Cria variáveis.
        self.var_manga_name = tk.StringVar()
        self.var_base_link = tk.StringVar()
        self.var_drive_url = tk.StringVar()
        self.var_phone_dir = tk.StringVar()
        self.var_pc_dir = tk.StringVar()
        self.var_imgs_dir = tk.StringVar()
        self.var_download_dir = tk.StringVar()
        self.var_files_dir = tk.StringVar()
        self.var_chapters_dir = tk.StringVar()

        # Carrega configurações.
        self.var_manga_name.set(config.get_config('manga_name'))
        self.var_base_link.set(config.get_config('base_link'))
        self.var_drive_url.set(config.get_config('drive_url'))
        self.var_phone_dir.set(config.get_config('phone_dir'))
        self.var_pc_dir.set(config.get_config('pc_dir'))
        self.var_imgs_dir.set(config.get_config('imgs_dir'))
        self.var_download_dir.set(config.get_config('download_dir'))
        self.var_files_dir.set(config.get_config('files_dir'))
        self.var_chapters_dir.set(config.get_config('chapters_dir'))

        # Cria widgets.
        # Linha 0.
        self.label_config = tk.Label(self.window, text='Configurações', font=24)
        self.label_config.grid(row=0, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

        # Linha 1.
        self.label_manga_name = tk.Label(self.window, text='Nome do Mangá:', anchor='e')
        self.label_manga_name.grid(row=1, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_manga_name = tk.Frame(self.window)
        self.frame_manga_name.columnconfigure(0, weight=1)
        self.frame_manga_name.grid(row=1, column=1, sticky='we')
        self.label_manga_name_warning = tk.Label(self.frame_manga_name, text='', fg='red')
        self.border_manga_name = tk.Frame(self.frame_manga_name)
        self.border_manga_name.columnconfigure(0, weight=1)
        self.border_manga_name.grid(row=1, column=0, sticky='nswe')
        self.entry_manga_name = tk.Entry(self.border_manga_name, textvariable=self.var_manga_name)
        self.entry_manga_name.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')

        # Linha 2.
        self.label_base_link = tk.Label(self.window, text='Link Base:', anchor='e')
        self.label_base_link.grid(row=2, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_base_link = tk.Frame(self.window)
        self.frame_base_link.columnconfigure(0, weight=1)
        self.frame_base_link.grid(row=2, column=1, sticky='we')
        self.label_base_link_warning = tk.Label(self.frame_base_link, text='', fg='red')
        self.border_base_link = tk.Frame(self.frame_base_link)
        self.border_base_link.columnconfigure(0, weight=1)
        self.border_base_link.grid(row=1, column=0, sticky='nswe')
        self.entry_base_link = tk.Entry(self.border_base_link, textvariable=self.var_base_link)
        self.entry_base_link.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')

        # Linha 3.
        self.label_drive_url = tk.Label(self.window, text='Google Drive url:', anchor='e')
        self.label_drive_url.grid(row=3, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_drive_url = tk.Frame(self.window)
        self.frame_drive_url.columnconfigure(0, weight=1)
        self.frame_drive_url.grid(row=3, column=1, sticky='we')
        self.label_drive_url_warning = tk.Label(self.frame_drive_url, text='', fg='red')
        self.border_drive_url = tk.Frame(self.frame_drive_url)
        self.border_drive_url.columnconfigure(0, weight=1)
        self.border_drive_url.grid(row=1, column=0, sticky='nswe')
        self.entry_drive_url = tk.Entry(self.border_drive_url, textvariable=self.var_drive_url)
        self.entry_drive_url.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')

        # Linha 4.
        self.label_phone_dir = tk.Label(self.window, text='Pasta no Celular:', anchor='e')
        self.label_phone_dir.grid(row=4, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_phone_dir = tk.Frame(self.window)
        self.frame_phone_dir.columnconfigure(0, weight=1)
        self.frame_phone_dir.grid(row=4, column=1, sticky='we')
        self.label_phone_dir_warning = tk.Label(self.frame_phone_dir, text='', fg='red')
        self.border_phone_dir = tk.Frame(self.frame_phone_dir)
        self.border_phone_dir.columnconfigure(0, weight=1)
        self.border_phone_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_phone_dir = tk.Entry(self.border_phone_dir, textvariable=self.var_phone_dir)
        self.entry_phone_dir.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')

        # Linha 5.
        self.label_pc_dir = tk.Label(self.window, text='Pasta no Computador:', anchor='e')
        self.label_pc_dir.grid(row=5, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_pc_dir = tk.Frame(self.window)
        self.frame_pc_dir.columnconfigure(0, weight=1)
        self.frame_pc_dir.grid(row=5, column=1, sticky='we')
        self.label_pc_dir_warning = tk.Label(self.frame_pc_dir, text='', fg='red')
        self.border_pc_dir = tk.Frame(self.frame_pc_dir)
        self.border_pc_dir.columnconfigure(0, weight=1)
        self.border_pc_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_pc_dir = tk.Entry(self.border_pc_dir, textvariable=self.var_pc_dir)
        self.entry_pc_dir.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')
        command = partial(self.select_dir, 'Selecione pasta final para transferencia.', self.var_pc_dir)
        self.button_pc_dir = tk.Button(self.window, text='Procurar', command=command)
        self.button_pc_dir.grid(row=5, column=2, padx=2, sticky='swe')

        # Linha 6.
        self.label_imgs_dir = tk.Label(self.window, text='Pasta de Imagens:', anchor='e')
        self.label_imgs_dir.grid(row=6, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_imgs_dir = tk.Frame(self.window)
        self.frame_imgs_dir.columnconfigure(0, weight=1)
        self.frame_imgs_dir.grid(row=6, column=1, sticky='we')
        self.label_imgs_dir_warning = tk.Label(self.frame_imgs_dir, text='', fg='red')
        self.border_imgs_dir = tk.Frame(self.frame_imgs_dir)
        self.border_imgs_dir.columnconfigure(0, weight=1)
        self.border_imgs_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_imgs_dir = tk.Entry(self.border_imgs_dir, textvariable=self.var_imgs_dir)
        self.entry_imgs_dir.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')
        command = partial(self.select_dir, 'Selecione pasta com as imagens de reconhecimento.', self.var_imgs_dir)
        self.button_imgs_dir = tk.Button(self.window, text='Procurar', command=command)
        self.button_imgs_dir.grid(row=6, column=2, padx=2, sticky='swe')

        # Linha 7.
        self.label_download_dir = tk.Label(self.window, text='Pasta de Download:', anchor='e')
        self.label_download_dir.grid(row=7, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_download_dir = tk.Frame(self.window)
        self.frame_download_dir.columnconfigure(0, weight=1)
        self.frame_download_dir.grid(row=7, column=1, sticky='we')
        self.label_download_dir_warning = tk.Label(self.frame_download_dir, text='', fg='red')
        self.border_download_dir = tk.Frame(self.frame_download_dir)
        self.border_download_dir.columnconfigure(0, weight=1)
        self.border_download_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_download_dir = tk.Entry(self.border_download_dir, textvariable=self.var_download_dir)
        self.entry_download_dir.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')
        command = partial(self.select_dir, 'Selecione pasta de download padrão do Chrome.', self.var_download_dir)
        self.button_download_dir = tk.Button(self.window, text='Procurar', command=command)
        self.button_download_dir.grid(row=7, column=2, padx=2, sticky='swe')

        # Linha 8.
        self.label_files_dir = tk.Label(self.window, text='Pasta de Arquivos:', anchor='e')
        self.label_files_dir.grid(row=8, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_files_dir = tk.Frame(self.window)
        self.frame_files_dir.columnconfigure(0, weight=1)
        self.frame_files_dir.grid(row=8, column=1, sticky='we')
        self.label_files_dir_warning = tk.Label(self.frame_files_dir, text='', fg='red')
        self.border_files_dir = tk.Frame(self.frame_files_dir)
        self.border_files_dir.columnconfigure(0, weight=1)
        self.border_files_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_files_dir = tk.Entry(self.border_files_dir, textvariable=self.var_files_dir)
        self.entry_files_dir.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')
        command = partial(self.select_dir, 'Selecione pasta para manipulação das imagens.', self.var_files_dir)
        self.button_files_dir = tk.Button(self.window, text='Procurar', command=command)
        self.button_files_dir.grid(row=8, column=2, padx=2, sticky='swe')

        # Linha 9.
        self.label_chapters_dir = tk.Label(self.window, text='Pasta de capítulos:', anchor='e')
        self.label_chapters_dir.grid(row=9, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_chapters_dir = tk.Frame(self.window)
        self.frame_chapters_dir.columnconfigure(0, weight=1)
        self.frame_chapters_dir.grid(row=9, column=1, sticky='we')
        self.label_chapters_dir_warning = tk.Label(self.frame_chapters_dir, text='', fg='red')
        self.border_chapters_dir = tk.Frame(self.frame_chapters_dir)
        self.border_chapters_dir.columnconfigure(0, weight=1)
        self.border_chapters_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_chapters_dir = tk.Entry(self.border_chapters_dir, textvariable=self.var_chapters_dir)
        self.entry_chapters_dir.grid(padx=parent.default_padx, pady=parent.default_pady, sticky='nswe')
        command = partial(self.select_dir, 'Selecione pasta para compilação dos capítulos.', self.var_chapters_dir)
        self.button_chapters_dir = tk.Button(self.window, text='Procurar', command=command)
        self.button_chapters_dir.grid(row=9, column=2, padx=2, sticky='swe')

        # Linha 10.
        self.bottom_buttons_frame = tk.Frame(self.window)
        self.bottom_buttons_frame.grid(row=10, column=1, padx=2)
        self.space = tk.Label(self.bottom_buttons_frame, text='')
        self.space.grid(row=0, column=0, padx=100)
        command = partial(self.reset_configs, parent)
        self.button_reset = tk.Button(self.bottom_buttons_frame, text='Configuração padrão', command=command)
        self.button_reset.grid(row=0, column=1, ipadx=20, pady=5, sticky='nswe')
        command = partial(self.save_and_switch_to_home, parent)
        self.button_back = tk.Button(self.window, text='Voltar', command=command)
        self.button_back.grid(row=10, column=2, ipadx=20, padx=2, pady=5, sticky='nswe')

        # Adiciona a lista de widgets que podem ser destacados.
        parent.widgets_with_warnings['config_window'] = {
            'manga_name': {
                'warning_label': self.label_manga_name_warning,
                'border': self.border_manga_name,
                'entry': self.entry_manga_name,
                'var': self.var_manga_name
            },
            'base_link': {
                'warning_label': self.label_base_link_warning,
                'border': self.border_base_link,
                'entry': self.entry_base_link,
                'var': self.var_base_link
            },
            'drive_url': {
                'warning_label': self.label_drive_url_warning,
                'border': self.border_drive_url,
                'entry': self.entry_drive_url,
                'var': self.var_drive_url
            },
            'phone_dir': {
                'warning_label': self.label_phone_dir_warning,
                'border': self.border_phone_dir,
                'entry': self.entry_phone_dir,
                'var': self.var_phone_dir
            },
            'pc_dir': {
                'warning_label': self.label_pc_dir_warning,
                'border': self.border_pc_dir,
                'entry': self.entry_pc_dir,
                'var': self.var_pc_dir
            },
            'imgs_dir': {
                'warning_label': self.label_imgs_dir_warning,
                'border': self.border_imgs_dir,
                'entry': self.entry_imgs_dir,
                'var': self.var_imgs_dir
            },
            'download_dir': {
                'warning_label': self.label_download_dir_warning,
                'border': self.border_download_dir,
                'entry': self.entry_download_dir,
                'var': self.var_download_dir
            },
            'files_dir': {
                'warning_label': self.label_files_dir_warning,
                'border': self.border_files_dir,
                'entry': self.entry_files_dir,
                'var': self.var_files_dir
            },
            'chapters_dir': {
                'warning_label': self.label_chapters_dir_warning,
                'border': self.border_chapters_dir,
                'entry': self.entry_chapters_dir,
                'var': self.var_chapters_dir
            }
        }

        parent.all_config_widgets['manga_name'] = self.var_manga_name
        parent.all_config_widgets['base_link'] = self.var_base_link
        parent.all_config_widgets['drive_url'] = self.var_drive_url
        parent.all_config_widgets['phone_dir'] = self.var_phone_dir
        parent.all_config_widgets['pc_dir'] = self.var_pc_dir
        parent.all_config_widgets['imgs_dir'] = self.var_imgs_dir
        parent.all_config_widgets['download_dir'] = self.var_download_dir
        parent.all_config_widgets['files_dir'] = self.var_files_dir
        parent.all_config_widgets['chapters_dir'] = self.var_chapters_dir

        # Adiciona às janelas existentes.
        parent.app_windows['config_window'] = self.window

    @staticmethod
    def select_dir(title, variable):
        """
            :param title: (String) Título da janela de seleção de pastas.
            :param variable: (tk.StringVar) Variável que vai receber o caminho.
            Abre janela para seleção de pastas e salva caminho selecionado.
        """
        # Abre janela de seleção de pastas.
        new_dir = askdirectory(title=title)

        # Se informado o caminho é atribuido a variável.
        if new_dir:
            variable.set(new_dir)

    @staticmethod
    def reset_configs(parent):
        """
            :param parent: (RootWindow) Instância da RootWindow.
            Volta o programa a suas configurações iniciais.
        """
        system_ma = SystemMa()
        system_ma.delete_config_txt()
        parent.unhighlight()
        parent.update_all_fields()

    def save_config_changes(self):
        """
            Salva variáveis da janela.
        """

        # Instancia a classe de Configurações.
        config = Config()

        # Seleciona os valores dos campos.
        configs_to_save = {
            'manga_name': self.var_manga_name.get(),
            'base_link': self.var_base_link.get(),
            'drive_url': self.var_drive_url.get(),
            'phone_dir': self.var_phone_dir.get(),
            'pc_dir': self.var_pc_dir.get(),
            'imgs_dir': self.var_imgs_dir.get(),
            'download_dir': self.var_download_dir.get(),
            'files_dir': self.var_files_dir.get(),
            'chapters_dir': self.var_chapters_dir.get()
        }

        # Edita as configurações.
        for key in configs_to_save.keys():
            config.edit_config(key, configs_to_save[key])

        # Salva as configurações.
        config.save_configs()

    def save_and_switch_to_home(self, parent):
        """
            :param parent: (RootWindow) Instância da RootWindow.
            Salva variáveis da janela e exibe a home.
        """

        # Salva variáveis.
        self.save_config_changes()

        # Exibe home.
        parent.switch_to_window('home_window')


class InfoWindow:
    def __init__(self, parent, queue):
        """
            :param parent: (RootWindow) Instância da RootWindow.
            :param queue: (Queue) Instância da Queue.
        """

        # Cria a janela de informações.
        self.window = tk.Frame(parent.window)

        # Cria variáveis.
        self.num_info_lines = 7
        self.max_char_per_line = 50
        self.button_action = 'go_back'
        self.dynamic_button_text = 'Voltar'

        # Cria widgets.
        # Linha 0.
        self.label_info_title = tk.Label(self.window)
        self.label_info_title.grid(row=0, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

        # Linha 1.
        self.scrolled_textbox = scrolledtext.ScrolledText(
            self.window, width=self.max_char_per_line, height=self.num_info_lines, cursor='arrow'
        )
        self.scrolled_textbox.grid(row=1, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

        # Linha 2.
        command = partial(self.exucute_button_action, queue, parent)
        self.button_dynamic = tk.Button(self.window, text=self.dynamic_button_text, command=command)
        self.button_dynamic.grid(row=2, column=2, padx=5, pady=5, sticky='nswe')

        # Adiciona à lista de janelas existentes.
        parent.app_windows['info_window'] = self.window

        # Verifica se há informações a serem mostradas.
        pending_functions = PFM.get_pending_functions(queue)
        if pending_functions:
            for function in pending_functions:
                if function[0] == 'show_info':
                    self.show_info(function[1], function[2])
                    PFM.remove_pending_function(queue, function)
                    break

    @staticmethod
    def interrupt_process(queue, parent, info_lines=None, info_title='Encerrado!'):
        """
            :param queue: (Queue) Instância da Queue.
            :param parent: (RootWindow) Instância da RootWindow.
            :param info_lines: (Array) Lista de strings a serem exibidas após o cessar da processo.
            :param info_title: (String) Titulo a ser exibido na janela de informações.
            Redireciona para a função global de interromper processo.
        """
        interrupt_process(queue, parent, info_lines, info_title)

    def exucute_button_action(self, queue, parent):
        """
            :param queue: (Queue) Instância da Queue.
            :param parent: (RootWindow) Instância da RootWindow.
            Executa a função do botão dinâmico.
        """
        if self.button_action == 'go_back':
            # Limpa campo de informações e volta à janela anterior.
            self.clear_info_and_go_back(parent)
        else:
            # Agenda o salvamento do ponto inicial de posicionamento do GUI.
            pending_functions = PFM.get_pending_functions(queue)
            update_scheduled = False
            if pending_functions:
                for function in pending_functions:
                    match function[0]:
                        case 'set_gui_initial_point':
                            update_scheduled = True
                            break
            if not update_scheduled:
                gui_initial_point = get_current_gui_initial_point(parent.title)
                PFM.add_pending_function(queue, ['set_gui_initial_point', gui_initial_point])
            if self.button_action == 'rebuild_main':
                # Recria o menu principal que foi destruído.
                PFM.add_pending_function(queue, ['create_main_gui', 'home_window'])
                parent.window.destroy()
            elif self.button_action == 'cancel':
                # Interrompe processo, sendo ele de download ou transferência.
                interrupt_process(queue, parent)

    def set_button_action_to_go_back(self):
        """
            Define a função do botão dinâmico para voltar à janela anterior.
        """
        self.button_action = 'go_back'
        self.button_dynamic['text'] = 'Voltar'

    def set_button_action_to_rebuild_main(self):
        """
            Define a função do botão dinâmico para reconstruir menu principal.
        """
        self.button_action = 'rebuild_main'
        self.button_dynamic['text'] = 'Voltar'

    def set_button_action_to_cancel(self):
        """
            Define a função do botão dinâmico para cancelar processo atual.
        """
        self.button_action = 'cancel'
        self.button_dynamic['text'] = 'Cancelar'

    def clear_info_and_go_back(self, parent):
        """
            :param parent: (RootWindow) Instância da RootWindow.
            Limpa campo de informações e volta à janela anterior.
        """
        self.clear_info()
        previous_window = parent.previous_window
        if not previous_window:
            previous_window = 'home_window'
        parent.switch_to_window(previous_window)

    @staticmethod
    def get_last_incident_index(text, character):
        """
            :param text: (String) Texto para análise.
            :param character: (String) Caractere para ser encontrado.
            :return: (Int) Índice do última incidencia do charactere.
        """
        last_incidence = None
        i = len(text) - 1
        while i > 0:
            if character == text[i]:
                last_incidence = i
                break
            i -= 1
        return last_incidence

    def get_index_of_what_comes_last(self, text, characters):
        """
            :param text: (String) Texto para análise.
            :param characters: (Array) Lista de caracteres para comparação.
            :return: (Int) Índice do caractere que aparece por último.
        """

        # Seleciona dos caracteres passados apenas os contidos no texto.
        characters = [char for char in characters if char in text]
        last_char_index = None
        for char in characters:
            # Verifica a ultima incidencia.
            index = self.get_last_incident_index(text, char)

            # Compara com o valor anterior, se for maior salva.
            if not last_char_index:
                last_char_index = index
            elif index > last_char_index:
                last_char_index = index
        return last_char_index

    def format_text(self, lines, max_lenght):
        """
            :param lines: (Array) Lista com as linhas de texto a serem formatadas.
            :param max_lenght: (Int) Número máximo de caracteres por linha.
            :return: (Array) Lista de linhas respeitando o comprimento máximo.
        """
        formatted_lines = []
        there_were_changes = True
        while there_were_changes:
            there_were_changes = False
            for i, line in enumerate(lines):
                line = line.strip()
                if len(line) > max_lenght:
                    there_were_changes = True
                    # Verifica onde pode cortar a linha
                    divider_index = self.get_index_of_what_comes_last(line[:max_lenght], [' ', ',', '.'])
                    if divider_index:
                        piece_that_fit = line[:divider_index + 1]
                        rest = line[divider_index + 1:]
                    else:
                        piece_that_fit = line[:max_lenght]
                        rest = line[max_lenght:]
                    # Adiciona partes cortadas
                    formatted_lines.append(piece_that_fit.strip())
                    rest = rest.strip()
                    if rest:
                        lines[i] = rest
                    else:
                        lines.pop(i)
                    break
                else:
                    # Linha está nas normas
                    formatted_lines.append(line)
        return formatted_lines

    def show_info(self, new_info_lines=None, info_title=''):
        """
            :param new_info_lines: (Array) Lista com linhas a serem exibidas.
            :param info_title: (String) Título a ser exibido na janela de informações.
            Apresenta informações na janela de informações.
        """

        # Atribui título.
        if info_title:
            self.label_info_title['text'] = info_title

        # Verifica o número de linhas exibidas.
        num_lines = len(self.get_info())

        if new_info_lines:
            # Formata texto.
            new_info_lines = self.format_text(new_info_lines, self.max_char_per_line)

            # Exibe texto.
            self.scrolled_textbox['state'] = 'normal'
            for i, line in enumerate(new_info_lines):
                if num_lines > 1 or i > 0:
                    self.scrolled_textbox.insert('end', f'\n{line}')
                else:
                    self.scrolled_textbox.insert('end', f'{line}')
            self.scrolled_textbox['state'] = 'disabled'
            self.scrolled_textbox.yview_scroll(len(new_info_lines) * 26, 'pixels')

        # Atualiza tela.
        self.window.update()

    def update_last_lines(self, info_lines, number_of_lines_to_delete=1):
        """
            :param info_lines: (Array) Lista de linhas de texto para substituir a última linha apresentada.
            :param number_of_lines_to_delete: (Int) Número de linhas que serão apagadas.
            Substitui últimas linhas exibidas.
        """

        # Verifica o número de linhas exibidas.
        num_lines = len(self.get_info())

        # Define índice inical de exclusão.
        initial_delete_index = num_lines - number_of_lines_to_delete

        # Verifica se podem ser excluidas tantas linhas quanto solicitado.
        if initial_delete_index < 1:
            initial_delete_index = 1

        # Apaga linhas.
        self.scrolled_textbox['state'] = 'normal'
        self.scrolled_textbox.delete(f'{initial_delete_index}.0', 'end')
        self.scrolled_textbox['state'] = 'disabled'

        # Exibe novas linhas.
        self.show_info(info_lines)

    def get_info(self):
        """
            :return: (Array) Lista com as linhas exibidas.
        """
        info_lines = [line for line in self.scrolled_textbox.get("1.0", 'end').split('\n')]
        if not info_lines[0]:
            info_lines.pop(0)
        return info_lines

    def clear_info(self):
        """
            Apaga o título e as linhas exibidas.
        """
        self.label_info_title['text'] = ''
        self.scrolled_textbox['state'] = 'normal'
        self.scrolled_textbox.delete("1.0", tk.END)
        self.scrolled_textbox['state'] = 'disabled'


def set_gui_initial_point(gui_initial_point):
    """
        :param gui_initial_point: (Tuple) Tupla com as coordenadas do ponto superior esquerdo da janela do aplicativo.
        Salva as cordenadas recebidas nas configurações.
    """
    config = Config()
    config.edit_config('gui_initial_point', gui_initial_point)
    config.save_configs()


def get_gui_initial_point():
    """
        :return: (Tuple) Tupla com as coordenadas do ponto superior esquerdo da janela.
    """
    config = Config()
    initial_point = [int(value.strip()) for value in config.get_config('gui_initial_point')[1:-1].split(',')]
    return initial_point[0], initial_point[1]


def get_current_gui_initial_point(window_name):
    """
        :param window_name: (String) Nome da janela.
        :return: (Tuple) Tupla com as coordenadas do ponto superior esquerdo da janela.
    """
    system_ma = SystemMa()
    return system_ma.get_window_position(system_ma.get_window(window_name))


def move_gui_to_initial_point(window_name):
    """
        :param window_name: Nome da janela.
        Move a janela para o ponto inicial.
    """
    system_ma = SystemMa()
    gui_initial_point = get_gui_initial_point()
    system_ma.set_window_position_by_initial_point(system_ma.get_window(window_name), gui_initial_point)


def interrupt_process(queue, parent, info_lines=None, info_title='Encerrado!'):
    """
        :param queue: (Queue) Instância da Queue.
        :param parent: (RootWindow) Instância da RootWindow.
        :param info_lines: (Array) Lista com linhas a serem exibidas após cessar o processo.
        :param info_title: (String) Titulo a ser exibido na janela de informações.
        Interrompe o processo secundario sendo ele download e/ou transferência.
    """

    # Verifica lista de funções pendentes.
    pending_functions = PFM.get_pending_functions(queue)

    # Fecha páginas abertas do chrome automatizado se necessário.
    for function in pending_functions:
        if function[0] == 'close_automated_chrome_window':
            system_ma = SystemMa()
            system_ma.close_windows(function[1])
            PFM.remove_pending_function(queue, function)
            break

    # Agenda abertura do menu principal.
    PFM.add_pending_function(queue, ['create_main_gui', 'info_window'])

    # Se não foram informadas novas linhas, exibe apenas que o processo foi interrompido.
    if not info_lines:
        info_lines = ['Processo interrompido!']

    # Agenda apresentação de informações.
    PFM.add_pending_function(queue, ['show_info', info_lines, info_title])

    # Destrói janela e processo atual.
    parent.window.destroy()
    SystemMa.end_process('current')


def create_gui(queue, download, transfer):
    """
        :param queue: (Queue) Instância da Queue.
        :param download: (Boolean) True se o processo de download foi selecionado.
        :param transfer: (Boolean) True se o processo de transferência foi selecionado.
    """

    # Cria janela para apresentação do progresso.
    new_root_window = RootWindow('Execução')
    new_info_window = InfoWindow(new_root_window, queue)
    new_info_window.set_button_action_to_cancel()
    new_root_window.switch_to_window('info_window')

    # Agenda movimentação da janela para ponto inicial.
    command = partial(move_gui_to_initial_point, new_root_window.title)
    new_root_window.window.after(10, command)

    # Agenda inicio dos processos selecionados.
    command = partial(
        run, queue, new_root_window, new_info_window, download, transfer
    )
    new_root_window.window.after(11, command)

    # Abre a janela.
    new_root_window.window.mainloop()


def run(queue, parent, info_window, download, transfer):
    """
        :param queue: (Queue) Instância da Queue.
        :param parent: (RootWindow) Instância da RootWindow.
        :param info_window: (InfoWindow) Instância da InfoWindow.
        :param download: (Boolean) True se o processo de download foi selecionado.
        :param transfer: (Boolean) True se o processo de transferência foi selecionado.
        Inicia os processos selecionados.
    """

    # Instancia classes necessárias.
    core = Core()
    config = Config()
    system_ma = SystemMa()

    # Espera por abertura da janela.
    error = system_ma.wait_until_open(10, parent.title)
    if error:
        # Divide a mensagem de erro por linhas.
        error_lines = [line.strip() for line in error.split("\n") if len(line) > 0]
        info_window.interrupt_process(queue, [error_lines], 'Erro!')

    if download:
        # Inicia processo de download.
        core.download_chapters(queue, parent, info_window)

        # Muda função do botão dinâmico para reconstruir menu principal.
        info_window.set_button_action_to_rebuild_main()
    if transfer:
        # Verifica se há arquivos para a transferência.
        if not system_ma.file_with_pattern_exists(config.chapters_dir, config.manga_name):
            warning = [
                'Não há capítulos para transferir.',
                'Baixe alguns.'
            ]
            info_window.show_info(warning, 'Erro!')
        else:
            # Muda função do botão dinâmico para cancelar o processo.
            info_window.set_button_action_to_cancel()

            # Inicia processo de transferência.
            core.transfer(queue, parent, info_window)

            # Muda função do botão dinâmico para reconstruir menu principal.
            info_window.set_button_action_to_rebuild_main()


def create_main_gui(first_window_name, queue):
    """
        :param first_window_name: (String) nome da primeira janela a ser exibida.
        :param queue: (Queue) Instância da Queue.
        Cria e exibe o menu principal.
    """

    # Atualiza ponto inicial do posicionamento da janela.
    pending_functions = PFM.get_pending_functions(queue)
    if pending_functions:
        for function in pending_functions:
            match function[0]:
                case 'set_gui_initial_point':
                    set_gui_initial_point(function[1])
                    PFM.remove_pending_function(queue, function)
                    break

    # Cria menu principal.
    root_window = RootWindow('Baixar Martial Peak')
    info_window = InfoWindow(root_window, queue)
    HomeWindow(root_window, queue, info_window)
    ConfigWindow(root_window)

    # Exibi a primeira janela.
    root_window.switch_to_window(first_window_name)

    # Agenda movimentação da janela para o ponto inicial.
    command = partial(move_gui_to_initial_point, root_window.title)
    root_window.window.after(10, command)

    # Abre janela
    root_window.window.mainloop()


def run_app():
    """
        Inicia e mantem o aplicativo funcionando.
    """
    app_running = True
    queue = Queue()
    PFM.add_pending_function(queue, ['create_main_gui', 'home_window'])
    while app_running:
        # Carrega funções pendentes.
        pending_functions = PFM.get_pending_functions(queue)
        if pending_functions:
            for function in pending_functions:
                match function[0]:
                    case 'create_main_gui':
                        # Cria e exibe o menu principal.
                        create_main_gui(function[1], queue)
                        PFM.remove_pending_function(queue, function)
                        break
                    case 'create_gui':
                        # Cria e exibe janela de informações para exibição do progresso das funções.
                        subprocess = Process(
                            target=create_gui,
                            args=(queue, function[1], function[2])
                        )
                        subprocess.start()
                        subprocess.join()
                        PFM.remove_pending_function(queue, function)
                        break
        else:
            # Encerra aplicativo.
            app_running = False


if __name__ == '__main__':
    run_app()
