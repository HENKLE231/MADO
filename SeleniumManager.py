from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import Select
import os


class SeleniumManager:
    def __init__(self, files_dir):
        """
            :param files_dir: Pasta onde serão editadas as imagens.
        """
        self.service = EdgeService(EdgeChromiumDriverManager().install())
        self.options = None
        self.nav = None
        self.imgs_info = []
        self.options = webdriver.EdgeOptions()
        self.options.add_argument(r'download.default_directory={}'.format(files_dir))
        self.options.add_experimental_option("prefs", {"download.default_directory": files_dir})

    def open_nav(self, page_load_strategy='normal', headless=False, size_and_position=None):
        """
            :param page_load_strategy: (String) Estratégia de carregamento de página, 'normal' espera a página
            carregar completamente ou 'eager' espera apenas as estruturas carregarem.
            :param headless: (Boolean) Se deve se esconder.
            :param size_and_position: (Tuple) Tupla com largura, altura, e coordenadas do ponto inicial da janela.
            Abre o navegador automatizado.
        """
        # Configura opções.
        self.options.page_load_strategy = page_load_strategy
        self.options.add_argument('inprivate')
        self.options.add_argument('mute-audio')

        # Define exibição.
        if headless:
            self.options.add_argument('user-agent=Mozilla/5.0'
                                      '(Windows NT 10.0; Win64; x64)'
                                      'AppleWebKit/537.36'
                                      '(KHTML, like Gecko)'
                                      'Chrome/111.0.0.0'
                                      'Safari/537.36')
            self.options.add_argument('headless')
        else:
            self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
            if size_and_position:
                size_x, size_y, position_x, position_y = size_and_position
                self.options.add_argument(r'window-size={},{}'.format(size_x, size_y))
                self.options.add_argument(r'window-position={},{}'.format(position_x, position_y))

        # Abre navegador.
        self.nav = webdriver.Edge(options=self.options, service=self.service)

    def close_nav(self):
        """
            Fecha navegador.
        """
        try:
            self.nav.close()
        except AttributeError:
            pass
        self.nav = None

    def open_link(self, link):
        """
            :param link: (String) Link de site.
            Abre link no navegador.
        """
        self.nav.get(link)

    def select_read_mode_open_pages(self, select_read_mode_location, visible_text):
        """
            :param select_read_mode_location: (Dict de Strings) Pelo que procurará e o valor.
            :param visible_text: (String) Texto exibido na opção desejada.
            Seleciona uma opção do seletor.
        """
        # Seleciona o seletor.
        select = Select(self.nav.find_element(select_read_mode_location['by'], select_read_mode_location['value']))

        # Seleciona a opção desejada.
        select.select_by_visible_text(visible_text)

    def get_current_chapter(self, is_select, chapter_number_location):
        """
            :param is_select: (Boolean) Se o elemento é um seletor.
            :param chapter_number_location: (Dict de Strings) Pelo que procurará e o valor.
            :return: (String) Numero do capítulo atual.
        """
        # Encontra o texto.
        element = self.nav.find_element(chapter_number_location['by'], chapter_number_location['value'])
        if is_select:
            element = element.find_element('xpath', '//*[@selected="selected]')

        chapter_text = element.text

        # Encontra o número.
        first_number_found = False
        first_number_index = 0
        last_number_index = 0

        for i, char in enumerate(chapter_text):
            if char.isdigit():
                if not first_number_found:
                    first_number_index = i
                    last_number_index = i
                    first_number_found = True
                else:
                    last_number_index = i

        return chapter_text[first_number_index:last_number_index+1]

    def get_imgs_src(self, manga_name, chapter, frames_location, imgs_location):
        """
            :param manga_name: (String) Nome do mangá.
            :param chapter: (String) Número do capítulo.
            :param frames_location: (Dict de Strings) Pelo que procurará e o valor.
            :param imgs_location: (Dict de Strings) Pelo que procurará e o valor.
            Define os nomes e salva as fontes das imagens.
        """
        img_num = 0
        scopes = [self.nav]

        # Se é necessário selecionar algum escopo antes das imagens.
        if frames_location['by'] != 'Selecione' and frames_location['value']:
            scopes = self.nav.find_elements(frames_location['by'], frames_location['value'])

        # Varre os escopos.
        for scope in scopes:
            # Seleciona as imagens
            imgs = scope.find_elements(imgs_location['by'], imgs_location['value'])

            # Varre as imagens.
            for img in imgs:
                # Monta o nome da imagem como ela será salva posteriormente.
                page_num = img_num
                if len(str(page_num)) < 2:
                    page_num = f'0{page_num}'
                img_name = f'{manga_name}_{chapter}-{page_num}.jpg'

                # Salva na instância o nome da imagem e o endereço.
                self.imgs_info.append([img_name, img.get_attribute('src'), False])
                img_num += 1

    def get_next_page_link(self, next_page_button_location):
        """
            :param next_page_button_location: (Dict de Strings) Pelo que procurará e o valor.
            :return: (String) Link do próximo capítulo.
        """
        next_page_button = self.nav.find_element(next_page_button_location['by'], next_page_button_location['value'])
        return next_page_button.get_attribute('href')

    def execute_script(self, script):
        """
            :param script: (Array de Strings) Lista com comandos de JavaScript.
            Executa os comandos em JavaScript no navegador.
        """
        for command in script:
            self.nav.execute_script(command)

    def download_img(self, img_name, link):
        """
            :param img_name: (String) Nome da imagem.
            :param link: (String) Endereço da imagem.
            Baixa a imagem.
        """
        # Edita o script de download.
        download_script = [
            'button=document.createElement("div")',
            f"""button.innerHTML='<a href="{link}"download="{img_name}"id="download"></a>'""",
            'document.getElementsByTagName("body")[0].append(button)',
            'document.getElementById("download").click()',
        ]
        # Baixa a imagem.
        self.execute_script(download_script)

    def get_percentage_of_downloaded_files(self, files_dir):
        """
            :param files_dir: (String) Caminho onde serão baixados os arquivos.
            :return: (Float) Porcentagem de arquivos baixados.
            Informa procentagem de arquivos baixados e salva como baixadas.
        """
        # Verifica número total de arquivos a serem baixados.
        num_imgs = len(self.imgs_info)
        num_completed_downloads = 0

        # Verifica existência dos arquivos.
        for i, img_info in enumerate(self.imgs_info):
            img_name, link, downloaded = img_info
            if os.path.isfile(os.path.join(files_dir, img_name)):
                num_completed_downloads += 1
                # Salva como baixado.
                if not downloaded:
                    self.imgs_info[i][2] = True

        # Calcula a porcentagem de downloads completos.
        return num_completed_downloads / num_imgs
