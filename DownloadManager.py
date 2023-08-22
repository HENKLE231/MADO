from SeleniumManager import SeleniumManager
from ConfigManager import ConfigManager
from SystemManager import SystemManager
from PDFManager import PDFManager
import time


class DownloadManager:
    def __init__(self):
        # Instancia classe necessária.
        config_ma = ConfigManager()

        # Cria e carrega variáveis.
        self.manga_name = config_ma.config_list['manga_name']
        self.base_link = config_ma.config_list['base_link']
        self.chapter = int(config_ma.config_list['initial_chapter'])
        self.final_chapter = int(config_ma.config_list['final_chapter'])
        self.download_dir = config_ma.config_list['download_dir']
        self.files_dir = config_ma.config_list['files_dir']
        self.final_dir = config_ma.config_list['final_dir']
        self.next_page_link = self.base_link
        self.frames_location = {
            'by': config_ma.config_list['frames_location_by'],
            'value': config_ma.config_list['frames_location_value']
        }
        self.imgs_location = {
            'by': config_ma.config_list['imgs_location_by'],
            'value': config_ma.config_list['imgs_location_value']
        }
        self.next_page_button_location = {
            'by': config_ma.config_list['next_page_button_location_by'],
            'value': config_ma.config_list['next_page_button_location_value']
        }

    @staticmethod
    def end_process(queue, error):
        """
            :param queue: (Queue) Instancia da Queue.
            :param error: (String) Mensagem de erro.
            Finalisa processo de download e avisa na tela.
        """
        error_lines = []
        if 'ERR_INTERNET_DISCONNECTED' in error:
            error = 'Sem internet.'

        if "\n" in error:
            # Divide a mensagem de erro por linhas.
            error_lines = [line.strip() for line in error.split("\n") if len(line) > 0]
        else:
            error_lines.append(error)

        # Interrompe o processo
        queue.put(['show_info', error_lines, 'Erro!'])
        queue.put(['kill_secondary_process'])

    def start_download(self, queue):
        """
            :param queue: (Queue) Instância da Queue.
            Baixa os capítulos do mangá.
        """

        # Instancia classes.
        selenium_ma = SeleniumManager()
        system_ma = SystemManager()

        # Salva identificador do processo
        queue.put(['save_secondary_process_id', SystemManager.get_current_process_id()])

        # Limpa pasta de arquivos desnecessários.
        unnecessary_files = system_ma.find_files(self.files_dir, [''])
        system_ma.delete(unnecessary_files)

        # Informa o inicio do processo.
        queue.put(['show_info', ['Iniciou.'], 'Download'])

        # Limpa os downloads de imagens ainda não transferidos para pasta de edição.
        unmoved_images = system_ma.find_files(self.download_dir, [f'{self.manga_name}_', '.jpg'], 2)
        system_ma.delete(unmoved_images)

        # Configurações.
        there_is_no_chapter = True
        num_chapters = self.final_chapter - self.chapter + 1
        current_chapter_index = 0

        # Informa o progresso.
        queue.put(['show_info', ['Obtendo links das imagens.', f'Progresso: {0:.2%}']])

        while self.chapter <= self.final_chapter:
            # Abre navegador.
            selenium_ma.open_nav('eager', True)

            # Abre o link do capítulo.
            try:
                selenium_ma.open_link(self.next_page_link)
            except Exception as error:
                self.end_process(queue, str(error))

            queue.put(['save_last_link', self.next_page_link])

            # Obtem os links das imagens.
            try:
                selenium_ma.get_imgs_src(self.manga_name, self.chapter, self.frames_location, self.imgs_location)
            except Exception as error:
                error = str(error)
                if 'Unable to locate element' in error:
                    error = f'Não há capítulo {self.chapter}.'
                    queue.put(['show_info', [error]])
                    selenium_ma.close_nav()
                    break

            if there_is_no_chapter:
                there_is_no_chapter = False

            # Avisa do progresso.
            completion_percentage = (current_chapter_index + 1) / num_chapters
            queue.put(['update_last_lines', [f'Progresso: {completion_percentage:.2%}']])

            if self.chapter != self.final_chapter:
                try:
                    self.next_page_link = selenium_ma.get_next_page_link(self.next_page_button_location)
                except Exception as error:
                    error = str(error)
                    if 'Unable to locate element' in error:
                        error = f'Não há capítulo {self.chapter + 1}.'
                        queue.put(['show_info', [error]])
                        # Fecha o navegador.
                        selenium_ma.close_nav()
                        break
                    else:
                        selenium_ma.close_nav()
                        self.end_process(queue, error)

            # Fecha o navegador.
            selenium_ma.close_nav()

            self.chapter += 1
            current_chapter_index += 1

        # Se não há capítulo, encerra.
        if there_is_no_chapter:
            self.end_process(queue, 'Não há capítulo para ser baixado.')

        # Configuração para navegador abrir fora da tela.
        size_and_position = [0, 0, system_ma.screen_x, system_ma.screen_y]

        # Abre navegador.
        selenium_ma.open_nav(size_and_position=size_and_position)

        # Avisa do progresso.
        queue.put(['show_info', ['Iniciando downloads.', f'Progresso: {0:.2%}']])

        completion_percentage = 0
        while True:
            imgs_to_download = [(img_name, link) for img_name, link, downloaded in selenium_ma.imgs_info if not downloaded]
            for current_img_index, img_info in enumerate(imgs_to_download):
                img_name, link = img_info

                # Abre link.
                try:
                    selenium_ma.open_link(link)
                except Exception as error:
                    self.end_process(queue, str(error))

                # Baixa imagem.
                try:
                    selenium_ma.download_img(img_name, link)
                except Exception as error:
                    self.end_process(queue, str(error))

                # Informa do progresso.
                completion_percentage = selenium_ma.get_percentage_of_downloaded_files(self.download_dir)
                queue.put(['update_last_lines', [f'Progresso: {completion_percentage:.2%}']])

                # Se é a última imagem espera 1 segundo antes de fechar o navegador.
                if current_img_index + 1 == len(selenium_ma.imgs_info):
                    time.sleep(1)
            if completion_percentage == 1:
                break

        # Fecha o navegador.
        selenium_ma.close_nav()

        # Informa do progresso.
        queue.put(['show_info', ['Downloads concluídos.']])

        # Move as imagens para uma pasta adequada.
        pattern = f'{self.manga_name}_'
        imgs_to_move = system_ma.find_files(self.download_dir, [pattern])
        system_ma.move_files(imgs_to_move, self.files_dir)

        # Informa o progresso.
        queue.put(['show_info', ['Imagens movidas para pasta de edição.']])

        # Obtem o nome das imagens.
        images_to_convert = system_ma.find_files(self.files_dir, [''])
        num_imgs = len(images_to_convert)

        # Avisa do progresso.
        queue.put(['show_info', ['Iniciando conversão para PDF.', f'Progresso: {0:.2%}']])

        for current_img_index, img_path in enumerate(images_to_convert):
            # Converte imagens para PDF.
            try:
                PDFManager.convert_to_pdf(img_path)
            except Exception as error:
                self.end_process(queue, str(error))

            # Informa o progresso.
            completion_percentage = (current_img_index + 1) / num_imgs
            queue.put(['update_last_lines', [f'Progresso: {completion_percentage:.2%}']])

        # Encontra os PDFs.
        pdfs_paths = system_ma.find_files(self.files_dir, ['.pdf'])

        # Identifica quantos e quais capítulos foram baixados.
        chapters = list(set([path[path.index('_') + 1:path.index('-')] for path in pdfs_paths]))
        num_chapters = len(chapters)

        # Informa o progresso.
        queue.put(['show_info', ['Iniciando compilação dos capítulos.', f'Progresso: {0:.2%}']])

        for chapter_index, chapter in enumerate(chapters):
            chapter_files = [path for path in pdfs_paths if path[path.index('_') + 1:path.index('-')] == chapter]

            # Compila os capítulos baixados.
            try:
                PDFManager.compile_chapters(chapter, chapter_files, self.final_dir)
            except Exception as error:
                self.end_process(queue, str(error))

            # Avisa do progresso.
            completion_percentage = (chapter_index + 1) / num_chapters
            queue.put(['update_last_lines', [f'Progresso: {completion_percentage:.2%}']])

        # Limpa pasta de arquivos desnecessários.
        unnecessary_files = system_ma.find_files(self.files_dir, [''])
        system_ma.delete(unnecessary_files)

        # Informa o progresso.
        queue.put(['show_info', ['Concluído com sucesso!'], 'Concluído!'])

        queue.put(['end'])