from SeleniumManager import SeleniumManager
# from ScreenManager import ScreenManager
from ConfigManager import ConfigManager
from SystemManager import SystemManager
# from PDFManager import PDFManager
# from TimeManager import TimeManager
# TODO: TIRAR TIME
import time
# import os


class DownloadManager:
    def __init__(self):
        # Instancia classes necessárias.
        # TODO APAGAR
        system_ma = SystemManager()
        config_ma = ConfigManager()

        # Cria e carrega variáveis.
        self.manga_name = config_ma.config_list['manga_name']
        self.base_link = config_ma.config_list['base_link']
        self.chapter = int(config_ma.config_list['initial_chapter'])
        self.final_chapter = int(config_ma.config_list['final_chapter'])
        self.imgs_dir = config_ma.config_list['imgs_dir']
        self.download_dir = config_ma.config_list['download_dir']
        self.files_dir = config_ma.config_list['files_dir']
        self.final_dir = config_ma.config_list['final_dir']

        # TODO: APAGAR
        # self.left_side = system_ma.get_half_screen_coords('left')
        # self.right_side = system_ma.get_half_screen_coords('right')
        # self.middle_of_left_side = system_ma.get_middle_of_window(self.left_side)
        # self.middle_of_right_side = system_ma.get_middle_of_window(self.right_side)

    @staticmethod
    def verify_outcome(queue, error, selenium_ma=None):
        """
            :param queue: (Queue) Instancia da Queue.
            :param error: (String) Mensagem de erro.
            :param selenium_ma: (SeleniumManager) Instância do SeleniumManager.
            Se há erro, o download é finalizado.
        """
        if error:
            # Fecha o navegador se ainda aberto.
            if selenium_ma:
                selenium_ma.close_nav()

            # Divide a mensagem de erro por linhas.
            error_lines = [line.strip() for line in error.split("\n") if len(line) > 0]

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

        # Atualiza a tela.
        queue.put(['show_info', ['Iniciou.'], 'Download'])

        # Limpa os downloads de imagens ainda não transferidos para pasta de edição.
        unmoved_images = system_ma.find_files(self.download_dir, [f'{self.manga_name}_', '.jpg'], 2)
        system_ma.delete(unmoved_images)

        # Configurações.
        # TODO?: VERIFICAR NECESSIDADE
        # size_and_position = [0, 0, system_ma.screen_x, system_ma.screen_y]
        there_are_imgs = False
        num_chapters = self.final_chapter - self.chapter + 1
        current_chapter_index = 0
        completion_percentage = 0

        # Abre navegador.
        selenium_ma.open_nav('eager', True)

        # Abre o link do capítulo inicial.
        self.verify_outcome(
            queue,
            selenium_ma.open_link(self.base_link),
            selenium_ma
        )

        # TODO: COLOCAR CONFIGS NO GUI
        frames_location = {
            'by': 'id',
            'value': 'chapter-video-frame'
        }
        imgs_location = {
            'by': 'tag name',
            'value': 'img'
        }

        while self.chapter <= self.final_chapter:
            # Obtem os links das imagens.
            self.verify_outcome(
                queue,
                selenium_ma.get_imgs_src(self.manga_name, self.chapter, frames_location, imgs_location),
                selenium_ma
            )

            time.sleep(5)

            # if not there_are_imgs:
            #     there_are_imgs = True
            #
            # # Fecha o navegador.
            # selenium_ma.close_nav(queue)
            #
            # # Avisa do progresso.
            # completion_percentage = (current_chapter_index + 1) / num_chapters
            # info_window.update_last_lines([f'Progresso: {completion_percentage:.2%}'])

            self.chapter += 1
            current_chapter_index += 1
    #
    #     # Se há imagens para serem baixadas, continua.
    #     if there_are_imgs:
    #         # Abrindo navegador.
    #         selenium_ma.open_nav(size_and_position=size_and_position)
    #
    #         # Avisa do progresso.
    #         completion_percentage = 0
    #         info_window.show_info(['Iniciando downloads.', f'Progresso: {completion_percentage:.2%}'])
    #
    #         while True:
    #             imgs_to_download = [(img_name, url) for img_name, url, downloaded in selenium_ma.imgs_info if not downloaded]
    #             for current_img_index, img_info in enumerate(imgs_to_download):
    #                 img_name, url = img_info
    #
    #                 # Abrindo link
    #                 self.verify_outcome(
    #                     app_instaces,
    #                     selenium_ma.open_link(url, queue)
    #                 )
    #
    #                 # Baixando imagem
    #                 self.verify_outcome(
    #                     app_instaces,
    #                     selenium_ma.download_img(img_name, url)
    #                 )
    #
    #                 # Informando progresso
    #                 completion_percentage = selenium_ma.get_percentage_of_downloaded_files(self.download_dir)
    #                 info_window.update_last_lines([f'Progresso: {completion_percentage:.2%}'])
    #
    #                 if current_img_index + 1 == len(selenium_ma.imgs_info):
    #                     time.sleep(1)
    #             if completion_percentage == 1:
    #                 break
    #
    #         # Fecha o navegador.
    #         selenium_ma.close_nav(queue)
    #
    #         # Avisa do progresso.
    #         info_window.show_info(['Downloads concluídos.'])
    #
    #         # Move as imagens para uma pasta adequada.
    #         pattern = f'{self.manga_name}_'
    #         system_ma.move_files(self.download_dir, self.files_dir, pattern)
    #         info_window.show_info(['Imagens movidas para pasta de edição.'])
    #
    #         # Obtem o nome das imagens.
    #         files = os.listdir(self.files_dir)
    #         num_imgs = len(files)
    #
    #         # Avisa do progresso.
    #         completion_percentage = 0
    #         info_window.show_info(['Iniciando conversão para PDF.', f'Progresso: {completion_percentage:.2%}'])
    #
    #         for current_img_index, file in enumerate(files):
    #             # Converte imagens para PDF.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 PDFMa.convert_to_pdf(self.files_dir, file)
    #             )
    #
    #             # Avisa do progresso.
    #             completion_percentage = (current_img_index + 1) / num_imgs
    #             info_window.update_last_lines([f'Progresso: {completion_percentage:.2%}'])
    #
    #         # Obtem os nomes dos PDFs.
    #         files = os.listdir(self.files_dir)
    #
    #         # Identifica quantos e quais capítulos foram baixados.
    #         chapters = []
    #         for file in files:
    #             chapters.append(file[file.index('_') + 1:file.index('-')])
    #         chapters = list(set(chapters))
    #         num_chapters = len(chapters)
    #
    #         # Avisa do progresso.
    #         completion_percentage = 0
    #         info_window.update_last_lines(['Iniciando compilação dos capítulos.', f'Progresso: {completion_percentage:.2%}'])
    #
    #         for current_chapter_index, chapter in enumerate(chapters):
    #             # Compila os capítulos baixados.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 PDFMa.compile_chapters(self.files_dir, files, self.chapters_dir, chapter)
    #             )
    #
    #             # Avisa do progresso.
    #             completion_percentage = (current_chapter_index + 1) / num_chapters
    #             info_window.update_last_lines([f'Progresso: {completion_percentage:.2%}'])
    #
    #         # Limpa pasta de arquivos desnecessários.
    #         system_ma.clear_dirs([self.files_dir])
    #
    #         # Avisa do progresso.
    #         info_window.show_info(['Concluído com sucesso!'], 'Concluído!')
    #     else:
    #         # Avisa do progresso.
    #         info_window.interrupt_process(queue, root_window, ['Não há capítulo para ser baixado.'], 'Erro!')

        # Verificar antes da transferencia para possivel substituição.
        # # Limpa arquivos de downloads anteriores.
        # system_ma.clear_dirs([self.files_dir, self.chapters_dir])
        queue.put(['end'])

    # def transfer(self, queue, root_window, info_window):
    #     """
    #         :param queue: (Queue) Instância da Queue.
    #         :param root_window: (RootWindow) Instância da RootWindow.
    #         :param info_window: (InfoWindow) Instância da InfoWindow.
    #         Transfere capítulos.
    #     """
    #
    #     # Avisa do progresso.
    #     info_window.show_info(['Iniciou processo de transferência.'], 'Transferência')
    #
    #     # Instancia classes.
    #     screen_ma = ScreenMa(self.imgs_dir, 0)
    #     system_ma = SystemMa()
    #     time_control = TimeControl()
    #     app_instaces = [queue, root_window, info_window]
    #
    #     if self.final_dir == 'PC':
    #         if self.delete_chapters:
    #             # Deleta capítulos do destino final.
    #             system_ma.delete_files(self.pc_dir, [self.manga_name])
    #
    #         # Copia os capítulos para o diretório final.
    #         system_ma.copy_files(self.chapters_dir, self.pc_dir, self.manga_name)
    #
    #     else:
    #         if self.final_dir == 'Celular':
    #             # Abre explorador de arquivos.
    #             system_ma.open_explorer(self.download_dir)
    #
    #             # Espera abrir.
    #             new_window_name = system_ma.get_fold_name(self.download_dir)
    #             self.verify_outcome(
    #                 app_instaces,
    #                 system_ma.wait_until_open(10, new_window_name)
    #             )
    #             file_explorer_window = system_ma.get_window(new_window_name)
    #
    #             # Ocupa o lado esquerdo da tela.
    #             system_ma.set_window_position(file_explorer_window, self.left_side)
    #
    #             # Abre pasta do telefone.
    #             screen_ma.move_in_explorer(self.phone_dir)
    #
    #             # Espera abrir.
    #             screen_ma.wait_for(3, ['disconnected-device.png', 'search-field-when-on-martial-peak-fold.png'], 'one')
    #
    #             # Se o aparelho não está conectado interrompe o processo.
    #             if screen_ma.locate('disconnected-device.png'):
    #                 screen_ma.confirm()
    #                 screen_ma.close_windows_by_coords([self.middle_of_left_side])
    #                 info_window.interrupt_process(queue, root_window, ['Aparelho está desconectado.'], 'Erro!')
    #
    #             if self.delete_chapters:
    #                 # Avisa do progresso.
    #                 info_window.show_info(['Verificando se há capítulos no diretório final para excluir.'])
    #
    #                 # Atribui uma pausa maior às interações com a tela.
    #                 screen_ma.set_pause(0.5)
    #
    #                 # Espera para ver se a pasta está vazia
    #                 if not screen_ma.wait_for(5, ['0-items.png'], region=self.left_side, confidence=0.8):
    #                     info_window.show_info(['Não há capítulos para excluir.'])
    #                 else:
    #                     # Avisa do progresso.
    #                     info_window.show_info(['Excluindo capítulos.'])
    #
    #                     # Seleciona tudo da pasta.
    #                     screen_ma.click(self.middle_of_left_side)
    #                     screen_ma.select_all()
    #
    #                     # Deleta capítulos do destino final.
    #                     screen_ma.delete()
    #
    #                     # Espera por pergunta de confirmação.
    #                     self.verify_outcome(
    #                         app_instaces,
    #                         screen_ma.wait_for(5, ['delete-confirmation.png'])
    #                     )
    #
    #                     # Confirma deleção.
    #                     screen_ma.confirm()
    #
    #                     # Espera deletar.
    #                     self.verify_outcome(
    #                         app_instaces,
    #                         screen_ma.wait_for(5, ['0-items.png'], region=self.left_side)
    #                     )
    #
    #                     # Avisa do progresso.
    #                     info_window.show_info(['Capítulos excluidos.'])
    #
    #                     # Normaliza pausa das interações com a tela.
    #                     screen_ma.set_pause(0.3)
    #
    #             # Abre explorador de arquivos.
    #             system_ma.open_explorer(self.chapters_dir)
    #
    #             # Obtem nome da pasta.
    #             new_window_name = system_ma.get_fold_name(self.chapters_dir)
    #
    #             # Espera pasta abrir.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 system_ma.wait_until_open(10, new_window_name)
    #             )
    #             final_dir_window = system_ma.get_window(new_window_name)
    #
    #             # Ocupa o lado direito da tela.
    #             system_ma.set_window_position(final_dir_window, self.right_side)
    #
    #             # Atribui uma pausa maior às interações com a tela.
    #             screen_ma.set_pause(0.5)
    #
    #             # Espera carregar a pasta dos capítulos.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_for(15, ['chapter-label.png'], region=self.right_side),
    #                 [self.middle_of_left_side, self.middle_of_right_side]
    #             )
    #
    #             # Move os capítulos para o celular.
    #             chapter_coords = screen_ma.locate(r'chapter-label.png', region=self.right_side)
    #             screen_ma.click(chapter_coords)
    #             screen_ma.select_all()
    #             screen_ma.copy()
    #             screen_ma.click(self.middle_of_left_side)
    #             screen_ma.paste()
    #
    #             # Esperando iniciar transferência.
    #             screen_ma.close_windows_by_coords([self.middle_of_left_side, self.middle_of_right_side])
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_for(10, ['transfer-icon.png', 'replace-files-icon.png'], 'one')
    #             )
    #
    #             # Espera pela pergunta de confirmação de substituição de capítulos com o mesmo nome.
    #             if not screen_ma.wait_for(2, ['replace-files-icon.png']):
    #                 # Confirma substituição.
    #                 screen_ma.click(screen_ma.locate('checkbox-icon.png'))
    #                 screen_ma.click(screen_ma.locate('replace-files-icon.png'))
    #
    #                 # Espera continuar a transferência.
    #                 self.verify_outcome(
    #                     app_instaces,
    #                     screen_ma.wait_for(5, ['transfer-icon.png'])
    #                 )
    #
    #             # Normaliza pausa das interações com a tela.
    #             screen_ma.set_pause(0.3)
    #
    #             # Espera completar upload.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_until_become_invisible(
    #                     time_control.get_transfer_timeout('upload', self.chapters_dir, 'dir'),
    #                     ['transfer-icon.png']
    #                 )
    #             )
    #
    #         if self.final_dir == 'Google Drive':
    #             # Abre o Google Chrome.
    #             system_ma.open_app('chrome.exe')
    #             new_window_name = r'Nova guia - Google Chrome'
    #
    #             # Espera abrir.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 system_ma.wait_until_open(10, new_window_name)
    #             )
    #             chrome_window = system_ma.get_window(new_window_name)
    #
    #             # TODO: APAGAR.
    #             new_window_name = r'Nova guia anônima - Google Chrome'
    #             screen_ma.open_anonimous_tab()
    #             self.verify_outcome(
    #                 app_instaces,
    #                 system_ma.wait_until_open(10, new_window_name)
    #             )
    #             chrome_window = system_ma.get_window(new_window_name)
    #
    #             # Maximiza janela.
    #             system_ma.set_window_state('maximized', chrome_window)
    #
    #             # Entra no drive.
    #             screen_ma.paste_and_confirm(self.drive_url)
    #
    #             # Espera carregar.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_for(15, ['drive-icon.png', 'need-to-log-in.png'], 'one')
    #             )
    #
    #             # Verifica se precisa logar.
    #             if not screen_ma.wait_for(1, ['need-to-log-in.png']):
    #                 # Avisa da necessidade de conectar a conta.
    #                 info_window.show_info(['Acesse sua conta do Google Drive.'])
    #
    #                 # TODO: PAREI AQUI
    #                 # Mostra janela de aviso.
    #                 gui_id = system_ma.get_window(root_window.title)
    #                 system_ma.set_window_state('show', gui_id)
    #                 print(f'Core Transfer (window_state): {system_ma.get_window_state(gui_id)}')
    #                 time.sleep(5)
    #                 print(f'Core Transfer (window_state): {system_ma.get_window_state(gui_id)}')
    #
    #                 # Espera logar.
    #                 self.verify_outcome(
    #                     app_instaces,
    #                     screen_ma.wait_for(200, ['drive-icon.png'])
    #                 )
    #
    #             # Espera carregar pasta com o nome Martial Peak.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_for(15, ['martial-peak-on-breadcrumbs.png'], region=self.left_side)
    #             )
    #
    #             if self.delete_chapters:
    #                 # Atribui uma pausa maior às interações com a tela.
    #                 screen_ma.set_pause(0.5)
    #
    #                 # Espera o capítulo aparecer.
    #                 if not screen_ma.wait_for(1, ['chapter-label-on-drive.png']):
    #                     # Seleciona os capítulos.
    #                     chapter_on_drive_coords = screen_ma.locate('chapter-label-on-drive.png')
    #                     screen_ma.click(chapter_on_drive_coords)
    #                     screen_ma.select_all()
    #
    #                     # Deleta capítulos.
    #                     screen_ma.delete()
    #
    #                 # Normaliza pausa das interações com a tela.
    #                 screen_ma.set_pause(0.3)
    #
    #             # Clica no botão de adição de arquivos.
    #             screen_ma.click(screen_ma.locate('add-button-icon.png'))
    #
    #             # Espera pela opção de transferência de arquivos.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_for(5, ['upload-file-icon.png']),
    #                 [self.middle_of_left_side]
    #             )
    #
    #             # Seleciona opção de transferência.
    #             screen_ma.click(screen_ma.locate('upload-file-icon.png'))
    #
    #             # Espera pela janela de seleção de arquivo.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_for(7, ['icons-of-file-explorer.png']),
    #                 [self.middle_of_left_side]
    #             )
    #
    #             # Acessa pasta de capítulos.
    #             screen_ma.move_in_explorer(self.chapters_dir)
    #             screen_ma.press_keys(['tab', 'tab', 'tab', 'tab'])
    #
    #             # Seleciona todos capítulos.
    #             screen_ma.select_all()
    #
    #             # Confirma trasnferencia.
    #             screen_ma.confirm()
    #
    #             # Espera iniciar transferência.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_for(10, ['uploading.png', 'completed-uploads.png', 'completed-upload.png'], 'one'),
    #                 [self.middle_of_left_side]
    #             )
    #
    #             # Espera completar transferência.
    #             self.verify_outcome(
    #                 app_instaces,
    #                 screen_ma.wait_for(
    #                     time_control.get_transfer_timeout('update', self.chapters_dir, 'dir'),
    #                     ['completed-uploads.png', 'completed-upload.png'],
    #                     'one'
    #                 ),
    #                 [self.middle_of_left_side]
    #             )
    #
    #             # Fecha janela.
    #             system_ma.close_windows([system_ma.get_window_name_by_window(chrome_window)])
    #
    #     # Avisa do progresso.
    #     info_window.show_info(['Transferência realizada com sucesso!'], 'Concluído!')
