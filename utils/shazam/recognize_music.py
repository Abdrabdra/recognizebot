import asyncio

from shazamio import Shazam

from utils.shazam.deezer_api import get_deezer_track_id


async def recognize_music(file_name):
    shazam_api = Shazam()
    recognition_result = await shazam_api.recognize_song(file_name)

    if 'track' in recognition_result.keys():
        track_result = recognition_result['track']
        music_isrc = track_result['isrc']

        music_lyrics = None
        if 'text' in track_result['sections'][1].keys():
            music_lyrics_list = track_result['sections'][1]['text']
            music_lyrics = '\n'.join(music_lyrics_list)

        music_title = track_result['title']
        music_artist = track_result['subtitle']

        deezer_id = await get_deezer_track_id(music_isrc)

        music_info_dict = {'title': music_title, 'artist': music_artist, 'lyrics': music_lyrics, 'deezer_id': deezer_id}
        return music_info_dict
    return None


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(recognize_music())
