import pypdf as pyf
from pathlib import Path
from PIL import Image
import os


class PDFManipulator:
    @staticmethod
    def convert_to_pdf(files_dir, file):
        """
            :param files_dir: (String) Caminho da pasta do arquivo.
            :param file: (String) Nome do arquivo.
            :return: (String) Mensagem de erro se necessário senão vazio.
        """

        # Define largura máxima.
        max_width = 1200

        try:
            # Abre a imagem.
            image_location = str(Path(r'{}/{}'.format(files_dir, file)))
            img = Image.open(image_location)

            # Redimensiona a imagem se ela possui um tamanho superior ao definido.
            width, height = img.size
            if width > max_width:
                difference = max_width / width
                new_width = int(width * difference)
                new_height = int(height * difference)
                img = img.resize((new_width, new_height))

            # Converte imagem.
            img_converted = img.convert('RGB')

            # Salva e fecha.
            pdf_name = r'{}/{}.pdf'.format(files_dir, file[:file.index('.')])
            pdf_name = str(Path(pdf_name))
            img_converted.save(pdf_name)
            img.close()
            img_converted.close()

            # Exclui imagem antiga.
            os.remove(image_location)
        except Exception as e:
            return str(e)

    @staticmethod
    def compile_chapters(files_dir, files, chapters_dir, chapter):
        """
            :param files_dir: (String) Caminho da pasta dos arquivos.
            :param files: (String) Nomes do arquivos.
            :param chapters_dir: (String) Caminho da pasta dos capítulos compilados.
            :param chapter: (String) Número do capítulo.
            :return: (String) Mensagem de erro se necessário senão vazio.
        """
        try:
            # Cria um pdf
            pdf_chapter = pyf.PdfWriter()

            for file in files:
                # Se o pdf pertencer a esse capítulo ele é adicionado ao pdf
                if chapter in file[file.index('_') + 1:file.index('-')]:
                    pdf_location = str(Path(r'{}/{}'.format(files_dir, file)))
                    pdf_pages = pyf.PdfReader(pdf_location)
                    for page in pdf_pages.pages:
                        pdf_chapter.add_page(page)

            with Path(f'{chapters_dir}/Martial Peak - {chapter}.pdf').open(mode='wb') as pdf_file:
                pdf_chapter.write(pdf_file)
        except Exception as e:
            return str(e)
