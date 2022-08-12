import os

from main import files_id
from utils.helpers import send_message, send_document, send_music
from utils.help_functions import update_statistics

from utils.advertisement.views import check_views

from utils.shazam.recognize_music import recognize_music
from utils.shazam.deezer_api import DeezerApi


async def recognizer_main(chat_id, user_lang, audio_file_name):
    music_info_dict = await recognize_music(audio_file_name)
    os.remove(audio_file_name)

    if music_info_dict is None:
        await send_message(chat_id, 'unable-recognize', user_lang)
        await update_statistics('error', user_lang)
        return

    await update_statistics('download', user_lang)

    track_id = music_info_dict['deezer_id']
    music_lyrics = music_info_dict['lyrics']
    music_title = music_info_dict['title']
    music_artist = music_info_dict['artist']

    music_name = f'{music_title} - {music_artist}'

    await send_message(chat_id, 'recognize-success', user_lang, args=music_name, parse='markdown')

    await send_lyrics(chat_id, music_name, music_lyrics)

    await send_recognized_music(chat_id, user_lang, track_id)

    await check_views(chat_id, user_lang)


async def send_lyrics(chat_id, music_name, lyrics_to_save):
    if lyrics_to_save is None:
        return

    lyrics_file_name = f'music/{music_name}.txt'
    with open(lyrics_file_name, 'w') as file_to_write:
        file_to_write.write(lyrics_to_save)

    await send_document(chat_id, lyrics_file_name, music_name)
    os.remove(lyrics_file_name)


async def send_recognized_music(chat_id, user_lang, track_id):
    # Check if there is a music file id
    music_file_id = files_id.get(track_id)
    if music_file_id is not None:
        await send_music(chat_id, str(music_file_id, 'utf-8'))
        return

    # Download deezer music and get track info
    deezer_api = DeezerApi(track_id, quality=3)
    track_dict = await deezer_api.download_track()

    # Check, if the track dict is exists
    if track_dict is None:
        deezer_api = DeezerApi(track_id, quality=1)
        track_dict = await deezer_api.download_track()
        if track_dict is None:
            await send_message(chat_id, 'unable-track', user_lang)
            return

    music_dir = track_dict['music_dir']
    title = track_dict['track_info']['title']
    artist = track_dict['track_info']['artist']['name']
    duration = track_dict['track_info']['duration']

    # Send Deezer music to user
    music_id = await send_music(chat_id, open(music_dir, 'rb'), title=title, performer=artist, duration=duration)

    # Save music file id to db
    if music_id is not None:
        files_id.set(track_id, music_id)

    os.remove(music_dir)

