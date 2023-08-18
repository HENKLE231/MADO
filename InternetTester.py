import speedtest


class InternetTester:
    @staticmethod
    def get_download_speed():
        """
            :return: (Float) Velocidade de download em MB/s.
        """
        st = speedtest.Speedtest()
        return round(st.upload() / 8000000, 1)

    @staticmethod
    def get_upload_speed():
        """
            :return: (Float) Velocidade de upload em MB/s.
        """
        st = speedtest.Speedtest()
        return round(st.upload() / 8000000, 1)

    @staticmethod
    def get_ping_delay():
        """
            :return: (Float) Velocidade de ping em ms.
        """
        st = speedtest.Speedtest()
        return st.results.ping

