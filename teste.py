import os
from PIL import Image

for file in os.listdir(r'C:\Users\Henrique\Desktop\Excluir'):
    print('file: {}'.format(file))
    if file.split('.')[-1] != 'pdf':
        print('file: {}'.format(file))
        file_name = os.path.basename(file).split('.')[-2]
        imagem = Image.open(file)
        imagem_convertida = imagem.convert('RGB')
        imagem_convertida.save('{}.pdf'.format(file_name))
        