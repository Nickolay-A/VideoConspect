"""
Модуль, который выполняет транскрибацию звуковой дорожки
"""
import os
import re
import argparse
from tempfile import gettempdir
from multiprocessing import Process, Manager

import torch
from faster_whisper import WhisperModel

# создаем парсер аргументов
parser = argparse.ArgumentParser()
parser.add_argument('--path', help='Путь к подкаталогу')

# разбираем аргументы командной строки
parser_args = parser.parse_args()

# получаем значение аргумента
path_for_sub = parser_args.path


def work_log(args_list, return_list):
    """
    Функция выполняет определение модели и выполнение транскрибации
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    compute_type = 'float16' if torch.cuda.is_available() else 'int8_float16'
    model_size = 'medium'

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    audio_path = args_list[0]

    file_name = os.path.basename(audio_path)
    # проверим, что файл действительно сформирован с помощью модуля getaudio
    regex = r'\d+_\d+_([a-z]+)\.mp3'
    match = re.match(regex, file_name)

    if match:
        lang = match.group(1)

    segments, _ = model.transcribe(audio=audio_path, language=lang)
    segments_list = [segment.text for segment in segments]
    text = ' '.join(segments_list)
    return_list[0] = text

    path_to_save = audio_path.replace('mp3', 'txt')
    with open(path_to_save, 'w', encoding='utf-8') as file:
        file.write(text)

def run_whisper_seperate_proc(*args):
    """
    Функция выполняет запуск модели faster_whisper в отдельном потоке,
    т.к. иначе при выгрузке из видеопамяти она останавливает телеграмбота
    """
    with Manager() as manager:
        return_list = manager.list([None])
        process = Process(target=work_log, args=[args, return_list])
        process.start()
        process.join()
        process.close()
        return return_list[0]


if __name__ == '__main__':
    try:
        run_whisper_seperate_proc(path_for_sub)
    except Exception as error:
        print(f'Ошибка при получении текста: {error}')
