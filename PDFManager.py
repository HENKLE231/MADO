import pypdf as pyf
from pathlib import Path
from PIL import Image
from TextManager import TextManager
import os


class PDFManager:
    @staticmethod
    def convert_to_pdf(file):
        """
            :param file: (String) Caminho do arquivo.
            Converte imagem para pdf e excluia antiga
        """

        # Define largura máxima.
        desired_width = 1200

        # Abre a imagem.
        img = Image.open(file)

        # Redimensiona a imagem com largura diferente da desejada.
        width, height = img.size
        if width != desired_width:
            difference = desired_width / width
            new_width = int(width * difference)
            new_height = int(height * difference)
            img = img.resize((new_width, new_height))

        # Converte imagem.
        img_converted = img.convert('RGB')

        # Salva e fecha.
        img_name = TextManager.get_last_piece_of_path(file)
        pdf_name = r'{}/{}.pdf'.format(file[:file.index(img_name)], img_name[:img_name.index('.')])
        pdf_name = str(Path(pdf_name))
        img_converted.save(pdf_name)
        img.close()
        img_converted.close()

        # Exclui imagem antiga.
        os.remove(file)

    @staticmethod
    def compile_chapters(manga_name, chapter, chapter_files, final_dir):
        """
            :param chapter: (String) Número do capítulo.
            :param chapter_files: (Array de String) Caminho dos arquivos do capítulo.
            :param final_dir: (String) Pasta final para compilação de arquivos.
            Compila o capítulo.
        """
        # Cria um pdf
        pdf_chapter = pyf.PdfWriter()

        # Adiciona imagens.
        for file in chapter_files:
            pdf_chapter.add_page(pyf.PdfReader(file).pages[0])

        # Salva arquivo final.
        with Path(f'{final_dir}/{manga_name} - {chapter}.pdf').open(mode='wb') as pdf_file:
            pdf_chapter.write(pdf_file)
