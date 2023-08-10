import time
from pathlib import Path
import pyautogui
import pyperclip
from TimeControl import TimeControl


class ScreenManipulator:
    def __init__(self, img_dir, pause):
        """
            :param img_dir: (String) Caminho para a pasta de imagens usadas no reconhecimento da tela.
            :param pause: (Float) Pausa entre os comandos em segundos.
        """
        self.img_dir = img_dir
        self.set_pause(pause)

    def locate(self, img_name, region=(), confidence=0.7):
        """
            :param img_name: (String) Nome da imagem.
            :param region: (Tuple) Tupla com as coordenadas do ponto superior esquerdo e o inferior direito da área.
            :param confidence: (Float) Nivel de exatidão exigido, sendo o máximo 1.
            :return: (Tuple) Tupla com coordenadas do centro da imagem.
        """
        # Monta o caminho da imagem.
        img_location = str(Path(r'{}\{}'.format(self.img_dir, img_name)))
        if region:
            # Converte as coordenadas da região para o pyautogui entender.
            region = self.parse_coords_to_region(region)

            # Pesquisa nas coordenadas passadas.
            return pyautogui.locateCenterOnScreen(img_location, confidence=confidence, region=region)
        else:
            # Pesquisa na tela inteira.
            return pyautogui.locateCenterOnScreen(img_location, confidence=confidence)

    def wait_for(self, time_out, img_names, how_many='all', region=(), confidence=None):
        """
            :param time_out: (Float) Tempo Limite em segundos.
            :param img_names: (Array) Nome das imagens a serem esperadas.
            :param how_many: (String) Sendo 'all' para esperar por todas ou 'one' para esperar apenas uma aparecer.
            :param region: (Tuple) Tupla com as coordenadas do ponto superior esquerdo e o inferior direito da área.
            :param confidence: (Float) Nivel de exatidão exigido, sendo o máximo 1.
            :return: (String) Mensagem de erro se necessário senão vazio.
        """
        loading = True
        status_msg = ''
        time_control = TimeControl()
        time_control.start()
        while loading:
            for img_name in img_names:
                if not self.locate(img_name, region=region, confidence=confidence):
                    loading = True
                    if time_control.time_is_up(time_out):
                        status_msg = f'Tempo excedido esperando por {img_name}'
                        loading = False
                    if how_many == 'all':
                        break
                else:
                    loading = False
                    if how_many == 'one':
                        break
        time_control.end()
        return status_msg

    def wait_until_become_invisible(self, time_out, img_names, how_many='all', region=(), confidence=None):
        """
            :param time_out: (Float) Tempo Limite em segundos.
            :param img_names: (Array) Nome das imagens a serem esperadas.
            :param how_many: (String) Sendo 'all' para esperar por todas ou 'one' para esperar apenas uma desaparecer.
            :param region: (Tuple) Tupla com as coordenadas do ponto superior esquerdo e o inferior direito da área.
            :param confidence: (Float) Nivel de exatidão exigido, sendo o máximo 1.
            :return: (String) Mensagem de erro se necessário senão vazio.
        """
        time_control = TimeControl()
        time_control.start()
        invisible = True
        waiting = True
        status_msg = ''

        while waiting:
            for img_name in img_names:
                if self.locate(img_name, region=region, confidence=confidence):
                    invisible = False
                    if time_control.time_is_up(time_out):
                        waiting = False
                        status_msg = f'Tempo excedido esperando sumir: {img_names[0]}'
                    elif how_many == 'all':
                        break
                else:
                    invisible = True
                    if how_many == 'one':
                        break
            if invisible:
                waiting = False
        time_control.end()
        return status_msg

    @staticmethod
    def parse_coords_to_region(coords):
        """
            :param coords: (Tuple) Tupla com as coordenadas do ponto superior esquerdo e o inferior direito da área.
            :return: (Tuple) Tupla com as coordenadas do ponto superior esquerdo, largura e altura da área.
        """
        coords_copy = [value for value in coords]
        revised_coordinates = []
        for value in coords_copy:
            if value < 0:
                revised_coordinates.append(0)
            else:
                revised_coordinates.append(value)

        x_init, y_init, x_end, y_end = revised_coordinates
        width = x_end - x_init
        height = y_end - y_init
        return x_init, y_init, width, height

    @staticmethod
    def set_pause(pause):
        """
            :param pause: (Float) Pausa entre os comandos em segundos.
             Atribuí o tempo de pausa entre os comandos do pyautogui.
        """
        pyautogui.PAUSE = pause

    @staticmethod
    def move_in_explorer(dir):
        """
            :param dir: (String) Caminho para uma pasta.
            Pesquisa no explorador de arquivos pela pasta.
        """
        pyperclip.copy(dir)
        pyautogui.hotkey('alt', 'd')
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')

    @staticmethod
    def click(coords, button='left', clicks=1):
        """
            :param coords: (Tuple) Tupla com as coordenadas do ponto a ser clicado.
            :param button: (String) Sendo 'left' para esquerdo ou 'right' para o clique com o botão direito do mouse.
            :param clicks: (Int) Quantidade de cliques.
            Clica nas coordenadas passadas.
        """
        pyautogui.click(coords, button=button, clicks=clicks)

    @staticmethod
    def press_keys(keys):
        """
            :param keys: (Array) Lista com teclas a serem pressionadas.
        """
        for key in keys:
            pyautogui.press(key)

    # TODO: EXCLUIR.
    @staticmethod
    def open_anonimous_tab():
        pyautogui.hotkey('ctrl', 'shift', 'n')

    @staticmethod
    def select_all():
        """
            Aciona o atalho Ctrl+A para seleção de tudo.
        """
        pyautogui.hotkey('ctrl', 'a')

    @staticmethod
    def delete():
        """
            Pressiona a tecla del para deletar.
        """
        pyautogui.press('del')

    @staticmethod
    def copy():
        """
            Aciona o atalho Ctrl+C para copiar.
        """
        pyautogui.hotkey('ctrl', 'c')

    def paste_and_confirm(self, text):
        """
            :param text: (String) Texto a ser colado.
            Copia o texto, cola e confirma.
        """
        pyperclip.copy(text)
        self.paste()
        self.confirm()

    @staticmethod
    def confirm():
        """
            Pressiona a tecla Enter para confirmar.
        """
        pyautogui.press('enter')

    @staticmethod
    def paste():
        """
            Aciona o atalho Ctrl+V para colar.
        """
        pyautogui.hotkey('ctrl', 'v')

    @staticmethod
    def drag(init_coords, end_coords):
        """
            :param init_coords: (Tuple) Tupla com as coordenadas do ponto inicial a ser clicado.
            :param end_coords: (Tuple) Tupla com as coordenadas do ponto final para onde o mouse será arrastado.
            Clica e arrasta.
        """
        pyautogui.mouseDown(init_coords)
        x, y = end_coords
        pyautogui.moveTo(x, y, 0.3)
        time.sleep(0.2)
        pyautogui.mouseUp()

    @staticmethod
    def close_window():
        """
            Aciona o atalho Alt+F4 para fechar janela.
        """
        pyautogui.hotkey('alt', 'f4')

    def close_windows_by_coords(self, windows_coords):
        """
            :param windows_coords: (Array) Lista com tuplas das coordenadas das janelas.
            Clica nas coordenas informadas e fecha elas.
        """
        for coords in windows_coords:
            self.click(coords)
            time.sleep(0.10)
            self.close_window()
