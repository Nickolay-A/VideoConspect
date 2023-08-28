"""
модуль обработывает ссылку на видеоролик на YouTube и сохраняет
.mp3 файл
"""
import os
import re
import yt_dlp


def get_from_youtube(url: str,
                     temp_dir: str,
                     name: str) -> None:
    """
    Функция сохраняет .mp3 файл по переданной ссылке на youtube
    из указанной директории
    """
    # оставим от ссылки только значимую часть
    # отрежем принадлежность к плейлисту и каналу
    url = re.sub(r"[&].*", "", url)

    # определим параметры для объекта YoutubeDL
    ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(temp_dir, name),
            }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return None


if __name__ == '__main__':
    import tempfile
    import shutil

    from datetime import datetime


    with tempfile.TemporaryDirectory() as temp_dir_:
        name_=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        get_from_youtube(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                         temp_dir=temp_dir_,
                         name=name_)

        source_file = os.path.join(temp_dir_, f"{name_}.mp3")
        destination_file = f"test\\{name_}.mp3"
        shutil.copy2(source_file, destination_file)
