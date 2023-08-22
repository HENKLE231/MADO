from win32api import GetSystemMetrics
from TextManager import TextManager
from pathlib import Path
import signal
import os


class SystemManager:
    def __init__(self):
        self.screen_x = GetSystemMetrics(0)
        self.screen_y = GetSystemMetrics(1)
        self.cwd = os.getcwd()
        self.user_dir = self.cwd[:self.cwd.index(r'\ '.strip(), self.cwd.index('Users')+6)]

    @staticmethod
    def end_process(pid):
        """
            :param pid: (Int) Identificador do processo (PID).
            Encerra o Processo.
        """
        os.kill(pid, signal.SIGTERM)

    @staticmethod
    def get_current_process_id():
        """
            :return pid: (Int) identificador do processo (PID).
            Pega o identificador do processo atual.
        """
        return os.getpid()

    @staticmethod
    def find_files(path, patterns, to_meet=1):
        """
            :param path: (String) Caminho de uma pasta.
            :param patterns: (Array de Strings) Padrões.
            :param to_meet: (Int) Quantidade de padrões necessários no mesmo arquivo.
            :return: (Array de Strings) Caminhos dos arquivos.
        """
        files_paths = []
        files = os.listdir(path)
        # Varre arquivos procurando por padrões.
        for file in files:
            # Verifica se atende aos padrões.
            if TextManager.find_patterns(file, patterns, to_meet):
                # Salva caminho.
                files_paths.append(str(Path(r'{}\{}'.format(path, file))))
        return files_paths

    @staticmethod
    def delete(paths):
        """
            :param paths: (Array de Strings) Caminhos para pastas ou arquivos.
            Exclui pastas e arquivos.
        """
        # Varre caminhos.
        for path in paths:
            # Verifica exixtência.
            if os.path.exists(path):
                # Excluí.
                os.remove(path)

    @staticmethod
    def move_files(files, new_dir):
        """
            :param files: (Array de Strings) Caminhos dos arquivos.
            :param new_dir: (String) Caminho da pasta de destino.
            Move arquivos para pasta desejada.
        """
        # Varre arquivos.
        for file in files:
            file_name = TextManager.get_last_piece_of_path(file)
            new_file_location = str(Path(r'{}/{}'.format(new_dir, file_name)))
            # Transfere.
            os.rename(file, new_file_location)

    @staticmethod
    def path_exist(path):
        """
            :param path: (String) Caminho para uma pasta.
            :return: (Boolean) True se pasta existe.
        """
        return os.path.exists(path)

    @staticmethod
    def count_files(path, patterns, to_meet=1):
        """
            :param path: (String) Caminho de uma pasta.
            :param patterns: (Array de Strings) Padrões.
            :param to_meet: (Int) Quantidade de padrões necessários no mesmo arquivo.
            :return: (Int) Quantidade de arquivos no padrão.
        """
        num_files = 0
        files = os.listdir(path)

        # Varre arquivos procurando por padrões.
        for file in files:
            # Verifica se atende aos padrões.
            if TextManager.find_patterns(file, patterns, to_meet):
                # Incrementa numero de arquivos.
                num_files += 1
        return num_files
