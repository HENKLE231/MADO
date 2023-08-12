import psutil as ps
import pandas as pd
from datetime import date
from ScreenManager import ScreenManipulator as ScreenMa


screen_ma = ScreenMa('imgs/', 0.3)
print(screen_ma.locate('need-to-log-in.png'))







# process_info = []
# today = date.today().strftime('%d/%m/%Y')
# for process in ps.process_iter():
#     # Conversão para texto.
#     p_txt = str(process)
#
#     # Pega o PID.
#     pid_start_index = p_txt.index('pid=') + 4
#     pid_end_index = p_txt.index(',', pid_start_index)
#     pid = int(p_txt[pid_start_index:pid_end_index])
#
#     # Pega o nome.
#     name_start_index = p_txt.index("name='") + 6
#     name_end_index = p_txt.index("'", name_start_index)
#     name = p_txt[name_start_index:name_end_index]
#
#     # Pega o tempo de início.
#     started = ''
#     if 'started' in p_txt:
#         started_start_index = p_txt.index("started='") + 9
#         started_end_index = p_txt.index("'", started_start_index)
#         started = p_txt[started_start_index:started_end_index]
#         if ' ' not in started:
#             # started = started.replace('-', '/')
#             process_info.append((started, pid, name))
#
# process_info.sort(key=lambda x: x[0])
#
# print('Started - PID - name')
# for process in process_info:
#     print(process)
