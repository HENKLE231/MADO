from SeleniumManager import SeleniumManager
from ConfigManager import ConfigManager
import time


selenium_ma = SeleniumManager()
config_ma = ConfigManager()

manga_name = config_ma.config_list['manga_name']
base_link = config_ma.config_list['base_link']
chapter = int(config_ma.config_list['initial_chapter'])
final_chapter = int(config_ma.config_list['final_chapter'])
imgs_dir = config_ma.config_list['imgs_dir']
download_dir = config_ma.config_list['download_dir']
files_dir = config_ma.config_list['files_dir']
final_dir = config_ma.config_list['final_dir']

# Abre navegador.
selenium_ma.open_nav('eager', False)

# Abre o link do capítulo inicial.
selenium_ma.open_link(base_link)

time.sleep(5)

# # TODO: COLOCAR CONFIGS NO GUI
# frames_location = {
#     'by': 'id',
#     'value': 'chapter-video-frame'
# }
# imgs_location = {
#     'by': 'tag name',
#     'value': 'img'
# }
#
# while self.chapter <= self.final_chapter:
#     # Obtem os links das imagens.
#     self.verify_outcome(
#         queue,
#         selenium_ma.get_imgs_src(self.manga_name, self.chapter, frames_location, imgs_location),
#         selenium_ma
#     )
#
#     # if not there_are_imgs:
#     #     there_are_imgs = True
#     #
#     # # Fecha o navegador.
#     # selenium_ma.close_nav(queue)
#     #
#     # # Avisa do progresso.
#     # completion_percentage = (current_chapter_index + 1) / num_chapters
#     # info_window.update_last_lines([f'Progresso: {completion_percentage:.2%}'])
#
#     self.chapter += 1
#     current_chapter_index += 1