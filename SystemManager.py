import win32gui
import win32com.client as com_cli
from win32api import GetSystemMetrics
from TextFormatter import TextFormatter
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
    def get_window_name():
        """
            :return: (String) Nome da janela com o foco atual.
        """
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())

    def get_window(self, window_name=''):
        """
            :param window_name: (String) Nome da janela.
            :return: (Int) Identificador da janela.
        """
        if not window_name:
            window_name = self.get_window_name()
        return win32gui.FindWindow(None, window_name)

    def close_windows(self, windows_to_close):
        """
            :param windows_to_close: (Array de Strings) Lista com os nomes das janelas.
            Fecha janelas com os nomes passados.
        """
        for window_name in windows_to_close:
            if self.get_window(window_name) != 0:
                wsh = com_cli.Dispatch('WScript.Shell')

                # Seleciona a janela.
                wsh.AppActivate(window_name)

                # Envia o atalho Alt+F4 para a janela.
                wsh.SendKeys('%{F4}')

    @staticmethod
    def end_process(target='pid', pid=0):
        """
            :param target: (String) Sendo 'current' para processo atual ou
            'pid' se informar o identificador do processo.
            :param pid: (Int) identificador do processo (PID).
            Encerra o Processo.
        """
        if target == 'current':
            os.kill(os.getpid(), signal.SIGTERM)
        elif target == 'pid' and pid:
            os.kill(pid, signal.SIGTERM)

    @staticmethod
    def get_current_process_id():
        """
            :return pid: (Int) identificador do processo (PID).
            Pega o identificador do processo atual.
        """
        return os.getpid()

    @staticmethod
    def find_files(dir_path, patterns, to_meet=1):
        """
            :param dir_path: (String) Caminho de uma pasta.
            :param patterns: (Array de Strings) Padrões.
            :param to_meet: (Int) Quantidade de padrões necessários no mesmo arquivo.
            :return: (Array de Strings) Caminhos dos arquivos.
        """
        files_paths = []
        files = os.listdir(dir_path)
        pattern_match = 0
        # Varre arquivos procurando por padrões.
        for file in files:
            for pattern in patterns:
                if pattern in file:
                    pattern_match += 1
            if pattern_match >= to_meet:
                files_paths.append(str(Path(r'{}\{}'.format(dir_path, file))))
            pattern_match = 0
        return files_paths

    @staticmethod
    def delete(paths):
        """
            :param paths: (Array de Strings) Caminhos para pastas ou arquivos.
            Exclui pastas e arquivos.
        """
        # Deleta
        for path in paths:
            path = str(Path(path))
            if os.path.exists(path):
                os.remove(path)

    @staticmethod
    def move_files(files, new_dir):
        """
            :param files: (Array de Strings) Caminhos dos arquivos.
            :param new_dir: (String) Caminho da pasta para onde os arquivo será transferido.
            Move arquivos para pasta desejada.
        """
        for file in files:
            file_name = TextFormatter.get_last_piece_of_path(file)
            new_file_location = str(Path(r'{}/{}'.format(new_dir, file_name)))
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
        files = os.listdir(path)
        num_files = 0
        pattern_match = 0
        # Varre arquivos procurando por padrões.
        for file in files:
            for pattern in patterns:
                if pattern in file:
                    pattern_match += 1
            if pattern_match >= to_meet:
                num_files += 1
            pattern_match = 0
        return num_files
