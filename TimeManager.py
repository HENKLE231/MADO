from InternetTester import InternetTester
import time


class TimeManager:
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

    def get_download_time_estimate(
            self, amount, average_size='0', measuring_unit='B', tolerance_percentage=30
    ):
        """
            :param amount: (Int) Quantidade de arquivos.
            :param average_size: (String) Tamanho médio e unidade de medida sem espaço. As unidades
            de medida sendo 'B', 'kB', 'MB' ou 'GB'.
            :param measuring_unit: (String) Unidade de medida.
            :param tolerance_percentage: (Int) Porcentagem de tolerância.
            :return: (Int) Tempo limite de transferência, sendo a soma da estimativa com a tolerância.
        """
        total_size = 0
        total_size = amount * average_size

        # Converte o tamanho total para MB.
        total_size = self.parse_to_MB(total_size, measuring_unit)

        # Verifica velocidade de download.
        download_speed = InternetTester.get_download_speed()

        # Calcula o tempo estimado de download e adiciona a tolerância.
        transfer_estimate = total_size / download_speed
        transfer_timeout = round(transfer_estimate + (transfer_estimate / 100 * tolerance_percentage))
        if transfer_timeout < 10:
            transfer_timeout = 10
        return transfer_timeout

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
