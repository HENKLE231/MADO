from SystemManager import SystemManager as SystemMa
from pathlib import Path
import os


class ConfigManager:
    def __init__(self):
        system_ma = SystemMa()

        self.config_list = {
            # Mangá.
            'manga_name': '',
            'base_link': '',
            'last_link': '',
            'initial_chapter': 1,
            'final_chapter': 1,
            'frames_location_by': 'Selecione',
            'frames_location_value': '',
            'imgs_location_by': 'Selecione',
            'imgs_location_value': '',
            'next_page_button_location_by': 'Selecione',
            'next_page_button_location_value': '',
            # Pastas.
            'download_dir': str(Path(r'{}\Downloads'.format(system_ma.user_dir))),
            'files_dir': str(Path(r'{}\files'.format(os.getcwd()))),
            'final_dir': '',
            # Arquivo de configuração
            'config_file': str(Path(r'{}\Config.txt'.format(os.getcwd())))
        }

        # Carrega configurações.
        self.load_configs()

    def load_configs(self):
        """
            Carrega configurações.
        """
        try:
            # Carrega informações do arquivo de configurações.
            config_txt = open(self.config_list['config_file'], 'r')
            config_lines = config_txt.readlines()
            config_txt.close()
            config_lines = [line.replace('\n', '') for line in config_lines]

            # Atribui valores.
            for config_key in self.config_list.keys():
                for line in config_lines:
                    if line.startswith('{}='.format(config_key)):
                        self.config_list[config_key] = line[line.index('=')+1:]
                        break
        except FileNotFoundError:
            self.save_configs()

    def save_configs(self):
        """
            Salva configurações.
        """
        with open(self.config_list['config_file'], 'w') as config_txt:
            for config_key, config in self.config_list.items():
                config_txt.write('{}={}\n'.format(config_key, config))

    def edit_config(self, config_name, value):
        """
            :param config_name: (String) Nome da configuração.
            :param value: (String) Configuração.
            Edita valor da variável na instância.
        """
        self.config_list[config_name] = value
