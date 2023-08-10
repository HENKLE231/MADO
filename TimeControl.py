from InternetSpeed import InternetSpeed
from pathlib import Path
import time
import os


class TimeControl:
    def __init__(self):
        self.start_times = []

    def start(self):
        """
            Adiciona na instância o horário de início da função.
        """
        self.start_times.append(time.time())

    def end(self):
        """
            Remove da instância o horário de início da última função.
        """
        self.start_times.pop()

    def time_is_up(self, timeout):
        """
            :param timeout: (Float) Tempo limite em segundos.
            :return: (Boolean) Verdadeiro se o tempo limite foi alcançado.
        """
        time_is_up = False
        current_time = time.time()
        if current_time - self.start_times[-1] >= timeout:
            time_is_up = True
        return time_is_up

    def get_transfer_timeout(
            self, transfer_type, info, info_type='file', average_size='0B', tolerance_percentage=30
    ):
        """
            :param transfer_type: (String) Tipo de transferência sendo 'download' ou 'upload'.
            :param info: (String ou Int) Caminho de arquivo, de pasta ou quantidade de arquivos.
            :param info_type: (String) Tipo de informação passada sendo 'file', 'dir' ou 'unit'.
            :param average_size: (String) Tamanho médio e unidade de medida sem espaço. As unidades
            de medida sendo 'B', 'kB', 'MB' ou 'GB'.
            :param tolerance_percentage: (Int) Porcentagem de tolerância.
            :return: (Int) Tempo limite de transferência, sendo a soma da estimativa com a tolerância.
        """
        measuring_unit = 'B'
        total_size = 0

        if info_type == 'file':
            total_size = os.path.getsize(info)
        elif info_type == 'dir':
            files = os.listdir(info)
            for file in files:
                file_path = str(Path(r'{}\{}'.format(info, file)))
                total_size += os.path.getsize(file_path)
        elif info_type == 'unit' and average_size:
            average_size, measuring_unit = self.identify_size_and_measuring_unit(average_size)
            total_size = info * average_size

        # Converte o tamanho total para MB
        total_size = self.parse_to_MB(total_size, measuring_unit)

        # Verifica velocidade da transferêncaia
        if transfer_type == 'download':
            transfer_speed = InternetSpeed.get_download_speed()
        elif transfer_type == 'upload':
            transfer_speed = InternetSpeed.get_upload_speed()

        # Calcula o tempo limite de transferência
        transfer_estimate = total_size / transfer_speed
        transfer_timeout = round(transfer_estimate + (transfer_estimate / 100 * tolerance_percentage))
        if transfer_timeout < 10:
            transfer_timeout = 10
        return transfer_timeout

    @staticmethod
    def identify_size_and_measuring_unit(average_size_text):
        """
            :param average_size_text: (String) Tamanho do arquivo e a unidade de medida, sem espaços.
            :return: (Tuple) Tupla contendo o tamanho convertido em float e a unidade de medida.
        """
        divider = 0
        i = len(average_size_text) - 1
        while i <= 0:
            if average_size_text[i].isnumeric():
                divider = i + 1
                break
            i -= 1
        size = float(average_size_text[:divider])
        measuring_unit = average_size_text[divider:]
        return size, measuring_unit

    @staticmethod
    def parse_to_MB(size, measuring_unit):
        """
            :param size: (Int ou Float) Tamanho do arquivo.
            :param measuring_unit: (String) Unidade de medida sendo 'B', 'kB', 'MB' ou 'GB'.
            :return: (Int ou Float) Tamanho convertido para MB.
        """
        if measuring_unit == 'B':
            size /= 1048576
        elif measuring_unit == 'kB':
            size /= 1024
        elif measuring_unit == 'MB':
            pass
        elif measuring_unit == 'GB':
            size *= 1024
        return size
