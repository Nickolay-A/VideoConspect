"""
Модуль, который выполняет транскрибацию звуковой дорожки
"""
import os
import re
import tempfile

from typing import Union

import whisper
import torch


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Переменая пути, если работать через subprocess
# path_for_sub = sys.argv[1]

def get_text(path: str, lang: Union[str, None] = None) -> None:
    """
    Функция выполняет транскрибацию звуковой дорожки
    На вход требует путь к аудиофайлу в формате .mp3
    """
    # имя файла
    file_name = os.path.basename(path)
    # проверим, что файл действительно сформирован с помощью модуля getaudio
    regex = r'\d+_\d+_([a-z]+)\.mp3'
    match = re.match(regex, file_name)

    if match:
        lang = match.group(1)
    # модуль whisper для транскрибации
    model = whisper.load_model('medium')

    with torch.cuda.device(device):
        result = model.transcribe(audio=path, language=lang)

    path_to_save = path.replace('mp3', 'txt')
    with open(path_to_save, 'w', encoding='utf-8') as file:
        file.write(result['text'])

    torch.cuda.empty_cache()

    return None
