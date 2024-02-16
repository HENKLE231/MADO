from pathlib import Path
import os
from win32api import GetSystemMetrics
import win32gui
import win32com.client as com_cli
from TextManager import TextManager


class SystemManager:
    def __init__(self):
        self.screen_x = GetSystemMetrics(0)
        self.screen_y = GetSystemMetrics(1)
        self.cwd = os.getcwd()
        self.user_dir = self.cwd[:self.cwd.index(r'\ '.strip(), self.cwd.index('Users')+6)]

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

    @staticmethod
    def get_current_window_handle():
        """
            :return: (Int) Identificador da janela.
        """
        return win32gui.GetForegroundWindow()

    @staticmethod
    def close_window(handle):
        """
            :param handle: (Int) Identificador da janela.
            Fecha a janela.
        """
        # Pega nome da janela.
        window_name = win32gui.GetWindowText(handle)

        # Verifica existencia da janela.
        if window_name:
            # Carrega Shell.
            wsh = com_cli.Dispatch('WScript.Shell')
            # Seleciona.
            wsh.AppActivate(window_name)
            # Envia o comando Alt+F4.
            wsh.SendKeys('%{F4}')
