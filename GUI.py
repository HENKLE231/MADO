import tkinter
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext, font
from tkinter.filedialog import askdirectory
from functools import partial
from multiprocessing import Process, Queue, active_children
from ConfigManager import ConfigManager
from SystemManager import SystemManager
from TextManager import TextManager
from DownloadManager import DownloadManager
import time


class GUI:
    def __init__(self):
        # RootWindow.
        # Variáveis.
        self.window = tk.Tk()
        self.title = 'MADO'
        self.window.title(self.title)
        self.browser_handle = 0
        self.queue = Queue()
        self.download_process = None
        self.default_padx = 2
        self.default_pady = 2
        self.selected_config_set = ''
        self.current_config_set = ''
        self.awaiting_function = ''
        self.bread_crumbs = []
        self.app_frames = {}
        self.config_fields = {}
        self.var_chapter_number_by = tk.StringVar()
        self.var_chapter_number_value = tk.StringVar()
        self.var_select = tk.BooleanVar()
        self.configs_for_download = [
            'manga_name',
            'num_chapters',
            'base_link',
            'last_link',
            'final_dir',
            'download_dir',
            'files_dir',
            'chapter_number_by',
            'chapter_number_value',
            'select'
            'select_read_mode_by',
            'select_read_mode_value',
            'visible_text',
            'frames_location_by',
            'frames_location_value',
            'imgs_location_by',
            'imgs_location_value',
            'next_page_button_location_by',
            'next_page_button_location_value'
        ]

        # Instancia classe de configuração.
        self.config_ma = ConfigManager()

        # Instancia classe de manipulação do sistema.
        self.system_ma = SystemManager()

        # Configuração de fonte.
        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family='Verdana', size=9)

        # ==============================================================================================================
        # MenuFrame.
        # Variáveis.
        self.menu_frame = tk.Frame(self.window)

        # Elementos.
        # Linha 0.
        self.label_menu_title = tk.Label(self.menu_frame, text='Menu de perfil', font=10)
        self.label_menu_title.grid(row=0, column=0, padx=50, pady=5, sticky='nswe')

        # Linha 1.
        command = partial(self.load_last_config_set_loaded)
        self.button_load_last_config_set = tk.Button(self.menu_frame, text='Carregar Último', command=command, state='disabled')
        self.button_load_last_config_set.grid(row=1, column=0, padx=5, pady=self.default_pady, sticky='nswe')

        # Linha 2.
        command = partial(self.open_selection_frame, 'continue_to_load', 'Selecione para carregar.')
        self.button_select_to_load = tk.Button(self.menu_frame, text='Selecionar', command=command, state='disabled')
        self.button_select_to_load.grid(row=2, column=0, padx=5, pady=self.default_pady, sticky='nswe')

        # Linha 3.
        command = partial(self.switch_frame, 'creation_frame')
        self.button_create_config_set = tk.Button(self.menu_frame, text='Criar', command=command)
        self.button_create_config_set.grid(row=3, column=0, padx=5, pady=self.default_pady, sticky='nswe')

        # Linha 4.
        command = partial(self.open_selection_frame, 'ask_confirmation_to_delete', 'Selecione para deletar.')
        self.button_delete_config_set = tk.Button(self.menu_frame, text='Deletar', command=command, state='disabled')
        self.button_delete_config_set.grid(row=4, column=0, padx=5, pady=self.default_pady, sticky='nswe')

        # Linha 5.
        command = partial(self.open_selection_frame, 'continue_to_rename', 'Selecione para renomear.')
        self.button_rename_config_set = tk.Button(self.menu_frame, text='Renomear', command=command, state='disabled')
        self.button_rename_config_set.grid(row=5, column=0, padx=5, pady=self.default_pady, sticky='nswe')

        # Linha 6.
        command = partial(self.close_app)
        self.button_close_app = tk.Button(self.menu_frame, text='Sair', command=command)
        self.button_close_app.grid(row=6, column=0, padx=5, pady=self.default_pady, sticky='nswe')

        # Adiciona à lista de janelas existentes.
        self.app_frames['menu_frame'] = {
            'frame': self.menu_frame,
            'widget_to_focus': ''
        }

        # Verifica opções disponíveis do menu.
        self.menu_frame.bind('<Map>', self.manage_menu_buttons_states)

        # ==============================================================================================================
        # SelectionFrame.
        # Variáveis.
        self.selection_frame = tk.Frame(self.window)
        self.var_config_set_name = tk.StringVar()
        self.var_config_set_to_copy = tk.StringVar()

        # Elementos.
        # Linha 0.
        self.label_selection_frame_title = tk.Label(self.selection_frame, text='', font=10)
        self.label_selection_frame_title.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')

        # Linha 1.
        self.frame_listbox = tk.Frame(self.selection_frame)
        self.frame_listbox.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')
        self.frame_listbox.columnconfigure(0, weight=1)
        self.scrollbar = tk.Scrollbar(self.frame_listbox)
        self.scrollbar.grid(row=0, column=1, sticky="nswe")
        self.listbox_config_sets = tk.Listbox(self.frame_listbox, yscrollcommand=self.scrollbar.set)
        self.listbox_config_sets.grid(row=0, column=0, sticky="nswe")

        # Linha 2.
        self.frame_selection_frame_buttons = tk.Frame(self.selection_frame)
        self.frame_selection_frame_buttons.columnconfigure(0, weight=1)
        self.frame_selection_frame_buttons.grid(row=2, column=0, columnspan=3, sticky='nswe')
        self.space = tk.Label(self.frame_selection_frame_buttons, text='')
        self.space.grid(row=0, column=0)
        command = partial(self.go_back)
        self.button_go_back = tk.Button(self.frame_selection_frame_buttons, text='Voltar', command=command)
        self.button_go_back.grid(row=0, column=1, padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.select_config_set)
        self.button_select = tk.Button(self.frame_selection_frame_buttons, text='Selecionar', command=command, state='disabled')
        self.button_select.grid(row=0, column=2, padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Adiciona à lista de janelas existentes.
        self.app_frames['selection_frame'] = {
            'frame': self.selection_frame,
            'widget_to_focus': ''
        }

        # Associa a seleção do listbox a ativação do botão de seleção.
        self.listbox_config_sets.bind('<FocusIn>', self.manage_button_select_state)
        self.listbox_config_sets.bind('<Unmap>', self.manage_button_select_state)

        # ==============================================================================================================
        # CreationFrame.
        # Variáveis.
        self.creation_frame = tk.Frame(self.window)
        self.var_config_set_name = tk.StringVar()
        self.var_config_set_to_copy = tk.StringVar()

        # Elementos.
        # Linha 0.
        self.label_menu_title = tk.Label(self.creation_frame, text='Criação de perfil', font=10)
        self.label_menu_title.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')

        # Linha 1.
        self.label_config_set_name = tk.Label(self.creation_frame, text='Nome:', anchor='e')
        self.label_config_set_name.grid(row=1, column=0, padx=5, pady=5, sticky='nswe')
        self.frame_config_set_name = tk.Frame(self.creation_frame)
        self.frame_config_set_name.columnconfigure(0, weight=1)
        self.frame_config_set_name.grid(row=1, column=1, columnspan=2, padx=5, sticky='we')
        self.warning_label_config_set_name = tk.Label(self.frame_config_set_name, text='', fg='red')
        self.border_config_set_name = tk.Frame(self.frame_config_set_name)
        self.border_config_set_name.columnconfigure(0, weight=1)
        self.border_config_set_name.grid(row=1, column=0, sticky='nswe')
        self.entry_config_set_name = tk.Entry(self.border_config_set_name, textvariable=self.var_config_set_name)
        self.entry_config_set_name.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 2.
        self.label_config_set_to_copy = tk.Label(self.creation_frame, text='Perfil à\nser copiada:', anchor='e')
        self.label_config_set_to_copy.grid(row=2, column=0, padx=5, pady=5, sticky='nswe')
        self.frame_config_set_to_copy = tk.Frame(self.creation_frame)
        self.frame_config_set_to_copy.columnconfigure(0, weight=1)
        self.frame_config_set_to_copy.grid(row=2, column=1, columnspan=2, padx=5, sticky='we')
        self.warning_label_config_set_to_copy = tk.Label(self.frame_config_set_to_copy, text='', fg='red')
        self.border_config_set_to_copy = tk.Frame(self.frame_config_set_to_copy)
        self.border_config_set_to_copy.columnconfigure(0, weight=1)
        self.border_config_set_to_copy.grid(row=1, column=0, sticky='nswe')
        self.entry_config_set_to_copy = tk.Entry(
            self.border_config_set_to_copy, textvariable=self.var_config_set_to_copy, state='disabled', cursor='arrow'
        )
        self.entry_config_set_to_copy.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 3.
        self.frame_creation_frame_buttons = tk.Frame(self.creation_frame)
        self.frame_creation_frame_buttons.columnconfigure(0, weight=1)
        self.frame_creation_frame_buttons.grid(row=3, column=0, columnspan=3, sticky='nswe')
        command = partial(self.go_back)
        self.button_go_back = tk.Button(self.frame_creation_frame_buttons, text='Voltar', command=command)
        self.button_go_back.grid(row=0, column=1, padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.open_selection_frame, 'continue_to_create', 'Selecione para copiar.')
        self.button_select_to_copy = tk.Button(self.frame_creation_frame_buttons, text='Selecionar', command=command)
        self.button_select_to_copy.grid(row=0, column=2, padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.validate_to_create)
        self.button_create = tk.Button(self.frame_creation_frame_buttons, text='Criar', command=command)
        self.button_create.grid(row=0, column=3, padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Adiciona a lista de widgets existentes.
        self.config_fields['config_set_name'] = {
            'display_frame': 'creation_frame',
            'warning_label': self.warning_label_config_set_name,
            'border': self.border_config_set_name,
            'widget': self.entry_config_set_name,
            'var': self.var_config_set_name
        }

        # Adiciona à lista de janelas existentes.
        self.app_frames['creation_frame'] = {
            'frame': self.creation_frame,
            'widget_to_focus': self.entry_config_set_name
        }

        # ==============================================================================================================
        # RenameFrame.
        # Variáveis.
        self.rename_frame = tk.Frame(self.window)
        self.var_current_config_set_name = tk.StringVar()
        self.var_new_config_set_name = tk.StringVar()

        # Elementos.
        # Linha 0.
        self.label_menu_title = tk.Label(self.rename_frame, text='Renomear perfil.', font=10)
        self.label_menu_title.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')

        # Linha 1.
        self.label_current_config_set_name = tk.Label(self.rename_frame, text='Nome Atual:', anchor='e')
        self.label_current_config_set_name.grid(row=1, column=0, padx=5, pady=5, sticky='nswe')
        self.frame_current_config_set_name = tk.Frame(self.rename_frame)
        self.frame_current_config_set_name.columnconfigure(0, weight=1)
        self.frame_current_config_set_name.grid(row=1, column=1, columnspan=2, padx=5, sticky='we')
        self.warning_label_current_config_set_name = tk.Label(self.frame_current_config_set_name, text='', fg='red')
        self.border_current_config_set_name = tk.Frame(self.frame_current_config_set_name)
        self.border_current_config_set_name.columnconfigure(0, weight=1)
        self.border_current_config_set_name.grid(row=1, column=0, sticky='nswe')
        self.entry_current_config_set_name = tk.Entry(
            self.border_current_config_set_name, textvariable=self.var_current_config_set_name, state='disabled', cursor='arrow'
        )
        self.entry_current_config_set_name.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 2.
        self.label_new_config_set_name = tk.Label(self.rename_frame, text='Novo nome:', anchor='e')
        self.label_new_config_set_name.grid(row=2, column=0, padx=5, pady=5, sticky='nswe')
        self.frame_new_config_set_name = tk.Frame(self.rename_frame)
        self.frame_new_config_set_name.columnconfigure(0, weight=1)
        self.frame_new_config_set_name.grid(row=2, column=1, columnspan=2, padx=5, sticky='we')
        self.warning_label_new_config_set_name = tk.Label(self.frame_new_config_set_name, text='', fg='red')
        self.border_new_config_set_name = tk.Frame(self.frame_new_config_set_name)
        self.border_new_config_set_name.columnconfigure(0, weight=1)
        self.border_new_config_set_name.grid(row=1, column=0, sticky='nswe')
        self.entry_new_config_set_name = tk.Entry(self.border_new_config_set_name, textvariable=self.var_new_config_set_name)
        self.entry_new_config_set_name.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 3.
        self.frame_rename_frame_buttons = tk.Frame(self.rename_frame)
        self.frame_rename_frame_buttons.columnconfigure(0, weight=1)
        self.frame_rename_frame_buttons.grid(row=3, column=0, columnspan=3, sticky='nswe')
        command = partial(self.go_back)
        self.button_go_back = tk.Button(self.frame_rename_frame_buttons, text='Voltar', command=command)
        self.button_go_back.grid(row=0, column=1, padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.validate_to_rename)
        self.button_create = tk.Button(self.frame_rename_frame_buttons, text='Renomear', command=command)
        self.button_create.grid(row=0, column=2, padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Adiciona a lista de widgets existentes.
        self.config_fields['new_config_set_name'] = {
            'display_frame': 'rename_frame',
            'warning_label': self.warning_label_new_config_set_name,
            'border': self.border_new_config_set_name,
            'widget': self.entry_new_config_set_name,
            'var': self.var_new_config_set_name
        }

        # Adiciona à lista de janelas existentes.
        self.app_frames['rename_frame'] = {
            'frame': self.rename_frame,
            'widget_to_focus': self.entry_new_config_set_name
        }

        # ==============================================================================================================
        # HomeFrame.
        # Variáveis.
        self.home_frame = tk.Frame(self.window)
        self.var_num_chapters = tk.StringVar()
        self.var_final_chapter = tk.StringVar()
        self.var_base_link = tk.StringVar()
        self.var_last_link = tk.StringVar()
        self.chapters_files = []

        # Elementos.
        # Linha 0.
        self.label_manga_name = tk.Label(self.home_frame, text='Home', font=10)
        self.label_manga_name.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')

        # Linha 1.
        self.label_loaded_config_set_name = tk.Label(self.home_frame, text='', anchor='center')
        self.label_loaded_config_set_name.grid(row=1, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')
        
        # Linha 2.
        self.label_num_chapters = tk.Label(self.home_frame, text='Quantidade de capítulos:', anchor='e')
        self.label_num_chapters.grid(row=2, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_num_chapters = tk.Frame(self.home_frame)
        self.frame_num_chapters.columnconfigure(0, weight=1)
        self.frame_num_chapters.grid(row=2, column=1, columnspan=2, sticky='we')
        self.warning_label_num_chapters = tk.Label(self.frame_num_chapters, text='', fg='red')
        self.border_num_chapters = tk.Frame(self.frame_num_chapters)
        self.border_num_chapters.columnconfigure(0, weight=1)
        self.border_num_chapters.grid(row=1, column=0, sticky='nswe')
        self.entry_num_chapters = tk.Entry(self.border_num_chapters, textvariable=self.var_num_chapters)
        self.entry_num_chapters.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        
        # Linha 3.
        self.label_base_link = tk.Label(self.home_frame, text='Link Inicial:', anchor='e')
        self.label_base_link.grid(row=3, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_base_link = tk.Frame(self.home_frame)
        self.frame_base_link.columnconfigure(0, weight=1)
        self.frame_base_link.grid(row=3, column=1, columnspan=2, sticky='nswe')
        self.warning_label_base_link = tk.Label(self.frame_base_link, text='', fg='red')
        self.border_base_link = tk.Frame(self.frame_base_link)
        self.border_base_link.columnconfigure(0, weight=1)
        self.border_base_link.grid(row=1, column=0, sticky='nswe')
        self.entry_base_link = tk.Entry(self.border_base_link, textvariable=self.var_base_link, width=50)
        self.entry_base_link.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 4.
        self.label_last_link = tk.Label(self.home_frame, text='Último Link Aberto:', anchor='e')
        self.label_last_link.grid(row=4, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_last_link = tk.Frame(self.home_frame)
        self.frame_last_link.columnconfigure(0, weight=1)
        self.frame_last_link.grid(row=4, column=1, columnspan=2, sticky='we')
        self.warning_label_last_link = tk.Label(self.frame_last_link, text='', fg='red')
        self.border_last_link = tk.Frame(self.frame_last_link)
        self.border_last_link.columnconfigure(0, weight=1)
        self.border_last_link.grid(row=1, column=0, sticky='nswe')
        self.entry_last_link = tk.Entry(self.border_last_link, textvariable=self.var_last_link)
        self.entry_last_link.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 5.
        self.frame_home_frame_buttons = tk.Frame(self.home_frame)
        self.frame_home_frame_buttons.grid(row=5, column=0, columnspan=3)
        command = partial(self.copy_last_link_to_base_link)
        self.button_last_link = tk.Button(self.frame_home_frame_buttons, text='Colar Último Link no Inicial', command=command)
        self.button_last_link.grid(row=0, column=0, columnspan=4, padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.save_and_go_back)
        self.button_config = tk.Button(self.frame_home_frame_buttons, text='Voltar', command=command)
        self.button_config.grid(row=1, column=0, padx=3, pady=3, sticky='nswe')
        command = partial(self.validate_to_delete_downloaded_chapters)
        self.button_config = tk.Button(
            self.frame_home_frame_buttons, text='Excluir Downloads', command=command
        )
        self.button_config.grid(row=1, column=1, padx=3, pady=3, sticky='nswe')
        command = partial(self.switch_frame, 'config_frame')
        self.button_config = tk.Button(self.frame_home_frame_buttons, text='Configurações', command=command)
        self.button_config.grid(row=1, column=2, padx=3, pady=3, sticky='nswe')
        command = partial(self.validate_to_download)
        self.button_run = tk.Button(self.frame_home_frame_buttons, text='Baixar', command=command)
        self.button_run.grid(row=1, column=3, padx=3, pady=3, sticky='nswe')

        # Adiciona a lista de widgets existentes.
        self.config_fields['num_chapters'] = {
            'display_frame': 'home_frame',
            'warning_label': self.warning_label_num_chapters,
            'border': self.border_num_chapters,
            'widget': self.entry_num_chapters,
            'var': self.var_num_chapters
        }
        self.config_fields['base_link'] = {
            'display_frame': 'home_frame',
            'warning_label': self.warning_label_base_link,
            'border': self.border_base_link,
            'widget': self.entry_base_link,
            'var': self.var_base_link
        }
        self.config_fields['last_link'] = {
            'display_frame': 'home_frame',
            'warning_label': self.warning_label_last_link,
            'border': self.border_last_link,
            'widget': self.entry_last_link,
            'var': self.var_last_link
        }

        # Adiciona à lista de janelas existentes.
        self.app_frames['home_frame'] = {
            'frame': self.home_frame,
            'widget_to_focus': ''
        }

        # ==============================================================================================================
        # ConfigFrame.
        # Variáveis.
        self.config_frame = tk.Frame(self.window)
        self.var_manga_name = tk.StringVar()
        self.var_final_dir = tk.StringVar()
        self.var_download_dir = tk.StringVar()
        self.var_files_dir = tk.StringVar()
        self.var_chapter_number_by = tk.StringVar()
        self.var_chapter_number_value = tk.StringVar()
        self.var_select = tk.BooleanVar()
        self.var_select_read_mode_by = tk.StringVar()
        self.var_select_read_mode_value = tk.StringVar()
        self.var_visible_text = tk.StringVar()
        self.var_frames_location_by = tk.StringVar()
        self.var_frames_location_value = tk.StringVar()
        self.var_imgs_location_by = tk.StringVar()
        self.var_imgs_location_value = tk.StringVar()
        self.var_next_page_button_location_by = tk.StringVar()
        self.var_next_page_button_location_value = tk.StringVar()

        # Elementos.
        # Linha 0.
        self.label_config = tk.Label(self.config_frame, text='Configurações', font=10)
        self.label_config.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')

        # Linha 1.
        self.label_manga_name = tk.Label(self.config_frame, text='Nome do Mangá:', anchor='e')
        self.label_manga_name.grid(row=1, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_manga_name = tk.Frame(self.config_frame)
        self.frame_manga_name.columnconfigure(0, weight=1)
        self.frame_manga_name.grid(row=1, column=1, sticky='we')
        self.warning_label_manga_name = tk.Label(self.frame_manga_name, text='', fg='red')
        self.border_manga_name = tk.Frame(self.frame_manga_name)
        self.border_manga_name.columnconfigure(0, weight=1)
        self.border_manga_name.grid(row=1, column=0, sticky='nswe')
        self.entry_manga_name = tk.Entry(self.border_manga_name, textvariable=self.var_manga_name)
        self.entry_manga_name.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 4.
        self.label_final_dir = tk.Label(self.config_frame, text='Pasta Final:', anchor='e')
        self.label_final_dir.grid(row=4, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_final_dir = tk.Frame(self.config_frame)
        self.frame_final_dir.columnconfigure(0, weight=1)
        self.frame_final_dir.grid(row=4, column=1, sticky='we')
        self.warning_label_final_dir = tk.Label(self.frame_final_dir, text='', fg='red')
        self.border_final_dir = tk.Frame(self.frame_final_dir)
        self.border_final_dir.columnconfigure(0, weight=1)
        self.border_final_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_final_dir = tk.Entry(self.border_final_dir, textvariable=self.var_final_dir)
        self.entry_final_dir.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.select_dir, 'Selecione pasta de destino dos mangás.', self.var_final_dir)
        self.button_final_dir = tk.Button(self.config_frame, text='Procurar', command=command)
        self.button_final_dir.grid(row=4, column=2, padx=self.default_padx, sticky='swe')

        # Linha 5.
        self.label_download_dir = tk.Label(self.config_frame, text='Pasta de Download:', anchor='e')
        self.label_download_dir.grid(row=5, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_download_dir = tk.Frame(self.config_frame)
        self.frame_download_dir.columnconfigure(0, weight=1)
        self.frame_download_dir.grid(row=5, column=1, sticky='we')
        self.warning_label_download_dir = tk.Label(self.frame_download_dir, text='', fg='red')
        self.border_download_dir = tk.Frame(self.frame_download_dir)
        self.border_download_dir.columnconfigure(0, weight=1)
        self.border_download_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_download_dir = tk.Entry(self.border_download_dir, textvariable=self.var_download_dir)
        self.entry_download_dir.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.select_dir, 'Selecione pasta de download padrão do navegador.', self.var_download_dir)
        self.button_download_dir = tk.Button(self.config_frame, text='Procurar', command=command)
        self.button_download_dir.grid(row=5, column=2, padx=self.default_padx, sticky='swe')

        # Linha 6.
        self.label_files_dir = tk.Label(self.config_frame, text='Pasta de Arquivos:', anchor='e')
        self.label_files_dir.grid(row=6, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_files_dir = tk.Frame(self.config_frame)
        self.frame_files_dir.columnconfigure(0, weight=1)
        self.frame_files_dir.grid(row=6, column=1, sticky='we')
        self.warning_label_files_dir = tk.Label(self.frame_files_dir, text='', fg='red')
        self.border_files_dir = tk.Frame(self.frame_files_dir)
        self.border_files_dir.columnconfigure(0, weight=1)
        self.border_files_dir.grid(row=1, column=0, sticky='nswe')
        self.entry_files_dir = tk.Entry(self.border_files_dir, textvariable=self.var_files_dir)
        self.entry_files_dir.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.select_dir, 'Selecione pasta para manipulação das imagens.', self.var_files_dir)
        self.button_files_dir = tk.Button(self.config_frame, text='Procurar', command=command)
        self.button_files_dir.grid(row=6, column=2, padx=self.default_padx, sticky='swe')

        # Linha 7.
        self.label_chapter_number_by = tk.Label(self.config_frame, text='Identificador de capítulo:', anchor='e')
        self.label_chapter_number_by.grid(row=7, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_chapter_number_value = tk.Frame(self.config_frame)
        self.frame_chapter_number_value.columnconfigure(0, weight=1)
        self.frame_chapter_number_value.grid(row=7, column=1, sticky='we')
        self.warning_label_chapter_number_value = tk.Label(self.frame_chapter_number_value, text='', fg='red')
        self.border_chapter_number_value = tk.Frame(self.frame_chapter_number_value)
        self.border_chapter_number_value.columnconfigure(0, weight=1)
        self.border_chapter_number_value.grid(row=1, column=0, sticky='nswe')
        self.entry_chapter_number_value = tk.Entry(self.border_chapter_number_value, textvariable=self.var_chapter_number_value)
        self.entry_chapter_number_value.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        self.frame_chapter_number_by = tk.Frame(self.config_frame)
        self.frame_chapter_number_by.columnconfigure(0, weight=1)
        self.frame_chapter_number_by.grid(row=7, column=2, sticky='we')
        self.warning_label_chapter_number_by = tk.Label(self.frame_chapter_number_by, text='', fg='red')
        self.border_chapter_number_by = tk.Frame(self.frame_chapter_number_by)
        self.border_chapter_number_by.columnconfigure(0, weight=1)
        self.border_chapter_number_by.grid(row=1, column=0, sticky='nswe')
        self.option_menu_chapter_number_by = tk.OptionMenu(
            self.border_chapter_number_by,  self.var_chapter_number_by,
            "Selecione", "id", "name", "xpath", "link text", "partial link text", "tag name", "class name", "css selector",
        )
        self.option_menu_chapter_number_by.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 8.
        self.label_select = tk.Label(self.config_frame, text='Identificador é um select:', anchor='e')
        self.label_select.grid(row=8, column=0, padx=5, pady=1, sticky='nswe')
        self.check_button_select = tk.Checkbutton(self.config_frame, variable=self.var_select, onvalue=0)
        self.check_button_select.grid(row=8, column=1, padx=5, pady=1, sticky='nswe')

        # Linha 9.
        self.label_select_read_mode_by = tk.Label(self.config_frame, text='Seletor:', anchor='e')
        self.label_select_read_mode_by.grid(row=9, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_select_read_mode_value = tk.Frame(self.config_frame)
        self.frame_select_read_mode_value.columnconfigure(0, weight=1)
        self.frame_select_read_mode_value.grid(row=9, column=1, sticky='we')
        self.warning_label_select_read_mode_value = tk.Label(self.frame_select_read_mode_value, text='', fg='red')
        self.border_select_read_mode_value = tk.Frame(self.frame_select_read_mode_value)
        self.border_select_read_mode_value.columnconfigure(0, weight=1)
        self.border_select_read_mode_value.grid(row=1, column=0, sticky='nswe')
        self.entry_select_read_mode_value = tk.Entry(self.border_select_read_mode_value, textvariable=self.var_select_read_mode_value)
        self.entry_select_read_mode_value.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        self.frame_select_read_mode_by = tk.Frame(self.config_frame)
        self.frame_select_read_mode_by.columnconfigure(0, weight=1)
        self.frame_select_read_mode_by.grid(row=9, column=2, sticky='we')
        self.warning_label_select_read_mode_by = tk.Label(self.frame_select_read_mode_by, text='', fg='red')
        self.border_select_read_mode_by = tk.Frame(self.frame_select_read_mode_by)
        self.border_select_read_mode_by.columnconfigure(0, weight=1)
        self.border_select_read_mode_by.grid(row=1, column=0, sticky='nswe')
        self.option_menu_select_read_mode_by = tk.OptionMenu(
            self.border_select_read_mode_by, self.var_select_read_mode_by,
            "Selecione", "id", "name", "xpath", "link text", "partial link text", "tag name", "class name", "css selector",
        )
        self.option_menu_select_read_mode_by.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 10.
        self.label_visible_text = tk.Label(self.config_frame, text='Texto da opção:', anchor='e')
        self.label_visible_text.grid(row=10, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_visible_text = tk.Frame(self.config_frame)
        self.frame_visible_text.columnconfigure(0, weight=1)
        self.frame_visible_text.grid(row=10, column=1, sticky='we')
        self.warning_label_visible_text = tk.Label(self.frame_visible_text, text='', fg='red')
        self.border_visible_text = tk.Frame(self.frame_visible_text)
        self.border_visible_text.columnconfigure(0, weight=1)
        self.border_visible_text.grid(row=1, column=0, sticky='nswe')
        self.entry_visible_text = tk.Entry(self.border_visible_text, textvariable=self.var_visible_text)
        self.entry_visible_text.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 11.
        self.label_frames_location_by = tk.Label(self.config_frame, text='Quadros:', anchor='e')
        self.label_frames_location_by.grid(row=11, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_frames_location_value = tk.Frame(self.config_frame)
        self.frame_frames_location_value.columnconfigure(0, weight=1)
        self.frame_frames_location_value.grid(row=11, column=1, sticky='we')
        self.warning_label_frames_location_value = tk.Label(self.frame_frames_location_value, text='', fg='red')
        self.border_frames_location_value = tk.Frame(self.frame_frames_location_value)
        self.border_frames_location_value.columnconfigure(0, weight=1)
        self.border_frames_location_value.grid(row=1, column=0, sticky='nswe')
        self.entry_frames_location_value = tk.Entry(self.border_frames_location_value, textvariable=self.var_frames_location_value)
        self.entry_frames_location_value.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        self.frame_frames_location_by = tk.Frame(self.config_frame)
        self.frame_frames_location_by.columnconfigure(0, weight=1)
        self.frame_frames_location_by.grid(row=11, column=2, sticky='we')
        self.warning_label_frames_location_by = tk.Label(self.frame_frames_location_by, text='', fg='red')
        self.border_frames_location_by = tk.Frame(self.frame_frames_location_by)
        self.border_frames_location_by.columnconfigure(0, weight=1)
        self.border_frames_location_by.grid(row=1, column=0, sticky='nswe')
        self.option_menu_frames_location_by = tk.OptionMenu(
            self.border_frames_location_by,  self.var_frames_location_by,
            "Selecione", "id", "name", "xpath", "link text", "partial link text", "tag name", "class name", "css selector",
        )
        self.option_menu_frames_location_by.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 12.
        self.label_imgs_location_by = tk.Label(self.config_frame, text='Imagens:', anchor='e')
        self.label_imgs_location_by.grid(row=12, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_imgs_location_value = tk.Frame(self.config_frame)
        self.frame_imgs_location_value.columnconfigure(0, weight=1)
        self.frame_imgs_location_value.grid(row=12, column=1, sticky='we')
        self.warning_label_imgs_location_value = tk.Label(self.frame_imgs_location_value, text='', fg='red')
        self.border_imgs_location_value = tk.Frame(self.frame_imgs_location_value)
        self.border_imgs_location_value.columnconfigure(0, weight=1)
        self.border_imgs_location_value.grid(row=1, column=0, sticky='nswe')
        self.entry_imgs_location_value = tk.Entry(self.border_imgs_location_value, textvariable=self.var_imgs_location_value)
        self.entry_imgs_location_value.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        self.frame_imgs_location_by = tk.Frame(self.config_frame)
        self.frame_imgs_location_by.columnconfigure(0, weight=1)
        self.frame_imgs_location_by.grid(row=12, column=2, sticky='we')
        self.warning_label_imgs_location_by = tk.Label(self.frame_imgs_location_by, text='', fg='red')
        self.border_imgs_location_by = tk.Frame(self.frame_imgs_location_by)
        self.border_imgs_location_by.columnconfigure(0, weight=1)
        self.border_imgs_location_by.grid(row=1, column=0, sticky='nswe')
        self.option_menu_imgs_location_by = tk.OptionMenu(
            self.border_imgs_location_by,  self.var_imgs_location_by,
            "Selecione", "id", "name", "xpath", "link text", "partial link text", "tag name", "class name", "css selector",
        )
        self.option_menu_imgs_location_by.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 13.
        self.label_next_page_button_location_by = tk.Label(self.config_frame, text='Botão de Avançar:', anchor='e')
        self.label_next_page_button_location_by.grid(row=13, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_next_page_button_location_value = tk.Frame(self.config_frame)
        self.frame_next_page_button_location_value.columnconfigure(0, weight=1)
        self.frame_next_page_button_location_value.grid(row=13, column=1, sticky='we')
        self.warning_label_next_page_button_location_value = tk.Label(
            self.frame_next_page_button_location_value, text='', fg='red'
        )
        self.border_next_page_button_location_value = tk.Frame(self.frame_next_page_button_location_value)
        self.border_next_page_button_location_value.columnconfigure(0, weight=1)
        self.border_next_page_button_location_value.grid(row=1, column=0, sticky='nswe')
        self.entry_next_page_button_location_value = tk.Entry(
            self.border_next_page_button_location_value, textvariable=self.var_next_page_button_location_value
        )
        self.entry_next_page_button_location_value.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        self.frame_next_page_button_location_by = tk.Frame(self.config_frame)
        self.frame_next_page_button_location_by.columnconfigure(0, weight=1)
        self.frame_next_page_button_location_by.grid(row=11, column=2, sticky='we')
        self.warning_label_next_page_button_location_by = tk.Label(self.frame_next_page_button_location_by, text='', fg='red')
        self.border_next_page_button_location_by = tk.Frame(self.frame_next_page_button_location_by)
        self.border_next_page_button_location_by.columnconfigure(0, weight=1)
        self.border_next_page_button_location_by.grid(row=1, column=0, sticky='nswe')
        self.option_menu_next_page_button_location_by = tk.OptionMenu(
            self.border_next_page_button_location_by,  self.var_next_page_button_location_by,
            "Selecione", "id", "name", "xpath", "link text", "partial link text", "tag name", "class name", "css selector"
        )
        self.option_menu_next_page_button_location_by.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 14.
        self.frame_info_frame_buttons = tk.Frame(self.config_frame)
        self.frame_info_frame_buttons.grid(row=14, column=1, padx=2)
        self.frame_info_frame_buttons.columnconfigure(0, weight=1)
        self.info_frame_space = tk.Label(self.frame_info_frame_buttons, text='')
        self.info_frame_space.grid(row=0, column=0)
        command = partial(self.ask_confirmation_to_reset)
        self.button_reset = tk.Button(self.frame_info_frame_buttons, text='Configuração Padrão', command=command)
        self.button_reset.grid(row=0, column=1, ipadx=20, pady=5, sticky='nswe')
        command = partial(self.save_and_go_back)
        self.button_back = tk.Button(self.config_frame, text='Voltar', command=command)
        self.button_back.grid(row=14, column=2, ipadx=20, padx=self.default_padx, pady=5, sticky='nswe')

        # Adiciona a lista de widgets existentes.
        self.config_fields['manga_name'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_manga_name,
            'border': self.border_manga_name,
            'widget': self.entry_manga_name,
            'var': self.var_manga_name
        }
        self.config_fields['final_dir'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_final_dir,
            'border': self.border_final_dir,
            'widget': self.entry_final_dir,
            'var': self.var_final_dir
        }
        self.config_fields['download_dir'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_download_dir,
            'border': self.border_download_dir,
            'widget': self.entry_download_dir,
            'var': self.var_download_dir
        }
        self.config_fields['files_dir'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_files_dir,
            'border': self.border_files_dir,
            'widget': self.entry_files_dir,
            'var': self.var_files_dir
        }
        self.config_fields['select'] = {
            'display_frame': 'config_frame',
            'warning_label': '',
            'border': '',
            'widget': self.check_button_select,
            'var': self.var_select
        }
        self.config_fields['chapter_number_by'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_chapter_number_by,
            'border': self.border_chapter_number_by,
            'widget': self.option_menu_chapter_number_by,
            'var': self.var_chapter_number_by
        }
        self.config_fields['chapter_number_value'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_chapter_number_value,
            'border': self.border_chapter_number_value,
            'widget': self.entry_chapter_number_value,
            'var': self.var_chapter_number_value
        }
        self.config_fields['select_read_mode_by'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_select_read_mode_by,
            'border': self.border_select_read_mode_by,
            'widget': self.option_menu_select_read_mode_by,
            'var': self.var_select_read_mode_by
        }
        self.config_fields['select_read_mode_value'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_select_read_mode_value,
            'border': self.border_select_read_mode_value,
            'widget': self.entry_select_read_mode_value,
            'var': self.var_select_read_mode_value
        }
        self.config_fields['visible_text'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_visible_text,
            'border': self.border_visible_text,
            'widget': self.entry_visible_text,
            'var': self.var_visible_text
        }
        self.config_fields['frames_location_by'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_frames_location_by,
            'border': self.border_frames_location_by,
            'widget': self.option_menu_frames_location_by,
            'var': self.var_frames_location_by
        }
        self.config_fields['frames_location_value'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_frames_location_value,
            'border': self.border_frames_location_value,
            'widget': self.entry_frames_location_value,
            'var': self.var_frames_location_value
        }
        self.config_fields['imgs_location_by'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_imgs_location_by,
            'border': self.border_imgs_location_by,
            'widget': self.option_menu_imgs_location_by,
            'var': self.var_imgs_location_by
        }
        self.config_fields['imgs_location_value'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_imgs_location_value,
            'border': self.border_imgs_location_value,
            'widget': self.entry_imgs_location_value,
            'var': self.var_imgs_location_value
        }
        self.config_fields['next_page_button_location_by'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_next_page_button_location_by,
            'border': self.border_next_page_button_location_by,
            'widget': self.option_menu_next_page_button_location_by,
            'var': self.var_next_page_button_location_by
        }
        self.config_fields['next_page_button_location_value'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_next_page_button_location_value,
            'border': self.border_next_page_button_location_value,
            'widget': self.entry_next_page_button_location_value,
            'var': self.var_next_page_button_location_value
        }

        # Adiciona às janelas existentes.
        self.app_frames['config_frame'] = {
            'frame': self.config_frame,
            'widget_to_focus': ''
        }

        # ==============================================================================================================
        # ConfirmationFrame.
        # Variáveis.
        self.confirmation_frame = tk.Frame(self.window)
        self.confirmation_frame_max_char_per_line = 50

        # Elementos.
        # Linha 0.
        self.label_confirmation_title = tk.Label(self.confirmation_frame, font=10)
        self.label_confirmation_title.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')

        # Linha 1.
        self.label_confirmation_description = tk.Label(self.confirmation_frame, anchor='w')
        self.label_confirmation_description.grid(row=1, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

        # Linha 2.
        self.frame_confirmation_frame_buttons = tk.Frame(self.confirmation_frame)
        self.frame_confirmation_frame_buttons.grid(row=2, column=0, columnspan=3)
        self.frame_confirmation_frame_buttons.columnconfigure(0, weight=1)
        self.info_frame_space = tk.Label(self.frame_confirmation_frame_buttons, text='')
        self.info_frame_space.grid(row=0, column=0)
        command = partial(self.cancel)
        self.cancelation_button = tk.Button(self.frame_confirmation_frame_buttons, text='Cancelar', command=command)
        self.cancelation_button.grid(row=0, column=1, padx=self.default_padx, pady=self.default_pady, sticky='nswe')
        command = partial(self.execute_awaiting_function)
        self.confirmation_button = tk.Button(self.frame_confirmation_frame_buttons, text='Confirmar', command=command)
        self.confirmation_button.grid(row=0, column=2, padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Adiciona à lista de janelas existentes.
        self.app_frames['confirmation_frame'] = {
            'frame': self.confirmation_frame,
            'widget_to_focus': ''
        }

        # ==============================================================================================================
        # InfoFrame.
        # Variáveis.
        self.info_frame = tk.Frame(self.window)
        self.num_info_lines = 7
        self.info_frame_max_char_per_line = 50
        self.dynamic_button_action = 'go_home'
        self.dynamic_button_text = 'Voltar'

        # Elementos.
        # Linha 0.
        self.label_info_title = tk.Label(self.info_frame, font=10)
        self.label_info_title.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')

        # Linha 1.
        self.scrolled_textbox = scrolledtext.ScrolledText(
            self.info_frame, width=self.info_frame_max_char_per_line, height=self.num_info_lines, cursor='arrow'
        )
        self.scrolled_textbox.grid(row=1, column=0, columnspan=3, padx=5, pady=self.default_pady, sticky='nswe')

        # Linha 2.
        command = partial(self.execute_dynamic_button_action)
        self.dynamic_button = tk.Button(self.info_frame, text=self.dynamic_button_text, command=command)
        self.dynamic_button.grid(row=2, column=2, padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Adiciona à lista de janelas existentes.
        self.app_frames['info_frame'] = {
            'frame': self.info_frame,
            'widget_to_focus': ''
        }

        # ==============================================================================================================
        # Exibe tela inicial
        self.switch_frame('menu_frame')

    # ==================================================================================================================
    # Funções gerais.
    def switch_frame(self, next_frame, current_frame=None):
        """
            Exibe o frame requerido.
        """
        # Verifica se há exibição de frame.
        if self.bread_crumbs:
            # Se não estiver voltando, pega o último frame do histórico como atual.
            if not current_frame:
                current_frame = self.bread_crumbs[-1]

            # Verifica se o frame requerido está sendo exibido.
            if current_frame == next_frame:
                return

        # Configura frames especificos.
        match next_frame:
            case 'home_frame':
                # Carrega configurações do home_frame e config_frame.
                self.update_all_fields()
                # Exibe nome do perfil carregado.
                self.display_loaded_config_set_name()
            case 'selection_frame':
                # Exibe conjuntos de configurações.
                self.display_config_sets()
            case 'creation_frame':
                self.manage_copy_button_state()

        # Esconde frame atualmente exibido.
        if current_frame:
            self.app_frames[current_frame]['frame'].grid_forget()

        # Define frames que só podem voltar para o menu.
        frames_that_can_only_go_back_to_the_menu = [
            'menu_frame',
            'home_frame',
            'creation_frame',
        ]

        # Configura retorno para o menu.
        if next_frame in frames_that_can_only_go_back_to_the_menu:
            self.bread_crumbs = ['menu_frame']

        # Se não for o menu_frame adiciona.
        if next_frame not in self.bread_crumbs:
            self.bread_crumbs.append(next_frame)

        # Exibe o frame requerido.
        self.app_frames[next_frame]['frame'].grid()

        # Seleciona widget
        widget_to_focus = self.app_frames[next_frame]['widget_to_focus']

        if widget_to_focus:
            # Foca no campo.
            widget_to_focus.focus_set()

            # Verifica õnde é o final do campo.
            info_length = len(widget_to_focus.get())

            # Move o foco para o final do campo.
            widget_to_focus.icursor(info_length)

    def go_back(self):
        """
            Tira do histórico o frame atual e anteriores até o primeiro que possa ser exibido
        """
        # Retira atual frame do histórico.
        current_frame = self.bread_crumbs.pop()

        # Define frames para não se voltar.
        frames_to_not_return = [
            'confirmation_frame',
            'rename_frame',
            'info_frame'
        ]

        # Procura o proximo frame possivel de voltar e retirar se não pode.
        next_frame = ''
        for frame in self.bread_crumbs[::-1]:
            if frame in frames_to_not_return:
                self.bread_crumbs.pop()
            elif frame == 'selection_frame' and not self.config_ma.get_config_set_names():
                self.bread_crumbs.pop()
            else:
                # Seleciona o proximo frame.
                next_frame = self.bread_crumbs.pop()
                break

        # Altera frame em exibição.
        self.switch_frame(next_frame, current_frame)

    def save_configs_for_download(self):
        """
            Salva variáveis de configuração.
        """
        # Carrega configurações.
        self.config_ma.load_config_set(self.current_config_set)

        # Varre os campos.
        for config_name, widgets in self.config_fields.items():
            if config_name in self.configs_for_download:
                # Pega o valor.
                value = widgets['var'].get().strip()

                # Salva na instância.
                self.config_ma.edit_config(config_name, value)

        # Salva.
        self.config_ma.save_config_set()

    def save_last_link(self, link):
        """
            :param link: (String) Link do último capítulo acessado.
            Salva o link do último capítulo acessado.
        """
        # Carrega configurações.
        self.config_ma.load_config_set(self.current_config_set)

        # Edita o config.
        self.config_ma.edit_config('last_link', link)

        # Salva.
        self.config_ma.save_config_set()

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
        target_frame = ''
        target_config_name = ''

        # Varre avisos.
        for config_name, warning in configs_and_warnings.items():
            # Seleciona campo.
            field = self.config_fields[config_name]

            # Salva o primeiro campo a ser destacado.
            if not target_frame:
                target_frame = field['display_frame']

            # Salva a primeira configuração a receber foco.
            if not target_config_name:
                target_config_name = config_name

            # Destaca campo e exibe aviso.
            field['warning_label']['text'] = warning
            field['border']['bg'] = 'red'
            field['warning_label'].grid(row=0, column=0)

        # Exibe o frame alvo.
        self.switch_frame(target_frame)

        # Seleciona campo.
        field = self.config_fields[target_config_name]

        # Foca no final do primeiro campo.
        field['widget'].focus_set()
        info_length = len(field['var'].get())
        field['widget'].icursor(info_length)

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
        # Carrega configurações.
        self.config_ma.load_config_set(self.current_config_set)

        # Preenche campos.
        for config_name, field in self.config_fields.items():
            if config_name in self.configs_for_download:
                field['var'].set(self.config_ma.config_list[config_name])

    def execute_awaiting_function(self):
        """
            Executa função esperando por confirmação.
        """
        match self.awaiting_function:
            case 'delete_chapters':
                self.delete_chapters()
            case 'continue_to_create':
                self.continue_to_create()
            case 'continue_to_load':
                self.continue_to_load()
            case 'ask_confirmation_to_delete':
                self.ask_confirmation_to_delete()
            case 'continue_to_delete':
                self.continue_to_delete()
            case 'continue_to_rename':
                self.continue_to_rename()
            case 'reset_config_set':
                self.reset_config_set()

    def open_selection_frame(self, awaiting_function, title):
        """
            Abre o frame de seleção e exibe titulo.
        """
        self.awaiting_function = awaiting_function
        self.display_selection_title(title)
        self.switch_frame('selection_frame')

    # ==================================================================================================================
    # Funções do MenuFrame.
    def manage_menu_buttons_states(self, event):
        """
            :param event: (Event) Evento tkinter.
            Manipula o estado dos botões do menu.
        """
        # Define estaod padrão
        new_state = 'disabled'

        # Verifica se há algo salvo.
        if self.config_ma.get_config_set_names():
            # Verifica se existe a configuração do último carregado.
            if self.config_ma.get_last_config_set_loaded():
                self.button_load_last_config_set['state'] = 'normal'
            else:
                self.button_load_last_config_set['state'] = 'disabled'

            # Define estado dos outros botões.
            new_state = 'normal'
        else:
            self.button_load_last_config_set['state'] = 'disabled'

        self.button_select_to_load['state'] = new_state
        self.button_delete_config_set['state'] = new_state
        self.button_rename_config_set['state'] = new_state

    def close_app(self):
        """
            Fecha o app.
        """
        self.window.destroy()

    def load_last_config_set_loaded(self):
        """
            Carrega o último conjunto de configurações carregado.
        """
        # Salva conjunto de configurações como atual.
        self.current_config_set = self.config_ma.get_last_config_set_loaded()

        # Carrega o conjunto de configurações.
        self.config_ma.load_config_set(self.current_config_set)

        # Exibe home.
        self.switch_frame('home_frame')

    # ==================================================================================================================
    # Funções do SelectionFrame.
    def display_config_sets(self):
        """
            Exibe os nomes dos conjuntos de configurações.
        """
        # Apaga exibições atuais.
        self.listbox_config_sets.delete(0, 'end')

        # Pega nomes.
        config_set_names = self.config_ma.get_config_set_names()

        # Exibe os nomes.
        for name in config_set_names:
            self.listbox_config_sets.insert('end', name)

    def display_selection_title(self, title):
        """
            :param title: (String) Titulo a ser exibido.
            Exibe titulo no SelectionFrame
        """
        self.label_selection_frame_title['text'] = title

    def manage_button_select_state(self, event):
        """
            :param event: (Event) Evento tkinter.
            Muda o estado do botão de seleção conforme o evento.
        """
        if 'FocusIn' in str(event):
            # Se Alguma opção foi selecionada habilita o botão.
            self.button_select['state'] = 'normal'
        else:
            # Se o botão saiu da tela ele é desabilitado.
            self.button_select['state'] = 'disabled'
            self.window.focus()

    def select_config_set(self):
        """
            Salva o conjunto de configurações selecionado e continua com a função em espera.
        """
        # Pega o item selecionado e salva.
        selected_index = self.listbox_config_sets.curselection()[0]
        self.selected_config_set = self.listbox_config_sets.get(selected_index)

        # executa função em espera.
        self.execute_awaiting_function()

    def continue_to_create(self):
        """
            Atribuí conjunto de configuração selecionado ao campo do frame e volta para o frame de criação.
        """
        # Exibe no campo o conjunto de configurações selecionado.
        self.var_config_set_to_copy.set(self.selected_config_set)

        # Limpa variavel de seleção.
        self.selected_config_set = ''

        # Retorna para a criação.
        self.go_back()

    def continue_to_load(self):
        self.config_ma.load_config_set(self.selected_config_set)

        # Salva conjunto de configurações como atual.
        self.current_config_set = self.selected_config_set

        # Limpa variavel de seleção.
        self.selected_config_set = ''

        # Exibe home.
        self.switch_frame('home_frame')

    def ask_confirmation_to_delete(self):
        """
            Pede confirmação antes da exclusão.
        """
        self.awaiting_function = 'continue_to_delete'
        self.switch_frame('confirmation_frame')
        self.display_confirmation_info(
            'Exclusão do perfil: {}.'.format(self.selected_config_set),
            ['O perfil será excluído permanentemente.', 'Deseja continuar?']
        )

    def continue_to_delete(self):
        """
            Continua com a exlusão de conjunto de configurações exclusão.
        """
        self.config_ma.delete_config_set(self.selected_config_set)
        self.selected_config_set = ''
        self.awaiting_function = 'ask_confirmation_to_delete'

        # Exibe conclusão.
        self.display_conclusion(['Deleção realizada com sucesso!'], 'Deleção de perfil')

    def continue_to_rename(self):
        """
            Atribuí conjunto de configuração selecionado ao campo do frame e volta para o frame de renomeação.
        """
        # Exibe no campo o conjunto de configurações selecionado.
        self.var_current_config_set_name.set(self.selected_config_set)
        self.var_new_config_set_name.set(self.selected_config_set)

        # Limpa variavel de seleção.
        self.selected_config_set = ''

        # Retorna para a criação.
        self.switch_frame('rename_frame')

    # ==================================================================================================================
    # Funções do CreationFrame.
    def validate_to_create(self):
        """
            Valida nome para criação de conjunto de configurações.
        """
        # Pega nome.
        name = self.var_config_set_name.get().strip()

        # Verifica existência de nome igual.
        configs_and_warnings = {}
        if not name:
            configs_and_warnings['config_set_name'] = 'Informe um nome.'
        elif self.config_ma.config_set_exist(name):
            configs_and_warnings['config_set_name'] = 'Nome indisponível.'

        if configs_and_warnings:
            self.highlight_fields(configs_and_warnings)
            return

        # Pega nome do conjunto de configuração a ser copiado.
        config_set_to_copy = self.var_config_set_to_copy.get().strip()

        # Limpa campos
        self.var_config_set_name.set('')
        self.var_config_set_to_copy.set('')

        # Cria um conjunto de configuirações.
        self.create_config_set(name, config_set_to_copy)

    def create_config_set(self, name, config_set_to_copy):
        """
            Cria conjunto de configutações e direciona para a home.
        """
        # Copia conjunto de configurações se requisitado, senão cria outro.
        if config_set_to_copy:
            self.config_ma.copy_config_set(name, config_set_to_copy)
        else:
            self.config_ma.set_default_configs()
            self.config_ma.add_config_set(name)

        # Salva o nome do atual conjunto de configurações.
        self.current_config_set = name

        # Exibe a home.
        self.switch_frame('home_frame')

    def manage_copy_button_state(self):
        state = 'disabled'
        if self.config_ma.get_config_set_names():
            state = 'normal'
        self.button_select_to_copy['state'] = state

    # ==================================================================================================================
    # Funções do RenameFrame.
    def validate_to_rename(self):
        """
            Valida nome para renomear o conjunto de configurações.
        """
        # Pega nomes.
        current_name = self.var_current_config_set_name.get().strip()
        new_name = self.var_new_config_set_name.get().strip()

        # Verifica se há nome.
        configs_and_warnings = {}
        if not new_name:
            configs_and_warnings['new_config_set_name'] = 'Informe um nome.'
        # Verica se há mudança.
        elif current_name == new_name:
            configs_and_warnings['new_config_set_name'] = 'Informe um nome diferente.'
        elif self.config_ma.config_set_exist(new_name):
            configs_and_warnings['new_config_set_name'] = 'Nome indisponível.'

        if configs_and_warnings:
            self.highlight_fields(configs_and_warnings)
            return

        # Limpa campos.
        self.var_current_config_set_name.set('')
        self.var_new_config_set_name.set('')

        # Renomeia.
        self.rename_config_set(current_name, new_name)

    def rename_config_set(self, current_name, new_name):
        """
            Renomeia conjunto de configutações e volta ao SelectionFrame.
        """
        # Renomeia.
        self.config_ma.rename_config_set(current_name, new_name)

        # Exibe conclusão.
        self.display_conclusion(['Renomeação realizada com sucesso!'], 'Renomeação de perfil')

    # ==================================================================================================================
    # Funções do HomeFrame.
    def validate_to_delete_downloaded_chapters(self):
        """
            Deleta arquivos da pasta final que correspondem ao nome e formato dos arquivos do mangá.
        """
        # Salva informações atuais.
        self.save_configs_for_download()

        # Seleciona informações salvas.
        final_dir = self.config_ma.config_list['final_dir']
        manga_name = self.config_ma.config_list['manga_name']

        # Verifica disponibilidade de informações necessárias.
        configs_and_warnings = {}
        if not final_dir:
            configs_and_warnings['final_dir'] = 'Informe a pasta final.'
        if not manga_name:
            configs_and_warnings['manga_name'] = 'Informe o nome do mangá.'

        # Tira destaques dos campos.
        self.unhighlight()

        # Destaca campos se necessário.
        if configs_and_warnings:
            self.highlight_fields(configs_and_warnings)
            return

        # Verifica o número de capítulos armazenados.
        patterns = [r'{} - '.format(manga_name), '.pdf']
        self.chapters_files = self.system_ma.find_files(final_dir, patterns, 2)
        num_files = len(self.chapters_files)

        if num_files == 0:
            # Monta frase de aviso, onde que não capítulos.
            deletion_status = ['Não há capítulos para serem excluidos.']

            # Exibe o frame de informações com o resultado da exclusão.
            self.switch_frame('info_frame')
            self.display_info(deletion_status, 'Exclusão')
        else:
            self.awaiting_function = 'delete_chapters'
            self.switch_frame('confirmation_frame')
            self.display_confirmation_info(
                'Exclusão de capítulos', ['Os arquivos serão excluídos permanentemente.', 'Deseja continuar?']
            )

    def display_loaded_config_set_name(self):
        """
            Exibe o nome do conjuntos de configurações carregado.
        """
        self.label_loaded_config_set_name['text'] = 'Perfil carregado: {}.'.format(self.config_ma.get_last_config_set_loaded())

    def delete_chapters(self):
        """
            Excluí capítulos baixados.
        """
        # Deleta capítulos.
        self.system_ma.delete(self.chapters_files)

        # Conta o número de arquivos.
        num_files = len(self.chapters_files)
        addition = ''
        if num_files > 1:
            addition = 's'
        deletion_status = [
            f'Exclusão de {num_files} capítulo{addition} realizada com sucesso!'
        ]

        # Limpa variável.
        self.chapters_files = []

        # Exibe o frame de informações com o resultado da exclusão.
        self.switch_frame('info_frame')
        self.display_info(deletion_status, 'Exclusão')

    def kill_secondary_process(self):
        """
            Mata o processo secundário e fecha navegador se ainda aberto.
        """
        # Seleciona subprocessos.
        active = active_children()

        # Manda encerrar.
        for child in active:
            child.terminate()

        # Espera encerramento.
        for child in active:
            child.join()

        # Informa do cancelamento.
        self.display_info(['Processo cancelado.'], 'Cancelado')

        # Muda função do botão dinâmico para voltar à home.
        self.set_dynamic_button_action('go_back')

        if self.browser_handle:
            time.sleep(1)
            SystemManager.close_window(self.browser_handle)

    def validate_to_download(self):
        """
            Verifica se há as informações necessárias para realizar os downloads.
        """
        # Salva informações atuais.
        self.save_configs_for_download()

        # Verifica disponibilidade de informações necessárias.
        configs_and_warnings = {}

        # Nome do mangá.
        if not self.config_ma.config_list['manga_name']:
            configs_and_warnings['manga_name'] = 'Informe o nome do mangá.'

        # Link do capítulo inicial à ser baixado.
        if not self.config_ma.config_list['base_link']:
            configs_and_warnings['base_link'] = 'Informe o link do capítulo inicial.'

        # Pasta onde serão compilados os capítulos.
        if not self.config_ma.config_list['final_dir']:
            configs_and_warnings['final_dir'] = 'Informe a pasta de destino.'
        elif not self.system_ma.path_exist(self.config_ma.config_list['final_dir']):
            configs_and_warnings['final_dir'] = 'Informe uma pasta valida.'

        # Capitulo inicial e final.
        initial_chapter = self.config_ma.config_list['initial_chapter']
        final_chapter = self.config_ma.config_list['final_chapter']
        are_numerical = True
        if not initial_chapter:
            configs_and_warnings['initial_chapter'] = 'Informe o número do capítulo.'
        else:
            if not initial_chapter.replace('.', '').isnumeric():
                are_numerical = False
                configs_and_warnings['initial_chapter'] = 'Informe apenas números.'

        if not final_chapter:
            configs_and_warnings['final_chapter'] = 'Informe o número do capítulo.'
        else:
            if not final_chapter.replace('.', '').isnumeric():
                are_numerical = False
                configs_and_warnings['final_chapter'] = 'Informe apenas números.'

        if initial_chapter and final_chapter and are_numerical:
            if initial_chapter > final_chapter:
                configs_and_warnings['initial_chapter'] = 'Deve ser menor ou igual ao final.'

        # Pasta de download do navegador.
        if not self.config_ma.config_list['download_dir']:
            configs_and_warnings['download_dir'] = 'Informe a pasta de download do chrome.'
        elif not self.system_ma.path_exist(self.config_ma.config_list['download_dir']):
            configs_and_warnings['download_dir'] = 'Informe uma pasta valida.'

        # Pasta de edição de arquivos.
        if not self.config_ma.config_list['files_dir']:
            configs_and_warnings['files_dir'] = 'Informe uma pasta para edição de imagens.'
        elif not self.system_ma.path_exist(self.config_ma.config_list['files_dir']):
            configs_and_warnings['files_dir'] = 'Informe uma pasta valida.'

        # Localização dos quadros das imagens.
        if self.config_ma.config_list['frames_location_value'] and self.config_ma.config_list['frames_location_by'] == 'Selecione':
            configs_and_warnings['frames_location_by'] = 'Selecione um identificador.'

        # Localização das imagens.
        if self.config_ma.config_list['imgs_location_by'] == 'Selecione':
            configs_and_warnings['imgs_location_by'] = 'Selecione um identificador.'
        if not self.config_ma.config_list['imgs_location_value']:
            configs_and_warnings['imgs_location_value'] = 'Informe um valor.'

        # Localização do botão de avançar para a próxima página.
        if self.config_ma.config_list['next_page_button_location_by'] == 'Selecione':
            configs_and_warnings['next_page_button_location_by'] = 'Selecione um identificador.'
        if not self.config_ma.config_list['next_page_button_location_value']:
            configs_and_warnings['next_page_button_location_value'] = 'Informe um valor.'

        # Tira o destaque dos campos.
        self.unhighlight()

        # Se necessário, destaca campos com erro.
        if configs_and_warnings:
            self.highlight_fields(configs_and_warnings)
            return

        # Executa download.
        self.execute_download_process()

    def execute_download_process(self):
        """
            Começa a baixar o mangá.
        """
        # Limpa identificador do navegador.
        self.browser_handle = 0

        # Instancia classe necessária.
        download_ma = DownloadManager(self.config_ma)

        # Muda função do botão dinâmico para cancelar.
        self.set_dynamic_button_action('cancel')

        # Exibe frame de informações.
        self.switch_frame('info_frame')

        self.download_process = Process(target=download_ma.download, args=(self.queue,))

        # Inicia download.
        self.download_process.start()

        # Monitora a comunicação com o outro processo.
        self.monitor_communication()

        # Muda função do botão dinâmico para voltar à home.
        self.set_dynamic_button_action('go_back')

    def monitor_communication(self):
        """
            Monitora comunição com processo paralelo.
        """
        while True:
            function = self.queue.get()
            func_name = function[0]
            param1 = None
            param2 = None
            if len(function) > 1:
                param1 = function[1]
            if len(function) > 2:
                param2 = function[2]

            match func_name:
                case 'save_browser_handle':
                    self.save_browser_handle(param1)
                case 'save_last_link':
                    self.save_last_link(param1)
                case 'display_info':
                    if param2:
                        self.display_info(param1, param2)
                    else:
                        self.display_info(param1)
                case 'update_last_lines':
                    if param2:
                        self.update_last_lines(param1, param2)
                    else:
                        self.update_last_lines(param1)
                case 'kill_secondary_process':
                    self.kill_secondary_process()
                    break
                case 'end':
                    break

    def save_and_go_back(self):
        """
            Salva e volta para o frame anterior.
        """
        self.save_configs_for_download()
        self.go_back()

    def copy_last_link_to_base_link(self):
        """
            Sobreescreve o link base com o último link acessado.
        """
        self.config_fields['base_link']['var'].set(self.config_fields['last_link']['var'].get().strip())

    # ==================================================================================================================
    # Funções do ConfigFrame.
    @staticmethod
    def select_dir(title, variable):
        """
            :param title: (String) Título da janela de seleção de pastas.
            :param variable: (tk.StringVar) Variável que receberá o caminho.
            Abre janela para seleção de pasta e preenche no campo selecionado.
        """
        # Abre janela de seleção de pastas.
        new_dir = askdirectory(title=title)

        # Se informado o caminho, preenche o campo.
        if new_dir:
            variable.set(str(Path(new_dir)))

    def ask_confirmation_to_reset(self):
        """
            Pede confirmação antes da exclusão.
        """
        self.awaiting_function = 'reset_config_set'
        self.switch_frame('confirmation_frame')
        self.display_confirmation_info(
            'Reconfiguração',
            ['O perfil receberá as configurações padrões.', 'Deseja continuar?']
        )

    def reset_config_set(self):
        """
            Atribuí as configurações padrões..
        """
        self.config_ma.reset_config_set()
        self.unhighlight()
        self.update_all_fields()
        self.display_conclusion(['Configuração padrão aplicada.'], 'Configuração padrão')

    # ==================================================================================================================
    # Funções do ConfirmationFrame.
    def display_confirmation_info(self, title, description):
        """
            :param title: (String) Título do frame de confirmação.
            :param description: (Array de Strings) Linhas da descrição do frame de confirmação.
            Exibe informações no ConfirmationFrame.
        """
        # Instancia classe necessária.
        text_formatter = TextManager()

        # Formata o título.
        formatted_title = text_formatter.format_text([title], self.confirmation_frame_max_char_per_line)

        # Atribui o título.
        self.label_confirmation_title['text'] = formatted_title

        # Formata a descrição.
        formatted_description = text_formatter.format_text(description, self.confirmation_frame_max_char_per_line)

        # Atribui a descrição.
        self.label_confirmation_description['text'] = formatted_description

        # Atualiza tela.
        self.window.update()

    def cancel(self):
        """
            Cancela função em espera.
        """
        # Volta para o frame anterior.
        self.go_back()

    # ==================================================================================================================
    # Funções do InfoFrame.
    def display_conclusion(self, message, title):
        """
            :param message: (Array de strings) linhas da mensagem a ser exibida.
            :param title: (String titulo da mensagem)
            Exibe conclusão de processo
        """
        self.set_dynamic_button_action('go_back')
        self.display_info(message, title)
        self.switch_frame('info_frame')

    def execute_dynamic_button_action(self):
        """
            Executa a função do botão dinâmico.
        """
        if self.dynamic_button_action == 'go_back':
            # Limpa campo de informações e retorna ao frame anterior.
            self.clear_info()
            self.go_back()
        elif self.dynamic_button_action == 'cancel':
            self.queue.put(['kill_secondary_process'])

    def set_dynamic_button_action(self, action):
        """
            Define função do botão dinâmico.
        """
        if action == 'cancel':
            self.dynamic_button_action = 'cancel'
            self.dynamic_button['text'] = 'Cancelar'
        elif action == 'go_back':
            self.dynamic_button_action = 'go_back'
            self.dynamic_button['text'] = 'Voltar'

    def display_info(self, info_lines, info_title=''):
        """
            :param info_lines: (Array de Strings) Lista com linhas a serem exibidas.
            :param info_title: (String) Título a ser exibido na janela de informações.
            Apresenta informações no frame de informações.
        """
        # Instancia classe necessária.
        text_formatter = TextManager()

        # Atribui título.
        if info_title:
            self.label_info_title['text'] = info_title

        if info_lines:
            # Formata texto.
            info_text = text_formatter.format_text(info_lines, self.info_frame_max_char_per_line)

            # Verifica o número de linhas exibidas.
            num_lines = len(self.get_info())

            if num_lines > 1:
                info_text = '\n' + info_text

            # Exibe texto.
            self.scrolled_textbox['state'] = 'normal'
            self.scrolled_textbox.insert('end', info_text)
            self.scrolled_textbox['state'] = 'disabled'

            # Movimenta scrool para baixo.
            self.scrolled_textbox.yview_scroll(len(info_lines) * 26, 'pixels')

        # Atualiza tela.
        self.window.update()

    def update_last_lines(self, info_lines, lines_to_update=1):
        """
            :param info_lines: (Array de Strings) Lista de linhas a serem apresentadas.
            :param lines_to_update: (Int) Número de linhas que serão atualizadas.
            Substitui últimas linhas exibidas.
        """

        # Verifica o número de linhas exibidas.
        num_lines = len(self.get_info())

        # Define índice inicial de exclusão.
        initial_delete_index = num_lines - lines_to_update

        # Verifica se podem ser excluidas tantas linhas quanto solicitados.
        if initial_delete_index < 1:
            initial_delete_index = 1

        # Apaga linhas.
        self.scrolled_textbox['state'] = 'normal'
        self.scrolled_textbox.delete(f'{initial_delete_index}.0', 'end')
        self.scrolled_textbox['state'] = 'disabled'

        # Exibe novas linhas.
        self.display_info(info_lines)

    def get_info(self):
        """
            :return: (Array de Strings) Lista com as linhas exibidas.
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


# TODO: RETIRAR
if __name__ == '__main__':
    gui = GUI()
    gui.window.mainloop()