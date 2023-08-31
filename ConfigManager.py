from SystemManager import SystemManager as SystemMa
from pathlib import Path
import os


class ConfigManager:
    def __init__(self, config_set_name=None):
        """
            :param config_set_name: (String) Nome do conjunto de configurações.
        """
        # Instancia classe necessária.
        system_ma = SystemMa()

        self.config_set_name = config_set_name

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
            'files_dir': str(Path(r'{}\files'.format(system_ma.cwd))),
            'final_dir': '',
            # Arquivo de configuração
            'config_file': str(Path(r'{}\Config.txt'.format(system_ma.cwd)))
        }

        # Carrega configurações.
        if config_set_name:
            self.load_configs()

    def edit_config(self, config_name, value):
        """
            :param config_name: (String) Nome da variável.
            :param value: (String) Valor da variável.
            Edita variável de instancia.
        """
        if config_name in self.config_list.keys():
            self.config_list[config_name] = value
        else:
            raise Exception('Configuração inexistente.')

    def load_configs(self, config_set_name=None):
        """
            :param config_set_name: (String) Nome do conjunto de configurações.
            Carrega configurações.
        """
        if config_set_name:
            self.config_set_name = config_set_name

        try:
            # Carrega informações do arquivo de configurações.
            config_lines = self.get_config_lines()

            # Verifica existência do cunjunto de configurações.
            if not self.config_set_exist(self.config_set_name):
                # Cria um conjunto de configuração.
                self.add_config_set()

                # Carrega linhas novamente.
                config_lines = self.get_config_lines()

            # Procura conjunto de configuração.
            initial_index, final_index = self.find_config_set(self.config_set_name, config_lines)

            # Seleciona linhas do conjunto escolhido.
            config_set_lines = config_lines[(initial_index + 1):final_index]

            # Carrega informações para a instância.
            for config_key in self.config_list.keys():
                for line in config_set_lines:
                    if line.startswith('{}='.format(config_key)):
                        self.config_list[config_key] = line[line.index('=')+1:]
                        break

            self.save_last_config_set_loaded(self.config_set_name)

        except FileNotFoundError:
            # Cria um conjunto de configuração.
            self.add_config_set()

    def add_config_set(self):
        """
            Adiciona configurações atuais como novo conjunto de configurações.
        """
        config_lines = []
        try:
            # Carrega informações do arquivo de configurações.
            config_lines = self.get_config_lines()
        except FileNotFoundError:
            pass

        if self.config_set_exist(self.config_set_name):
            raise Exception('Conjunto de configurações já existente.')

        # Adiciona informações anteriormente contidas.
        lines_to_write = config_lines

        # Adiciona tag de abertura.
        lines_to_write.append('<{}'.format(self.config_set_name))

        # Adiciona informações atuais.
        for config_key, value in self.config_list.items():
            lines_to_write.append('{}={}'.format(config_key, value))

        # Adiciona tag de fechamento.
        lines_to_write.append('/>')

        # Atribui configuração se ainda não existente.
        lines = []
        if not lines_to_write[0].startswith('last_config_set_loaded='):
            lines.append('last_config_set_loaded=')
        lines.extend(lines_to_write)

        # Escreve no arquivo de configurações.
        self.write_in_config_file(lines)

    def save_config_set(self):
        """
            Edita o atual conjunto de configurações.
        """
        lines_to_write = []
        try:
            # Carrega informações do arquivo de configurações.
            config_lines = self.get_config_lines()

            if not self.config_set_exist(self.config_set_name):
                raise Exception('Conjunto de configurações inexistente.')

            # Procura conjunto de configuração.
            initial_index, final_index = self.find_config_set(self.config_set_name, config_lines)

            for i, line in enumerate(config_lines):
                # Adiciona configurações anteriores.
                if i < initial_index:
                    lines_to_write.append(line)
                # Adiciona nome do conjunto de configuração atual.
                elif i == initial_index:
                    lines_to_write.append('<{}'.format(self.config_set_name))
                # Adiciona configurações atuais.
                elif i < final_index:
                    for config_key, config in self.config_list.items():
                        lines_to_write.append('{}={}\n'.format(config_key, config))
                # Fecha conjunto de configurações.
                elif i == final_index:
                    lines_to_write.append('/>')
                # Adiciona configurações posteriores.
                else:
                    lines_to_write.append(line)

            # Escreve no arquivo.
            self.write_in_config_file(lines_to_write)

        except FileNotFoundError:
            raise FileNotFoundError('Arquivo de configurações não encontrado.')

    def rename_config_set(self, new_name, current_name=None):
        """
            :param new_name: (String) Novo nome.
            :param current_name: (String) Atual nome do conjunto de configurações.
            Renomeio conjunto de configurações.
        """
        if not current_name:
            current_name = self.config_set_name

        lines_to_write = []
        try:
            # Carrega informações do arquivo de configurações.
            config_lines = self.get_config_lines()

            if not self.config_set_exist(self.config_set_name):
                raise Exception('Conjunto de configurações inexistente.')

            # Procura conjunto de configuração.
            initial_index, final_index = self.find_config_set(current_name, config_lines)

            # Copia configurações, alterando apenas o nome do cunjunto.
            lines_to_write = config_lines
            lines_to_write[initial_index] = '<{}'.format(new_name)

            # Escreve no arquivo de configurações.
            self.write_in_config_file(lines_to_write)

        except FileNotFoundError:
            raise FileNotFoundError('Arquivo de configurações não encontrado.')

    def delete_config_set(self, config_set_name=None):
        """
            :param config_set_name: (String) Nome do conjunto de configurações.
            Deleta conjunto de configurações.
        """
        if not config_set_name:
            config_set_name = self.config_set_name

        lines_to_write = []
        try:
            # Carrega informações do arquivo de configurações.
            config_lines = self.get_config_lines()

            if not self.config_set_exist(self.config_set_name):
                raise Exception('Conjunto de configurações inexistente.')

            # Procura conjunto de configuração.
            initial_index, final_index = self.find_config_set(config_set_name, config_lines)

            # Seleciona todas linhas menos o conjunto atual.
            lines_to_write = config_lines[:initial_index]
            lines_to_write.extend(config_lines[(final_index + 1):])

            # Escreve no arquivo.
            self.write_in_config_file(lines_to_write)

        except FileNotFoundError:
            raise FileNotFoundError('Arquivo de configurações não encontrado.')

    def get_config_lines(self):
        """
            :return: (Array de Strings) Linhas de configurações.
            Carrega informações do arquivo de configurações.
        """
        try:
            config_txt = open(self.config_list['config_file'], 'r')
            config_lines = config_txt.readlines()
            config_txt.close()
            # Retira quebra de linhas.
            config_lines = [line[:-2] for line in config_lines]
            return config_lines
        except FileNotFoundError:
            raise FileNotFoundError('Arquivo de configurações não encontrado.')

    def write_in_config_file(self, lines):
        """
            :param lines: (Array de Strings) Linhas que serão escritas.
            Escreve no arquivo de configurações.
        """
        # Abre o arquivo e escreve.
        with open(self.config_list['config_file'], 'w') as config_txt:
            for line in lines:
                # Escreve e adiciona quebra de linha.
                config_txt.write('{}\n'.format(line))

    def config_set_exist(self, config_set_name):
        """
            :return: (Boolean) Se o Conjunto de configurações existe.
        """
        config_lines = self.get_config_lines()
        existing_names = [line[1:] for line in config_lines if line.startswith('<')]
        return config_set_name in existing_names

    @staticmethod
    def find_config_set(config_set_name, config_lines):
        """
            :param config_set_name: (String) Nome do conjunto de configurações.
            :param config_lines: (Array de Strings) Linhas de configuração.
            :return: (Tupla de 2 Ints) Índice inicial e final do conjunto de configurações.
        """
        initial_index_found = False
        initial_index = 0
        final_index = 0
        for i, line in enumerate(config_lines):
            if not initial_index_found:
                # Procura tag de abertura
                if line.startswith('<{}'.format(config_set_name)):
                    initial_index = i
                    initial_index_found = True
            else:
                # Procura tag de fechamento.
                if line.startswith('/>'):
                    final_index = i
                    break
        return initial_index, final_index

    def save_last_config_set_loaded(self, config_set_name):
        """
            :config_set_name: (String) Nome do conjunto de configuração.
            Salva o nome do último conjunto de configurações carregado.
        """
        try:
            config_lines = self.get_config_lines()

            # Atribui configuração se ainda não existente.
            lines = []
            if not config_lines[0].startswith('last_config_set_loaded='):
                lines.append('last_config_set_loaded={}'.format(config_set_name))
            lines.extend(config_lines)

            # Salva.
            self.write_in_config_file(lines)

        except FileNotFoundError:
            raise FileNotFoundError('Arquivo de configurações não encontrado.')

    def get_last_config_set_loaded(self):
        """
            :config_set_name: (String) Nome do conjunto de configuração.
            :return: (String) Nome do último conjunto de configurações carregado.
        """
        try:
            config_lines = self.get_config_lines()

            # Pega primeira linha.
            first_line = config_lines[0]
            if first_line.startswith('last_config_set_loaded='):
                return first_line[(first_line.index('=') + 1):]
            else:
                raise Exception('Configuração last_config_set_loaded não encontrada.')
        except FileNotFoundError:
            raise FileNotFoundError('Arquivo de configurações não encontrado.')

