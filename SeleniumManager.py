from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os


class SeleniumManager:
    def __init__(self):
        self.service = EdgeService(EdgeChromiumDriverManager().install())
        self.options = None
        self.nav = None
        self.imgs_info = []

    def open_nav(self, page_load_strategy='normal', headless=False, size_and_position=None):
        """
            :param page_load_strategy: (String) Estratégia de carregamento de página, 'normal' espera a página
            carregar completamente ou 'eager' espera apenas as estruturas carregarem.
            :param headless: (Boolean) Se deve se esconder.
            :param size_and_position: (Tuple) Tupla com largura, altura, e coordenadas do ponto inicial da janela.
            Abre o navegador Google Chrome automatizado.
        """
        self.options = webdriver.EdgeOptions()
        self.options.page_load_strategy = page_load_strategy
        # TODO: TESTAR SEM
        # self.options.add_argument('auto-open-devtools-for-tabs')
        self.options.add_argument("inprivate")

        # Define exibição.
        if headless:
            # TODO: VERIFICAR NECESSIDADE.
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
        self.nav = webdriver.Edge(options=self.options, service=self.service)

    def close_nav(self):
        """
            Fecha navegador.
        """
        self.nav.close()
        self.nav = None

    def open_link(self, link):
        """
            :param link: (String) Link de site.
            :return: (String) Mensagem de erro se necessário.
            Abre link no navegador.
        """
        status_msg = ''
        try:
            # Abre link.
            self.nav.get(link)
        except Exception as e:
            error = str(e)
            if 'ERR_INTERNET_DISCONNECTED' in error:
                status_msg = 'Sem internet.'
            else:
                status_msg = error
        return status_msg

    def get_nav_title(self):
        """
            :return: (String) Titulo da página.
        """
        return self.nav.title

    def get_imgs_src(self, manga_name, chapter, frames_location, imgs_location):
        """
            :param manga_name: (String) Nome do mangá.
            :param chapter: (Int) Número do capítulo.
            :param frames_location: (Array de Strings) Pelo que procurara e o valor.
            :param imgs_location: (Array de Strings) Pelo que procurara e o valor.
            :return: (String) Mensagem de erro se necessário senão vazio.
        """
        status_msg = ''
        img_num = 0
        scopes = [self.nav]
        try:
            # Se é necessário selecionar algum escopo antes das imagens.
            if frames_location:
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
                    self.imgs_info.append([img_name, img.get_attribute('src')])
                    print([img_name, img.get_attribute('src')])
                    img_num += 1

        except Exception as e:
            error = str(e)
            if 'Unable to locate element' in error:
                status_msg = f'Não há capítulo {chapter}.'
            else:
                status_msg = error
        return status_msg

    def execute_script(self, script):
        """
            :param script: (Array de Strings) Lista com comandos de JavaScript.
            Executa o comando js no navegador.
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
            :return: (Float) Porcentagem de downloads completos.
        """
        # Verifica número total de imagens a serem baixadas.
        num_imgs = len(self.imgs_info)
        num_completed_downloads = 0

        # Verifica existência dos arquivos.
        for img_info in self.imgs_info:
            if os.path.isfile(os.path.join(download_dir, img_info[0])):
                num_completed_downloads += 1

        # Calcula a porcentagem de downloads completos.
        return num_completed_downloads / num_imgs