from SystemManager import SystemManipulator as SystemMa
from pathlib import Path
import os


class Config:
    def __init__(self):
        system_ma = SystemMa()
        self.cwd = os.getcwd()
        self.config_lines = []
        self.manga_name = 'Martial Peak'
        self.base_link = r'https://manhuaplus.com/manga/martial-peak/chapter-'
        self.drive_url = ''
        self.phone_dir = ''
        self.pc_dir = ''
        self.initial_chapter = 1
        self.final_chapter = 1
        self.imgs_dir = str(Path(r'{}\imgs'.format(self.cwd)))
        self.download_dir = str(Path(r'{}\Downloads'.format(system_ma.user_dir)))
        self.files_dir = str(Path(r'{}\files_for_chapters'.format(self.cwd)))
        self.chapters_dir = str(Path(r'{}\chapters'.format(self.cwd)))
        self.download = True
        self.transfer = True
        self.final_dir = 'Celular'
        self.delete_chapters = True
        self.gui_initial_point = 100, 100

        # Carrega configurações.
        self.load_configs()

    def load_configs(self):
        """
            Carrega configurações.
        """
        try:
            # Carrega informações do arquivo de configurações.
            config_txt = open(r'{}\Config.txt'.format(self.cwd), 'r')
            config_lines = config_txt.readlines()
            config_txt.close()
            self.config_lines = [line.replace('\n', '') for line in config_lines]
    
            # Atribui valores.
            self.manga_name = self.get_config('manga_name')
            self.base_link = self.get_config('base_link')
            self.drive_url = self.get_config('drive_url')
            self.phone_dir = self.get_config('phone_dir')
            self.pc_dir = self.get_config('pc_dir')
            self.initial_chapter = self.get_config('initial_chapter')
            self.final_chapter = self.get_config('final_chapter')
            self.imgs_dir = self.get_config('imgs_dir')
            self.download_dir = self.get_config('download_dir')
            self.files_dir = self.get_config('files_dir')
            self.chapters_dir = self.get_config('chapters_dir')
            self.final_dir = self.get_config('final_dir')
            self.download = self.get_config('download') == 'True'
            self.transfer = self.get_config('transfer') == 'True'
            self.delete_chapters = self.get_config('delete_chapters') == 'True'
            self.gui_initial_point = self.get_config('gui_initial_point')
        except:
            self.create_default_configs_file(self.load_configs)

    def create_default_configs_file(self, callback):
        """
            :param callback: (function) Função a ser chamada no final dessa.
            Cria arquivo padrão de configurações.
        """
        configs_dict = {
            'manga_name': self.manga_name,
            'base_link': self.base_link,
            'drive_url': self.drive_url,
            'phone_dir': self.phone_dir,
            'pc_dir': self.pc_dir,
            'initial_chapter': self.initial_chapter,
            'final_chapter': self.initial_chapter,
            'imgs_dir': self.imgs_dir,
            'download_dir': self.download_dir,
            'files_dir': self.files_dir,
            'chapters_dir': self.chapters_dir,
            'final_dir': self.final_dir,
            'download': self.download,
            'transfer': self.transfer,
            'delete_chapters': self.delete_chapters,
            'gui_initial_point': self.gui_initial_point
        }
        with open(r'{}\Config.txt'.format(self.cwd), 'w') as config_txt:
            for config_name in configs_dict.keys():
                config_txt.write('{}={}\n'.format(config_name, configs_dict[config_name]))
        callback()

    def get_config(self, config_name):
        """
            :param config_name: (String) nome da configuração.
            :return: (String) Valor da configuração.
        """
        for line in self.config_lines:
            if line.startswith('{}='.format(config_name)):
                return line[line.index('=')+1:]

    @staticmethod
    def find_line(start_with, lines):
        """
            :param start_with: (String) Inicio da linha desejada.
            :param lines: (Array) Lista com todas as linhas.
            :return: (Int) Indice da linha, se não encontrada retorna -1.
        """
        line_index = -1
        for i, line in enumerate(lines):
            if line.startswith(start_with):
                line_index = i
                break
        return line_index

    def edit_config(self, config_name, value):
        """
            :param config_name: (String) Nome da configuração.
            :param value: (String) Configuração.
            Edita valor da variável na instância.
        """
        config_index = self.find_line(f'{config_name}=', self.config_lines)
        if config_index != -1:
            self.config_lines[config_index] = r'{}={}'.format(config_name, value)

    def save_configs(self):
        """
            Salva as variáveis da instância no arquivo de configurações.
        """
        with open(r'{}\Config.txt'.format(self.cwd), 'w') as config_txt:
            for line in self.config_lines:
                config_txt.write('{}\n'.format(line))
    
    def get_configs_dict(self):
        """
            :return: (Dict) Dicionário com os nomes e valores de todas as configurações.
        """
        configs_dict = {
            'manga_name': '',
            'base_link': '',
            'drive_url': '',
            'phone_dir': '',
            'pc_dir': '',
            'initial_chapter': '',
            'final_chapter': '',
            'imgs_dir': '',
            'download_dir': '',
            'files_dir': '',
            'chapters_dir': '',
            'final_dir': '',
            'download': '',
            'transfer': '',
            'delete_chapters': '',
            'gui_initial_point': ''
        }
        for key in configs_dict.keys():
            configs_dict[key] = self.get_config(key)

        configs_dict['download'] = configs_dict['download'] == 'True'
        configs_dict['transfer'] = configs_dict['transfer'] == 'True'
        configs_dict['delete_chapters'] = configs_dict['delete_chapters'] == 'True'

        return configs_dict
