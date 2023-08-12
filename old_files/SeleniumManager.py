from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PendingFunctionsManager import PendingFunctionsManager as PFM
import os


class SeleniumManipulator:
    def __init__(self):
        self.service = Service(ChromeDriverManager().install())
        self.options = None
        self.nav = None
        self.imgs_info = []

    def open_nav(self, page_load_strategy='normal', display='', size_and_position=None):
        """
            :param page_load_strategy: (String) Estratégia de carregamento de página, 'normal' espera a página
            carregar completamente ou 'eager' espera apenas as estruturas carregarem.
            :param display: (String) 'headless' para não aparecer ou '' para aparecer.
            :param size_and_position: (Tulple) Tupla com largura, altura, e coordenadas do ponto inicial da janela.
            Abre o navegador Google Chrome automatizado.
        """
        self.options = webdriver.ChromeOptions()
        self.options.page_load_strategy = page_load_strategy
        self.options.add_argument('auto-open-devtools-for-tabs')

        # Define exibição.
        if display == 'headless':
            self.options.add_argument('user-agent=Mozilla/5.0'
                                      '(Windows NT 10.0; Win64; x64)'
                                      'AppleWebKit/537.36'
                                      '(KHTML, like Gecko)'
                                      'Chrome/111.0.0.0'
                                      'Safari/537.36')
            self.options.add_argument('headless')
        else:
            self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
            if size_and_position:
                size_x, size_y, position_x, position_y = size_and_position
                self.options.add_argument(r'window-size={},{}'.format(size_x, size_y))
                self.options.add_argument(r'window-position={},{}'.format(position_x, position_y))

        # Abre navegador.
        self.nav = webdriver.Chrome(service=self.service, options=self.options)

    def close_nav(self, queue):
        """
            :param queue: (Queue) Instância da Queue.
            Fecha navegador Google Chrome automatizado e retira das funções pendentes a função de fecha-lo.
        """
        self.nav.close()
        self.nav = None
        pending_functions = PFM.get_pending_functions(queue)
        if pending_functions:
            for function in pending_functions:
                if function[0] == 'close_automated_chrome_window':
                    PFM.remove_pending_function(queue, function)
                    break

    def open_link(self, link, queue):
        """
            :param link: (String) Endereço de um site.
            :param queue: (Queue) Instância da Queue.
            :return: (String) Mensagem de erro se necessário senão vazio.
        """
        status_msg = ''
        try:
            # Abre link.
            self.nav.get(link)

            # Adiciona na lista de funções pendentes a função de fechar o navegador.
            pending_functions = PFM.get_pending_functions(queue)
            if pending_functions:
                for function in pending_functions:
                    if function[0] == 'close_automated_chrome_window':
                        PFM.remove_pending_function(queue, function)
                        PFM.add_pending_function(queue, [function[0], [self.nav.title]])
                        break
        except Exception as e:
            error = str(e)
            if 'ERR_INTERNET_DISCONNECTED' in error:
                status_msg = 'Sem internet.'
            else:
                status_msg = error
        return status_msg

    def get_imgs_urls(self, manga_name, chapter):
        """
            :param manga_name: (String) Nome do mangá.
            :param chapter: (Int) Número do capítulo.
            :return: (String) Mensagem de erro se necessário senão vazio.
        """
        status_msg = ''
        try:
            # Pega o endereço de todas as imagens do mangá.
            chapter_frame = self.nav.find_element('id', 'chapter-video-frame')
            imgs = chapter_frame.find_elements('tag name', 'img')
            for i, img in enumerate(imgs):
                page_num = i

                # Monta o nome da imagem como ela será salva posteriormente.
                if len(str(page_num)) < 2:
                    page_num = f'0{i}'
                img_name = f'{manga_name}_{chapter}-{page_num}.jpg'

                # Salva na instância o nome da imagem o endereço dela e que ela não foi baixada.
                self.imgs_info.append([img_name, img.get_attribute('src'), False])
        except Exception as e:
            error = str(e)
            if 'Unable to locate element' in error:
                status_msg = f'Não há capítulo {chapter}.'
            else:
                status_msg = error
        return status_msg

    def execute_script(self, script):
        """
            :param script: (Array) Lista com comandos de JavaScript.
            Executa o script no navegador Google Chrome automatizado.
        """
        for command in script:
            self.nav.execute_script(command)

    def download_img(self, img_name, url):
        """
            :param img_name: (String) Nome da imagem.
            :param url: (String) Endereço da imagem.
            :return: (String) Mensagem de erro se necessário senão vazio.
            Baixa a imagem.
        """
        status_msg = ''
        # Edita o script de download.
        download_script = [
            'button=document.createElement("div")',
            f"""button.innerHTML='<a href="{url}"download="{img_name}"id="download"></a>'""",
            'document.getElementsByTagName("body")[0].append(button)',
            'document.getElementById("download").click()',
        ]
        try:
            # Baixa a imagem.
            self.execute_script(download_script)
        except Exception as e:
            error = str(e)
            if 'ERR_INTERNET_DISCONNECTED' in error:
                status_msg = 'Sem internet.'
            else:
                status_msg = error
        return status_msg

    def get_percentage_of_downloaded_files(self, download_dir):
        """
            :param download_dir: (String) Caminho para pasta de downloads.
            :return: (Float) Porcentagem de imagens a serem baixadas que já se encontram na pasta de downloads.
        """
        # Verifica número total de imagens a serem baixadas.
        num_downloads = len(self.imgs_info)
        num_completed_downloads = 0
        for current_img_index, img_info in enumerate(self.imgs_info):
            img_name, ulr, downloaded = img_info
            if os.path.isfile(os.path.join(download_dir, img_name)):
                if not downloaded:
                    # Marca imagem como baixada.
                    self.imgs_info[current_img_index][2] = True
                num_completed_downloads += 1
        return num_completed_downloads / num_downloads
