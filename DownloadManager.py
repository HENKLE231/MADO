from SeleniumManager import SeleniumManager
from SystemManager import SystemManager
from PDFManager import PDFManager
import time


class DownloadManager:
    def __init__(self, config_ma, communication_options):
        self.communication_options = communication_options
        # Cria e carrega variáveis.
        self.manga_name = config_ma.config_list['manga_name']
        self.next_page_link = config_ma.config_list['base_link']
        self.num_chapters = config_ma.config_list['num_chapters']
        self.download_dir = config_ma.config_list['download_dir']
        self.files_dir = config_ma.config_list['files_dir']
        self.final_dir = config_ma.config_list['final_dir']
        self.is_select = config_ma.config_list['is_select'] == '1'
        self.chapter_number_by = config_ma.config_list['chapter_number_by']
        self.chapter_number_value = config_ma.config_list['chapter_number_value']
        self.select_read_mode_by = config_ma.config_list['select_read_mode_by']
        self.select_read_mode_value = config_ma.config_list['select_read_mode_value']
        self.visible_text = config_ma.config_list['visible_text']
        self.chapter_number = {
            'by': config_ma.config_list['chapter_number_by'],
            'value': config_ma.config_list['chapter_number_value']
        }
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
        queue.put(['display_info', error_lines, 'Erro!'])
        queue.put(['kill_secondary_process'])

    def download(self, queue):
        """
            :param queue: (Queue) Instância da Queue.
            Baixa os capítulos do mangá.
        """

        # Instancia classes.
        selenium_ma = SeleniumManager()
        system_ma = SystemManager()

        # Informa o inicio do processo.
        queue.put([self.communication_options.DISPLAY_INFO, ['Iniciou.'], 'Download'])

        # Limpa pasta de arquivos desnecessários.
        unnecessary_files = system_ma.find_files(self.files_dir, [''])
        system_ma.delete(unnecessary_files)

        # Limpa os downloads de imagens ainda não transferidos para pasta de edição.
        unmoved_images = system_ma.find_files(self.download_dir, [f'{self.manga_name}_', '.jpg'], 2)
        system_ma.delete(unmoved_images)

        # Informa o progresso.
        queue.put([self.communication_options.DISPLAY_INFO, ['Obtendo links das imagens.', f'Progresso: {0:.2%}']])

        there_is_no_chapter = True
        for i in range(self.num_chapters):
            # Abre navegador.
            try:
                selenium_ma.open_nav('normal', headless=True)
            except Exception as error:
                self.end_process(queue, str(error))

            # Abre o link do capítulo.
            try:
                selenium_ma.open_link(self.next_page_link)
            except Exception as error:
                self.end_process(queue, str(error))

            queue.put([self.communication_options.SAVE_LAST_LINK, self.next_page_link])

            # Seleciona o modo de leitura com páginas abertas.
            if self.visible_text:
                try:
                    selenium_ma.select_read_mode_open_pages(self.select_read_mode_by, self.select_read_mode_value, self.visible_text)
                except Exception as error:
                    error = str(error)
                    if 'Unable to locate element' in error:
                        error = f'Não foi possível encontrar o botão de modo de leitura.'
                    selenium_ma.close_nav()
                    self.end_process(queue, error)

            # Obtem o número do capítulo
            try:
                current_chapter = selenium_ma.get_current_chapter(self.select, self.chapter_number_by, self.chapter_number_value)
            except Exception as error:
                error = str(error)
                if 'Unable to locate element' in error:
                    error = 'Não foi possível encontrar o número do capítulo.'
                selenium_ma.close_nav()
                self.end_process(queue, error)

            # Obtem os links das imagens.
            try:
                selenium_ma.get_imgs_src(self.manga_name, current_chapter, self.frames_location, self.imgs_location)
            except Exception as error:
                error = str(error)
                if 'Unable to locate element' in error:
                    error = f'Não há capítulo {current_chapter}.'
                    queue.put([self.communication_options.DISPLAY_INFO, [error]])
                    selenium_ma.close_nav()
                    break
                else:
                    self.end_process(queue, error)

            # Salva existência de capitulo.
            if there_is_no_chapter:
                there_is_no_chapter = False

            if i != self.num_chapters:
                try:
                    self.next_page_link = selenium_ma.get_next_page_link(self.next_page_button_location)
                except Exception as error:
                    error = str(error)
                    if 'Unable to locate element' in error:
                        error = f'Não há capítulo {current_chapter}.'
                        queue.put([self.communication_options.DISPLAY_INFO, [error]])
                        # Fecha o navegador.
                        selenium_ma.close_nav()
                        break
                    else:
                        selenium_ma.close_nav()
                        self.end_process(queue, error)

            # Fecha o navegador.
            selenium_ma.close_nav()

            # Informa o progresso.
            completion_percentage = (i + 1) / self.num_chapters
            queue.put([self.communication_options.UPDATE_LAST_LINES, [f'Progresso: {completion_percentage:.2%}']])

        # Se não há capítulo, encerra.
        if there_is_no_chapter:
            self.end_process(queue, 'Não há capítulo para ser baixado.')

        # Informa o progresso.
        queue.put([self.communication_options.DISPLAY_INFO, ['Iniciando downloads.', f'Progresso: {0:.2%}']])

        # Configuração para navegador abrir fora da tela.
        size_and_position = [0, 0, system_ma.screen_x, system_ma.screen_y]

        # Abre navegador.
        selenium_ma.open_nav(page_load_strategy='normal', size_and_position=size_and_position)

        # Salva identificador do navegador.
        queue.put([self.communication_options.SAVE_BROWSER_HANDLE, system_ma.get_current_window_handle()])

        # Seleciona imagens não baixadas.
        imgs_to_download = [(img_name, link) for img_name, link, downloaded in selenium_ma.imgs_info if not downloaded]

        # Varre informações das imagens.
        for current_img_index, img_info in enumerate(imgs_to_download):
            # Desempacota variáveis.
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

            # Se é a última imagem espera 1 segundo antes de fechar o navegador.
            if current_img_index + 1 == len(selenium_ma.imgs_info):
                time.sleep(0.5)

            # Informa o progresso.
            completion_percentage = selenium_ma.get_percentage_of_downloaded_files(self.download_dir)
            queue.put([self.communication_options.UPDATE_LAST_LINES, [f'Progresso: {completion_percentage:.2%}']])

        # Fecha o navegador.
        selenium_ma.close_nav()

        # Salva identificador do navegador.
        queue.put([self.communication_options.SAVE_BROWSER_HANDLE, 0])

        # Informa o progresso.
        queue.put([self.communication_options.DISPLAY_INFO, ['Iniciando transferência de imagens para pasta de edição.']])

        # Move as imagens para uma pasta adequada.
        patterns = [f'{self.manga_name}_', '.jpg']
        downloaded_imgs = system_ma.find_files(self.download_dir, patterns)
        system_ma.move_files(downloaded_imgs, self.files_dir)
        downloaded_imgs = system_ma.find_files(self.files_dir, patterns)

        # Informa o progresso.
        queue.put([self.communication_options.DISPLAY_INFO, ['Imagens movidas para pasta de edição.']])

        # Obtem o nome das imagens.
        num_imgs = len(downloaded_imgs)

        # Informa o progresso.
        queue.put([self.communication_options.DISPLAY_INFO, ['Iniciando conversão para PDF.', f'Progresso: {0:.2%}']])

        # Converte imagens para PDF.
        for current_img_index, img_path in enumerate(downloaded_imgs):
            try:
                PDFManager.convert_to_pdf(img_path)
            except Exception as error:
                self.end_process(queue, str(error))

            # Informa o progresso.
            completion_percentage = (current_img_index + 1) / num_imgs
            queue.put([self.communication_options.UPDATE_LAST_LINES, [f'Progresso: {completion_percentage:.2%}']])

        # Encontra os PDFs.
        pdfs_paths = system_ma.find_files(self.files_dir, ['.pdf'])

        # Identifica quantos e quais capítulos foram baixados.
        chapters = list(set([path[path.index('_') + 1:path.index('-')] for path in pdfs_paths]))
        num_chapters = len(chapters)

        # Informa o progresso.
        queue.put([self.communication_options.DISPLAY_INFO, ['Iniciando compilação dos capítulos.', f'Progresso: {0:.2%}']])

        for chapter_index, chapter in enumerate(chapters):
            # Seleciona imagens pertencentes a esse capítulo.
            chapter_files = [path for path in pdfs_paths if path[path.index('_') + 1:path.index('-')] == chapter]

            # Compila os capítulos baixados.
            try:
                PDFManager.compile_chapters(self.manga_name, chapter, chapter_files, self.final_dir)
            except Exception as error:
                self.end_process(queue, str(error))

            # Informa o progresso.
            completion_percentage = (chapter_index + 1) / num_chapters
            queue.put([self.communication_options.UPDATE_LAST_LINES, [f'Progresso: {completion_percentage:.2%}']])

        # Limpa pasta de arquivos desnecessários.
        unnecessary_files = system_ma.find_files(self.files_dir, [''])
        system_ma.delete(unnecessary_files)

        # Informa o progresso.
        queue.put([self.communication_options.DISPLAY_INFO, ['Concluído com sucesso!'], 'Concluído!'])

        # Encerra processo de download.
        queue.put([self.communication_options.END])
