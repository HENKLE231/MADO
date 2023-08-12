import win32gui
import win32con
import win32com.client as com_cli
from win32api import GetSystemMetrics
from win32api import GetMonitorInfo, MonitorFromPoint
from TimeControl import TimeControl
from pathlib import Path
import shutil
import signal
import os


class SystemManipulator:
    def __init__(self):
        self.point_x_zero = -7
        self.point_y_zero = 0
        self.screen_x = GetSystemMetrics(0) - self.point_x_zero
        self.screen_y = GetSystemMetrics(1)
        self.work_area_x, self.work_area_y = GetMonitorInfo(MonitorFromPoint((0, 0))).get('Work')[-2:]
        self.work_area_x = self.screen_x
        self.work_area_y = self.work_area_y + self.point_x_zero * -1
        self.window_states = {
            'maximized': win32con.SW_SHOWMAXIMIZED,
            'minimized': win32con.SW_SHOWMINIMIZED,
            'showna': win32con.SW_SHOWNA,
            'normal': win32con.SW_SHOWNORMAL,
            'show': win32con.SW_SHOW
        }
        self.cwd = os.getcwd()
        self.user_dir = self.cwd[:self.cwd.index(r'\ '.strip(), self.cwd.index('Users')+6)]

    @staticmethod
    def end_process(target='current', pid=0):
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

    def get_window(self, window_name=''):
        """
            :param window_name: (String) Nome da janela.
            :return: (Int) Identificador da janela.
        """
        if not window_name:
            window_name = self.get_window_name()
        return win32gui.FindWindow(None, window_name)

    def get_window_state(self, window=0):
        """
            :param window: (Int) Identificador da janela.
            :return: (String) Estado da janela
        """
        if not window:
            window = self.get_window()
        placement = win32gui.GetWindowPlacement(window)[1]
        for key in self.window_states.keys():
            if self.window_states[key] == placement:
                return key

    def set_window_state(self, new_state, window=0):
        """
            :param new_state: (String) Novo estado da janela: 'maximized', 'minimized', 'showna', 'normal' ou 'show'.
            :param window: (Int) Identificador da janela.
            Muda o estado da janela.
        """
        if not window:
            window = win32gui.FindWindow(None, self.get_window_name())
        placements = win32gui.GetWindowPlacement(window)
        new_placement = (placements[0], self.window_states[new_state], placements[2], placements[3], placements[4])
        win32gui.SetWindowPlacement(window, new_placement)

    @staticmethod
    def get_window_position(window):
        """
            :param window: (Int) Identificador da janela.
            :return: (Tuple) Tupla com as coordenadas do ponto superior esquerdo da janela.
        """
        window_position = win32gui.GetWindowPlacement(window)[4]
        return window_position[0], window_position[1]

    def set_window_position(self, window, size_and_position):
        """
            :param window: (Int) Identificador da janela.
            :param size_and_position: (Tuple) Tupla com as coordenadas do ponto superior esquerdo e inferior direito da janela.
            Muda a posição da janela.
        """
        placements = win32gui.GetWindowPlacement(window)
        new_placement = (placements[0], self.window_states['normal'], placements[2], placements[3], size_and_position)
        win32gui.SetWindowPlacement(window, new_placement)

    def set_window_position_by_initial_point(self, window, initial_point):
        """
            :param window: (Int) Identificador da janela.
            :param initial_point: (Tuple) Tupla com as coordenadas onde se posicionará o canto superior esquerdo da janela.
            Posiciona janela conforme o ponto inicial.
        """
        # Verifica a dimensão e localização atual da janela.
        placements = win32gui.GetWindowPlacement(window)
        current_x_init, current_y_init, current_x_end, current_y_end = placements[4]
        x_init, y_init = initial_point
        x_end = (current_x_end - current_x_init) + x_init
        y_end = (current_y_end - current_y_init) + y_init
        size_and_position = (x_init, y_init, x_end, y_end)
        new_placement = (placements[0], self.window_states['normal'], placements[2], placements[3], size_and_position)

        # Move janela.
        win32gui.SetWindowPlacement(window, new_placement)

    def get_half_screen_coords(self, side='left'):
        """
            :param side: (String) Lado da tela, sendo: 'left' para esquerdo ou 'right' para direito.
            :return: (Array) Lista com coordenadas do canto superior esquerdo e inferior direito de metade da tela.
        """
        x_init, y_init, x_end, y_end = [0, 0, 0, 0]
        if side == 'left':
            x_init = self.point_x_zero
            y_init = self.point_y_zero
            x_end = int(self.screen_x / 2) + (self.point_x_zero * -1)
            y_end = self.work_area_y
        elif side == 'right':
            x_init = int(self.screen_x / 2) - (self.point_x_zero * -1)
            y_init = self.point_y_zero
            x_end = self.screen_x
            y_end = self.work_area_y
        return x_init, y_init, x_end, y_end

    @staticmethod
    def get_middle_of_window(coords):
        """
            :param coords: (Array) Lista com coordenadas do canto superior esquerdo e inferior direito da janela.
            :return: (Tuple) Tupla com coordenadas do meio da área informada.
        """
        x_init, y_init, x_end, y_end = coords
        half_width = (x_end - x_init) / 2
        half_height = (y_end - y_init) / 2
        x = x_init + half_width
        y = y_init + half_height
        return x, y

    def wait_until_open(self, time_out, window_name):
        """
            :param time_out: (Float) Tempo limite de espera em segundos.
            :param window_name: (String) Nome da janela.
            :return: Mensagem de erro se necessário denão vazio
            Espera até janela estar aberta.
        """
        time_control = TimeControl()
        time_control.start()
        status_msg = ''
        window_open = False
        loading = True
        while loading:
            # Pega o identificador da janela.
            window = self.get_window(window_name)
            if window:
                # Pega estado inicial.
                initial_state = self.get_window_state(window)

                # Define outro estado.
                if initial_state != 'minimized':
                    other_state = 'minimized'
                else:
                    other_state = 'normal'

                # Espera ser possivel mudar o estado.
                while not window_open:
                    # Tenta atribuir outro estado
                    self.set_window_state(other_state, window)
                    if self.get_window_state(window) != initial_state:
                        # Devolve estado inicial.
                        self.set_window_state(initial_state, window)
                        window_open = True
                        loading = False
                    elif time_control.time_is_up(time_out):
                        loading = False
                        status_msg = f'Tempo excedido esperando {window_name} abrir.'
                        break
            elif time_control.time_is_up(time_out):
                status_msg = f'Tempo excedido esperando {window_name} abrir.'
                break
        return status_msg

    @staticmethod
    def get_fold_name(path):
        """
            :param path: (String) Caminho completo para a pasta.
            :return: (String) Nome da pasta no final do caminho.
        """
        seps = [r'\ '.strip(), '/']
        for sep in seps:
            if sep in path:
                return path.split(sep)[-1]

    def close_windows(self, windows_to_close):
        """
            :param windows_to_close: (Array) Lista com os nomes das janelas.
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
    def get_window_name():
        """
            :return: (String) Nome da janela com o foco atual.
        """
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())

    @staticmethod
    def get_window_name_by_window(window):
        """
            :param window: (Int) Identificador da janela.
            :return: (String) Nome da janela.
        """
        return win32gui.GetWindowText(window)

    @staticmethod
    def open_app(exe_name):
        """
            :param exe_name: (String) Nome do executável.
            Inicia o executável por comando DOS.
        """
        os.system(r'start {}'.format(exe_name))

    @staticmethod
    def open_explorer(path=''):
        """
            :param path: (String) Caminho para a pasta do computador a ser aberta.
            Abre o explorador de arquivos na pasta desejada.
        """
        if path:
            system_command = f'explorer.exe /e, /n, "{path}"'
        else:
            system_command = 'explorer.exe'
        os.system(system_command)

    @staticmethod
    def clear_dirs(dirs):
        """
            :param dirs: (Array) Lista com os caminhos das pastas.
            Limpa pastas.
        """
        for path in dirs:
            files = os.listdir(path)
            for file in files:
                os.remove(str(Path(r'{}/{}'.format(path, file))))

    @staticmethod
    def delete_files(path, patterns):
        """
            :param path: (String) Caminho para a pasta.
            :param patterns: (Array) Lista de padrões encontrados nos nomes dos arquivos.
            Exclui os arquivos da pasta que possuem algum dos padrões.
        """
        files = os.listdir(path)
        for file in files:
            for pattern in patterns:
                if pattern in file:
                    os.remove(str(Path(r'{}/{}'.format(path, file))))
                    break

    @staticmethod
    def delete_config_txt():
        """
            Deleta o arquivo de configurações.
        """
        config_path = r'{}\Config.txt'.format(os.getcwd())
        if os.path.exists(config_path):
            os.remove(str(Path(config_path)))

    @staticmethod
    def move_files(current_dir, new_dir, pattern=''):
        """
            :param current_dir: (String) Caminho da pasta atual do arquivo.
            :param new_dir: (String) Caminho da pasta para onde o arquivo será transferido.
            :param pattern: (String) Padrão encontrado nos nomes dos arquivos a serem movidos.
            Move arquivos.
        """
        files = os.listdir(current_dir)
        for file in files:
            if pattern in file:
                file_location = str(Path(r'{}/{}'.format(current_dir, file)))
                new_file_location = str(Path(r'{}/{}'.format(new_dir, file)))
                os.rename(file_location, new_file_location)

    @staticmethod
    def file_with_pattern_exists(path, pattern=''):
        """
            :param path: (String) Caminho da pasta do arquivo.
            :param pattern: (String) Padrão encontrado no nome do arquivo.
            :return: (Boolean) True se o arquivo existe.
        """
        files = os.listdir(path)
        for file in files:
            if pattern in file:
                return True
        return False

    @staticmethod
    def path_exist(path):
        """
            :param path: (String) Caminho para uma pasta.
            :return: (Boolean) True se pasta existe.
        """
        return os.path.exists(path)

    @staticmethod
    def how_many_files(path, pattern=''):
        """
            :param path: (String) Caminho de uma pasta.
            :param pattern: (String) Padrão procurado.
            :return: (Int) Quantidade de arquivos com o padrão na pasta.
        """
        files = os.listdir(path)
        number_of_matching_files = 0
        for file in files:
            if pattern in file:
                number_of_matching_files += 1
        return number_of_matching_files

    @staticmethod
    def copy_files(current_dir, new_dir='', pattern=''):
        """
            :param current_dir: (String) Caminho para a pasta atual.
            :param new_dir: (String) Caminho para a pasta para onde serão copiados os arquivos.
            :param pattern: (String) Padrão encontrado nos arquivos que serão transferidos.
            Copia arquivos.
        """
        if not new_dir:
            new_dir = current_dir
        files = os.listdir(current_dir)
        for file in files:
            if pattern in file:
                file_location = str(Path(r'{}/{}'.format(current_dir, file)))
                new_file_location = str(Path(r'{}/'.format(new_dir)))
                shutil.copy2(file_location, new_file_location)
