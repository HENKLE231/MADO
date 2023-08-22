from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext
from tkinter.filedialog import askdirectory
from functools import partial
from multiprocessing import Process, Queue
from ConfigManager import ConfigManager
from SystemManager import SystemManager
from TextFormatter import TextFormatter
from DownloadManager import DownloadManager


class GUI:
    def __init__(self):
        # RootWindow.
        # Variáveis.
        self.window = tk.Tk()
        self.title = 'Mangá Downloader'
        self.window.title(self.title)
        self.secondary_process_id = 0
        self.default_padx = 2
        self.default_pady = 2
        self.previous_frame = 'home_frame'
        self.current_frame = ''
        self.app_frames = {}
        self.config_fields = {}

        # =======================================================================================================
        # HomeFrame.
        # Variáveis.
        self.home_frame = tk.Frame(self.window)
        self.var_initial_chapter = tk.StringVar()
        self.var_final_chapter = tk.StringVar()

        # Elementos.
        # Linha 0.
        self.label_manga_name = tk.Label(self.home_frame, text='Home', font=24)
        self.label_manga_name.grid(row=0, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

        # Linha 1.
        self.label_initial_chapter = tk.Label(self.home_frame, text='Capítulo Inicial:', anchor='e')
        self.label_initial_chapter.grid(row=1, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_initial_chapter = tk.Frame(self.home_frame)
        self.frame_initial_chapter.columnconfigure(0, weight=1)
        self.frame_initial_chapter.grid(row=1, column=1, columnspan=2, padx=5, sticky='we')
        self.warning_label_initial_chapter = tk.Label(self.frame_initial_chapter, text='', fg='red')
        self.border_initial_chapter = tk.Frame(self.frame_initial_chapter)
        self.border_initial_chapter.columnconfigure(0, weight=1)
        self.border_initial_chapter.grid(row=1, column=0, sticky='nswe')
        self.entry_initial_chapter = tk.Entry(self.border_initial_chapter, textvariable=self.var_initial_chapter)
        self.entry_initial_chapter.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 2.
        self.label_final_chapter = tk.Label(self.home_frame, text='Capítulo Final:', anchor='e')
        self.label_final_chapter.grid(row=2, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_final_chapter = tk.Frame(self.home_frame)
        self.frame_final_chapter.columnconfigure(0, weight=1)
        self.frame_final_chapter.grid(row=2, column=1, columnspan=2, padx=5, sticky='we')
        self.warning_label_final_chapter = tk.Label(self.frame_final_chapter, text='', fg='red')
        self.border_final_chapter = tk.Frame(self.frame_final_chapter)
        self.border_final_chapter.columnconfigure(0, weight=1)
        self.border_final_chapter.grid(row=1, column=0, sticky='nswe')
        self.entry_final_chapter = tk.Entry(self.border_final_chapter, textvariable=self.var_final_chapter)
        self.entry_final_chapter.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 3.
        command = partial(self.delete_downloaded_chapters)
        self.button_config = tk.Button(
            self.home_frame, text='Excluir capítulos\nbaixados', command=command
        )
        self.button_config.grid(row=3, column=0, padx=3, pady=3, sticky='nswe')
        command = partial(self.switch_frame, 'config_frame')
        self.button_config = tk.Button(self.home_frame, text='Configurações', command=command)
        self.button_config.grid(row=3, column=1, padx=3, pady=3, sticky='nswe')
        command = partial(self.verify_for_run)
        self.button_run = tk.Button(self.home_frame, text='Baixar', command=command)
        self.button_run.grid(row=3, column=2, padx=3, pady=3, sticky='nswe')

        # Adiciona a lista de widgets que podem ser destacados.
        self.config_fields['initial_chapter'] = {
            'display_frame': 'home_frame',
            'warning_label': self.warning_label_initial_chapter,
            'border': self.border_initial_chapter,
            'entry': self.entry_initial_chapter,
            'var': self.var_initial_chapter
        }
        self.config_fields['final_chapter'] = {
            'display_frame': 'home_frame',
            'warning_label': self.warning_label_final_chapter,
            'border': self.border_final_chapter,
            'entry': self.entry_final_chapter,
            'var': self.var_final_chapter
        }

        # Adiciona à lista de janelas existentes.
        self.app_frames['home_frame'] = self.home_frame

        # =======================================================================================================
        # ConfigFrame.
        # Variáveis.
        self.config_frame = tk.Frame(self.window)
        self.var_manga_name = tk.StringVar()
        self.var_base_link = tk.StringVar()
        self.var_last_link_opened = tk.StringVar()
        self.var_final_dir = tk.StringVar()
        self.var_download_dir = tk.StringVar()
        self.var_files_dir = tk.StringVar()
        self.var_frames_location_by = tk.StringVar()
        self.var_frames_location_value = tk.StringVar()
        self.var_imgs_location_by = tk.StringVar()
        self.var_imgs_location_value = tk.StringVar()
        self.var_next_page_button_location_by = tk.StringVar()
        self.var_next_page_button_location_value = tk.StringVar()

        # Elementos.
        # Linha 0.
        self.label_config = tk.Label(self.config_frame, text='Configurações', font=24)
        self.label_config.grid(row=0, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

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

        # Linha 2.
        self.label_base_link = tk.Label(self.config_frame, text='Link do capítulo inicial:', anchor='e')
        self.label_base_link.grid(row=2, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_base_link = tk.Frame(self.config_frame)
        self.frame_base_link.columnconfigure(0, weight=1)
        self.frame_base_link.grid(row=2, column=1, sticky='we')
        self.warning_label_base_link = tk.Label(self.frame_base_link, text='', fg='red')
        self.border_base_link = tk.Frame(self.frame_base_link)
        self.border_base_link.columnconfigure(0, weight=1)
        self.border_base_link.grid(row=1, column=0, sticky='nswe')
        self.entry_base_link = tk.Entry(self.border_base_link, textvariable=self.var_base_link)
        self.entry_base_link.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 3.
        self.label_last_link_opened = tk.Label(self.config_frame, text='Último link aberto:', anchor='e')
        self.label_last_link_opened.grid(row=3, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_last_link_opened = tk.Frame(self.config_frame)
        self.frame_last_link_opened.columnconfigure(0, weight=1)
        self.frame_last_link_opened.grid(row=3, column=1, sticky='we')
        self.warning_label_last_link_opened = tk.Label(self.frame_last_link_opened, text='', fg='red')
        self.border_last_link_opened = tk.Frame(self.frame_last_link_opened)
        self.border_last_link_opened.columnconfigure(0, weight=1)
        self.border_last_link_opened.grid(row=1, column=0, sticky='nswe')
        self.entry_last_link_opened = tk.Entry(self.border_last_link_opened, textvariable=self.var_last_link_opened)
        self.entry_last_link_opened.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 4.
        self.label_final_dir = tk.Label(self.config_frame, text='Pasta final:', anchor='e')
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
        self.label_frames_location_by = tk.Label(self.config_frame, text='Procurar quadros por:', anchor='e')
        self.label_frames_location_by.grid(row=7, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_frames_location_by = tk.Frame(self.config_frame)
        self.frame_frames_location_by.columnconfigure(0, weight=1)
        self.frame_frames_location_by.grid(row=7, column=1, sticky='we')
        self.warning_label_frames_location_by = tk.Label(self.frame_frames_location_by, text='', fg='red')
        self.border_frames_location_by = tk.Frame(self.frame_frames_location_by)
        self.border_frames_location_by.columnconfigure(0, weight=1)
        self.border_frames_location_by.grid(row=1, column=0, sticky='nswe')
        self.option_menu_frames_location_by = tk.OptionMenu(
        self.border_frames_location_by,  self.var_frames_location_by,
            "Selecione", "id", "name", "xpath", "link text", "partial link text", "tag name", "class name", "css selector",
        )
        self.option_menu_frames_location_by.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 8.
        self.label_frames_location_value = tk.Label(self.config_frame, text='Valor:', anchor='e')
        self.label_frames_location_value.grid(row=8, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_frames_location_value = tk.Frame(self.config_frame)
        self.frame_frames_location_value.columnconfigure(0, weight=1)
        self.frame_frames_location_value.grid(row=8, column=1, sticky='we')
        self.warning_label_frames_location_value = tk.Label(self.frame_frames_location_value, text='', fg='red')
        self.border_frames_location_value = tk.Frame(self.frame_frames_location_value)
        self.border_frames_location_value.columnconfigure(0, weight=1)
        self.border_frames_location_value.grid(row=1, column=0, sticky='nswe')
        self.entry_frames_location_value = tk.Entry(self.border_frames_location_value, textvariable=self.var_frames_location_value)
        self.entry_frames_location_value.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 9.
        self.label_imgs_location_by = tk.Label(self.config_frame, text='Procurar imagens por:', anchor='e')
        self.label_imgs_location_by.grid(row=9, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_imgs_location_by = tk.Frame(self.config_frame)
        self.frame_imgs_location_by.columnconfigure(0, weight=1)
        self.frame_imgs_location_by.grid(row=9, column=1, sticky='we')
        self.warning_label_imgs_location_by = tk.Label(self.frame_imgs_location_by, text='', fg='red')
        self.border_imgs_location_by = tk.Frame(self.frame_imgs_location_by)
        self.border_imgs_location_by.columnconfigure(0, weight=1)
        self.border_imgs_location_by.grid(row=1, column=0, sticky='nswe')
        self.option_menu_imgs_location_by = tk.OptionMenu(
        self.border_imgs_location_by,  self.var_imgs_location_by,
            "Selecione", "id", "name", "xpath", "link text", "partial link text", "tag name", "class name", "css selector",
        )
        self.option_menu_imgs_location_by.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 10.
        self.label_imgs_location_value = tk.Label(self.config_frame, text='Valor:', anchor='e')
        self.label_imgs_location_value.grid(row=10, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_imgs_location_value = tk.Frame(self.config_frame)
        self.frame_imgs_location_value.columnconfigure(0, weight=1)
        self.frame_imgs_location_value.grid(row=10, column=1, sticky='we')
        self.warning_label_imgs_location_value = tk.Label(self.frame_imgs_location_value, text='', fg='red')
        self.border_imgs_location_value = tk.Frame(self.frame_imgs_location_value)
        self.border_imgs_location_value.columnconfigure(0, weight=1)
        self.border_imgs_location_value.grid(row=1, column=0, sticky='nswe')
        self.entry_imgs_location_value = tk.Entry(self.border_imgs_location_value, textvariable=self.var_imgs_location_value)
        self.entry_imgs_location_value.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 11.
        self.label_next_page_button_location_by = tk.Label(self.config_frame, text='Procurar botão de avançar por:', anchor='e')
        self.label_next_page_button_location_by.grid(row=11, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_next_page_button_location_by = tk.Frame(self.config_frame)
        self.frame_next_page_button_location_by.columnconfigure(0, weight=1)
        self.frame_next_page_button_location_by.grid(row=11, column=1, sticky='we')
        self.warning_label_next_page_button_location_by = tk.Label(self.frame_next_page_button_location_by, text='', fg='red')
        self.border_next_page_button_location_by = tk.Frame(self.frame_next_page_button_location_by)
        self.border_next_page_button_location_by.columnconfigure(0, weight=1)
        self.border_next_page_button_location_by.grid(row=1, column=0, sticky='nswe')
        self.option_menu_next_page_button_location_by = tk.OptionMenu(
        self.border_next_page_button_location_by,  self.var_next_page_button_location_by,
            "Selecione", "id", "name", "xpath", "link text", "partial link text", "tag name", "class name", "css selector",
        )
        self.option_menu_next_page_button_location_by.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 12.
        self.label_next_page_button_location_value = tk.Label(self.config_frame, text='Valor:', anchor='e')
        self.label_next_page_button_location_value.grid(row=12, column=0, padx=5, pady=1, sticky='nswe')
        self.frame_next_page_button_location_value = tk.Frame(self.config_frame)
        self.frame_next_page_button_location_value.columnconfigure(0, weight=1)
        self.frame_next_page_button_location_value.grid(row=12, column=1, sticky='we')
        self.warning_label_next_page_button_location_value = tk.Label(self.frame_next_page_button_location_value, text='', fg='red')
        self.border_next_page_button_location_value = tk.Frame(self.frame_next_page_button_location_value)
        self.border_next_page_button_location_value.columnconfigure(0, weight=1)
        self.border_next_page_button_location_value.grid(row=1, column=0, sticky='nswe')
        self.entry_next_page_button_location_value = tk.Entry(self.border_next_page_button_location_value, textvariable=self.var_next_page_button_location_value)
        self.entry_next_page_button_location_value.grid(padx=self.default_padx, pady=self.default_pady, sticky='nswe')

        # Linha 13.
        self.bottom_buttons_frame = tk.Frame(self.config_frame)
        self.bottom_buttons_frame.grid(row=13, column=1, padx=2)
        self.space = tk.Label(self.bottom_buttons_frame, text='')
        self.space.grid(row=0, column=0, padx=100)
        command = partial(self.reset_configs)
        self.button_reset = tk.Button(self.bottom_buttons_frame, text='Configuração padrão', command=command)
        self.button_reset.grid(row=0, column=1, ipadx=20, pady=5, sticky='nswe')
        command = partial(self.switch_frame, 'home_frame')
        self.button_back = tk.Button(self.config_frame, text='Voltar', command=command)
        self.button_back.grid(row=13, column=2, ipadx=20, padx=self.default_padx, pady=5, sticky='nswe')

        # Adiciona a lista de widgets que podem ser destacados.
        self.config_fields['manga_name'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_manga_name,
            'border': self.border_manga_name,
            'entry': self.entry_manga_name,
            'var': self.var_manga_name
        }
        self.config_fields['base_link'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_base_link,
            'border': self.border_base_link,
            'entry': self.entry_base_link,
            'var': self.var_base_link
        }
        self.config_fields['last_link_opened'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_last_link_opened,
            'border': self.border_last_link_opened,
            'entry': self.entry_last_link_opened,
            'var': self.var_last_link_opened
        }
        self.config_fields['final_dir'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_final_dir,
            'border': self.border_final_dir,
            'entry': self.entry_final_dir,
            'var': self.var_final_dir
        }
        self.config_fields['download_dir'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_download_dir,
            'border': self.border_download_dir,
            'entry': self.entry_download_dir,
            'var': self.var_download_dir
        }
        self.config_fields['files_dir'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_files_dir,
            'border': self.border_files_dir,
            'entry': self.entry_files_dir,
            'var': self.var_files_dir
        }
        self.config_fields['frames_location_by'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_frames_location_by,
            'border': self.border_frames_location_by,
            'entry': self.option_menu_frames_location_by,
            'var': self.var_frames_location_by
        }
        self.config_fields['frames_location_value'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_frames_location_value,
            'border': self.border_frames_location_value,
            'entry': self.entry_frames_location_value,
            'var': self.var_frames_location_value
        }
        self.config_fields['imgs_location_by'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_imgs_location_by,
            'border': self.border_imgs_location_by,
            'entry': self.option_menu_imgs_location_by,
            'var': self.var_imgs_location_by
        }
        self.config_fields['imgs_location_value'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_imgs_location_value,
            'border': self.border_imgs_location_value,
            'entry': self.entry_imgs_location_value,
            'var': self.var_imgs_location_value
        }
        self.config_fields['next_page_button_location_by'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_next_page_button_location_by,
            'border': self.border_next_page_button_location_by,
            'entry': self.option_menu_next_page_button_location_by,
            'var': self.var_next_page_button_location_by
        }
        self.config_fields['next_page_button_location_value'] = {
            'display_frame': 'config_frame',
            'warning_label': self.warning_label_next_page_button_location_value,
            'border': self.border_next_page_button_location_value,
            'entry': self.entry_next_page_button_location_value,
            'var': self.var_next_page_button_location_value
        }

        # Adiciona às janelas existentes.
        self.app_frames['config_frame'] = self.config_frame

        # =======================================================================================================
        # InfoFrame.
        # Variáveis.
        self.info_frame = tk.Frame(self.window)
        self.num_info_lines = 7
        self.max_char_per_line = 50
        self.dynamic_button_action = 'go_back'
        self.dynamic_button_text = 'Voltar'

        # Elementos.
        # Linha 0.
        self.label_info_title = tk.Label(self.info_frame)
        self.label_info_title.grid(row=0, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

        # Linha 1.
        self.scrolled_textbox = scrolledtext.ScrolledText(
            self.info_frame, width=self.max_char_per_line, height=self.num_info_lines, cursor='arrow'
        )
        self.scrolled_textbox.grid(row=1, column=0, columnspan=3, padx=5, pady=1, sticky='nswe')

        # Linha 2.
        command = partial(self.execute_dynamic_button_action)
        self.dynamic_button = tk.Button(self.info_frame, text=self.dynamic_button_text, command=command)
        self.dynamic_button.grid(row=2, column=2, padx=5, pady=5, sticky='nswe')

        # Adiciona à lista de janelas existentes.
        self.app_frames['info_frame'] = self.info_frame

        # Exibe tela inicial
        self.switch_frame('home_frame')

        # =======================================================================================================
        # Carrega configurações.
        self.update_all_fields()

    # =======================================================================================================
    # Funções gerais.
    def switch_frame(self, next_frame):
        """
            :param next_frame: (String) Nome do próximo frame.
            Exibe o frame requerido.
        """

        # Salva o nome do frame atual caso seja necessário voltar.
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

        # Instancia a classe de Configurações.
        config_ma = ConfigManager()

        # Varre os campos.
        for config_name, widgets in self.config_fields.items():
            # Edita a configuração.
            config_ma.edit_config(config_name, widgets['var'].get())

        # Salva as configurações.
        config_ma.save_configs()

    def highlight_fields(self, configs_and_warnings):
        """
            :param configs_and_warnings: (Dict) Dicionário com os nomes das variáveis como chaves e
            avisos como valores.
            Destaca campos com informações incorretas.
        """
        target_frame = 'home_frame'
        target_config_name = ''

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
        config_ma = ConfigManager()
        for config_name, field in self.config_fields.items():
            field['var'].set(config_ma.config_list[config_name])

    # =======================================================================================================
    # Funções do HomeFrame.
    def delete_downloaded_chapters(self):
        """
            Deleta arquivos da pasta final que correspondem ao nome do mangá.
        """
        # Salva informações atuais.
        self.save_config_changes()

        # Instancia classes necessárias.
        config_ma = ConfigManager()
        system_ma = SystemManager()

        # Seleciona informações salvas.
        final_dir = config_ma.config_list['final_dir']
        manga_name = config_ma.config_list['manga_name']

        # Verifica disponibilidade de informações necessárias.
        configs_and_warnings = {}
        if not final_dir:
            configs_and_warnings['final_dir'] = 'Informe a pasta final.'
        if not manga_name:
            configs_and_warnings['manga_name'] = 'Informe o nome do mangá.'

        # Tira destaques dos campos.
        self.unhighlight()

        # Destaca campos.
        if configs_and_warnings:
            self.highlight_fields(configs_and_warnings)
            return

        # Verifica o número de capítulos armazenados.
        patterns = [r'{} - '.format(manga_name), '.pdf']
        chapters_files = system_ma.find_files(final_dir, patterns, 2)
        num_files = len(chapters_files)

        if num_files == 0:
            # Monta frase de aviso, onde que não capítulos.
            deletion_status = ['Não há capítulos para serem excluidos.']
        else:
            # Deleta capítulos.
            system_ma.delete(chapters_files)

            addition = ''
            if num_files > 1:
                addition = 's'
            deletion_status = [
                f'Exclusão de {num_files} capítulo{addition} realizada com sucesso!'
            ]

        # Exibe o frame de informações com o resultado da exclusão.
        self.switch_frame('info_frame')
        self.show_info(deletion_status, 'Exclusão')

    def save_secondary_process_id(self, process_id):
        """
            :param process_id: (Int) Identificador do processo.
            Salva o PID..
        """
        self.secondary_process_id = process_id

    def kill_secondary_process(self):
        """
            Mata o processo secundario.
        """
        SystemManager.end_process('pid', self.secondary_process_id)

    def verify_for_run(self):
        """
            Verifica se há as informações necessárias para realizar os downloads.
        """
        # Salva informações atuais.
        self.save_config_changes()

        # Instancia classes necessárias.
        config_ma = ConfigManager()
        system_ma = SystemManager()

        # Verifica disponibilidade de informações necessárias.
        configs_and_warnings = {}

        # Nome do mangá.
        if not config_ma.config_list['manga_name']:
            configs_and_warnings['manga_name'] = 'Informe o nome do mangá.'

        # Link do capítulo inicial à ser baixado.
        if not config_ma.config_list['base_link']:
            configs_and_warnings['base_link'] = 'Informe o link do capítulo inicial.'

        # Pasta onde serão compilados os capítulos.
        if not config_ma.config_list['final_dir']:
            configs_and_warnings['final_dir'] = 'Informe a pasta de destino.'
        elif not system_ma.path_exist(config_ma.config_list['final_dir']):
            configs_and_warnings['final_dir'] = 'Informe uma pasta valida.'

        # Capitulo inicial e final.
        initial_chapter = config_ma.config_list['initial_chapter']
        final_chapter = config_ma.config_list['final_chapter']
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
        if not config_ma.config_list['download_dir']:
            configs_and_warnings['download_dir'] = 'Informe a pasta de download do chrome.'
        elif not system_ma.path_exist(config_ma.config_list['download_dir']):
            configs_and_warnings['download_dir'] = 'Informe uma pasta valida.'

        # Pasta de para edição de arquivos.
        if not config_ma.config_list['files_dir']:
            configs_and_warnings['files_dir'] = 'Informe uma pasta para edição de imagens.'
        elif not system_ma.path_exist(config_ma.config_list['files_dir']):
            configs_and_warnings['files_dir'] = 'Informe uma pasta valida.'
            
        # Localização dos quadros das imagens.
        if config_ma.config_list['frames_location_value'] and config_ma.config_list['frames_location_by'] == 'Selecione':
            configs_and_warnings['frames_location_by'] = 'Selecione um identificador.'

        # Localização das imagens.
        if config_ma.config_list['imgs_location_by'] == 'Selecione':
            configs_and_warnings['imgs_location_by'] = 'Selecione um identificador.'
        if not config_ma.config_list['imgs_location_value']:
            configs_and_warnings['imgs_location_value'] = 'Informe um valor.'

        # Localização do botão de avançar para a próxima página.
        if config_ma.config_list['next_page_button_location_by'] == 'Selecione':
            configs_and_warnings['next_page_button_location_by'] = 'Selecione um identificador.'
        if not config_ma.config_list['next_page_button_location_value']:
            configs_and_warnings['next_page_button_location_value'] = 'Informe um valor.'

        # Tira o destaque dos campos.
        self.unhighlight()

        if configs_and_warnings:
            # Destaca campos com erro.
            self.highlight_fields(configs_and_warnings)
            return

        # Executa download.
        self.run()

    def run(self):
        """
            Começa a baixar o mangá.
        """
        # Instancia classes necessárias.
        system_ma = SystemManager()
        download_ma = DownloadManager()

        # Muda função do botão dinâmico para cancelar.
        self.set_dynamic_button_action('cancel')

        # Exibe frame de informações.
        self.switch_frame('info_frame')

        # Instancia Queue para comunicação entre processos.
        queue = Queue()
        download_process = Process(target=download_ma.start_download, args=(queue, ))

        # Inicia download.
        download_process.start()

        # Verifica constantemente mensagens do outro processo.
        while True:
            function = queue.get()
            func_name = function[0]
            param1 = None
            param2 = None
            if len(function) > 1:
                param1 = function[1]
            if len(function) > 2:
                param2 = function[2]

            match func_name:
                case 'save_secondary_process_id':
                    self.save_secondary_process_id(param1)
                case 'show_info':
                    if param2:
                        self.show_info(param1, param2)
                    else:
                        self.show_info(param1)
                case 'update_last_lines':
                    if param2:
                        self.update_last_lines(param1, param2)
                    else:
                        self.update_last_lines(param1)
                case 'close_windows':
                    system_ma.close_windows(param1)
                case 'kill_secondary_process':
                    self.kill_secondary_process()
                    break
                case 'end':
                    break

        # Muda função do botão dinâmico para voltar à home.
        self.set_dynamic_button_action('go_back')

    # =======================================================================================================
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

    def reset_configs(self):
        """
            Retorna o programa às suas configurações iniciais.
        """
        config_ma = ConfigManager()
        system_ma = SystemManager()
        system_ma.delete([config_ma.config_list['config_file']])
        self.unhighlight()
        self.update_all_fields()

    # =======================================================================================================
    # Funções do InfoFrame.
    def execute_dynamic_button_action(self):
        """
            Executa a função do botão dinâmico.
        """
        if self.dynamic_button_action == 'go_back':
            # Limpa campo de informações e volta ao frame anterior.
            self.clear_info()
            self.switch_frame(self.previous_frame)
        elif self.dynamic_button_action == 'cancel':
            # Mata processo secundário.
            self.kill_secondary_process()
            # Muda função do botão dinâmico para voltar à home.
            self.set_dynamic_button_action('go_back')

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

    def show_info(self, info_lines, info_title=''):
        """
            :param info_lines: (Array de Strings) Lista com linhas a serem exibidas.
            :param info_title: (String) Título a ser exibido na janela de informações.
            Apresenta informações no frame de informações.
        """
        # Instancia classes necessárias.
        text_formatter = TextFormatter()

        # Atribui título.
        if info_title:
            self.label_info_title['text'] = info_title

        # Verifica o número de linhas exibidas.
        num_lines = len(self.get_info())

        if info_lines:
            # Formata texto.
            info_lines = text_formatter.format_text(info_lines, self.max_char_per_line)

            # Exibe texto.
            self.scrolled_textbox['state'] = 'normal'
            for i, line in enumerate(info_lines):
                if num_lines > 1 or i > 0:
                    self.scrolled_textbox.insert('end', f'\n{line}')
                else:
                    self.scrolled_textbox.insert('end', f'{line}')
            self.scrolled_textbox['state'] = 'disabled'
            self.scrolled_textbox.yview_scroll(len(info_lines) * 26, 'pixels')

        # Atualiza tela.
        self.window.update()

    def update_last_lines(self, info_lines, lines_to_update=1):
        """
            :param info_lines: (Array) Lista de linhas de texto para substituir a última linha apresentada.
            :param lines_to_update: (Int) Número de linhas que serão atualizadas.
            Substitui últimas linhas exibidas.
        """

        # Verifica o número de linhas exibidas.
        num_lines = len(self.get_info())

        # Define índice inical de exclusão.
        initial_delete_index = num_lines - lines_to_update

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
