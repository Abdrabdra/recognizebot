import asyncio
import hashlib
import os
from functools import wraps, partial

from mutagen import id3, File
from mutagen.easyid3 import EasyID3

import requests
from mutagen.flac import FLACVorbisError
from mutagen.id3 import ID3, APIC
from requests.packages.urllib3.util.retry import Retry
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import aiohttp

SECRET = 'g4el58wc0zvf9na1'
DECRYPTED_URL = 'https://e-cdns-proxy-{0}.dzcdn.net/mobile/1/{1}'
AJAX_URL = 'https://www.deezer.com/ajax/gw-light.php'

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/68.0.3440.106 Safari/537.36'
)

HTTP_HEADERS = {
    'User-Agent': USER_AGENT,
    'Content-Language': 'en-US',
    'Cache-Control': 'max-age=0',
    'Accept': '*/*',
    'Accept-Charset': 'utf-8,ISO-8859-1;q=0.7,*;q=0.3',
    'Accept-Language': 'en-US;q=0.6,en;q=0.4',
    'Connection': 'keep-alive',
}

DEEZER_ISRC_URL = 'https://api.deezer.com/track/isrc:{}'

TOKEN = '0edd3c917560dd07b123e6e6015b2f7fc6f1902a3f632baea81d5850a8b9ed10339a1a3098409b74db60ced719a23' \
        'fb59a6c848a3e8a1206941ca3797d7c07facd8bf0142c4353ea9d81d726c43a3619f788c24dabdfea6b1de908dd9fe1ead0'


def wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


def get_track_download_url(md5, media_version, sngid, quality):
    """ Calculates the deezer download URL from a given MD5_ORIGIN (MD5 hash), SNG_ID and MEDIA_VERSION."""

    char = b'\xa4'.decode('unicode_escape')
    step1 = char.join((md5, quality, sngid, media_version))
    m = hashlib.md5()
    m.update(bytes([ord(x) for x in step1]))
    step2 = f'{m.hexdigest()}{char}{step1}{char}'
    step3 = step2.ljust(80, ' ')
    cipher = Cipher(algorithms.AES(bytes('jo6aey6haid2Teih', 'ascii')),
                    modes.ECB(), default_backend())
    encryptor = cipher.encryptor()
    step4 = encryptor.update(bytes([ord(x) for x in step3])).hex()
    decrypted_ready_url = DECRYPTED_URL.format(md5[0], step4)
    return decrypted_ready_url


def get_blow_fish_key(track_id):
    """ Calculates the Blow fish decrypt key for a given SNG_ID."""
    m = hashlib.md5()
    m.update(bytes([ord(x) for x in track_id]))
    id_md5 = m.hexdigest()
    bf_key = bytes(([(ord(id_md5[i]) ^ ord(id_md5[i + 16]) ^ ord(SECRET[i]))
                    for i in range(16)]))
    return bf_key


def decrypt_chunk(chunk, bf_key):
    """ Decrypt a given encrypted chunk with a blow fish key. """
    cipher = Cipher(algorithms.Blowfish(bf_key), modes.CBC(bytes([i for i in range(8)])), default_backend())
    decryptor = cipher.decryptor()
    dec_chunk = decryptor.update(chunk) + decryptor.finalize()
    return dec_chunk


class DeezerDownloader:
    def __init__(self):
        if TOKEN == '' or len(TOKEN) != 192:
            print('Wrong token.')
            return

        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)
        self._login_user_token(TOKEN)
        self.CSRFToken = self._api_call('deezer.getUserData')['checkForm']

    def _api_call(self, method, json_req=None):
        """ Requests info from the hidden api: gw-light.php."""

        unofficial_api_queries = {
            'api_version': '1.0', 'api_token': 'null' if method == 'deezer.getUserData' else self.CSRFToken,
            'input': '3', 'method': method
        }

        req = self._requests_retry_session().post(url=AJAX_URL, params=unofficial_api_queries, json=json_req).json()
        return req['results']

    def _login_user_token(self, token):
        """ Handles userToken for settings file, for initial setup.
            If no USER_ID is found, False is returned and thus the
            cookie arl is wrong. Instructions for obtaining your arl
            string are in the README.md
        """

        cookies = {'arl': token}
        self.session.cookies.update(cookies)
        req = self._api_call('deezer.getUserData')
        if not req['USER']['USER_ID']:
            return False
        else:
            return True

    def _requests_retry_session(self, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor,
                      status_forcelist=status_forcelist, method_whitelist=frozenset(['GET', 'POST']))

        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        return self.session

    def _get_json(self, media_type, media_id, subtype=""):
        """ Official API. This function is used to download the ID3 tags. Subtype can be 'albums' or 'tracks'."""
        url = f'https://api.deezer.com/{media_type}/{media_id}/{subtype}?limit=-1'
        return self._requests_retry_session().get(url).json()

    def _resume_download(self, url, file_size):
        resume_header = {'Range': 'bytes=%d-' % file_size}
        req = self._requests_retry_session().get(url, headers=resume_header, stream=True)
        return req

    def _download_track(self, filename, url, bf_key):
        """ Download and decrypts a track. Resumes download for tmp files."""
        temporary_file = f'{filename}.tmp'
        real_file_name = f'{filename}.mp3'

        if os.path.isfile(temporary_file):
            size_on_disk = os.stat(temporary_file).st_size  # size downloaded file
            # reduce size_on_disk to a multiple of 2048 for seamless decryption
            size_on_disk = size_on_disk - (size_on_disk % 2048)
            i = size_on_disk / 2048
            req = self._resume_download(url, size_on_disk)
        else:
            size_on_disk = 0
            i = 0
            req = self._requests_retry_session().get(url, stream=True)
            if req.headers['Content-length'] == '0':
                print("Empty file, skipping...\n", end='')
                return False

        # Decrypt content and write to file
        with open(temporary_file, 'ab') as fd:
            fd.seek(size_on_disk)  # jump to end of the file in order to append to it
            # Only every third 2048 byte block is encrypted.
            for chunk in req.iter_content(2048):
                if i % 3 == 0 and len(chunk) >= 2048:
                    chunk = decrypt_chunk(chunk, bf_key)
                fd.write(chunk)
                i += 1

        os.rename(temporary_file, real_file_name)
        return True

    def _add_audio_tags(self, music_dir, title, artist, track_thumbnail):
        try:
            audio = EasyID3(music_dir)
        except id3.ID3NoHeaderError:
            try:
                audio = File(music_dir, easy=True)
                audio.add_tags()
            except FLACVorbisError:
                return

        audio['title'] = title
        audio['artist'] = artist
        audio.save()

        thumb_content = self.session.get(track_thumbnail)

        audio = ID3(music_dir)
        audio['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=thumb_content.content)
        audio.save()

    def get_track(self, track_id, quality):
        """
        Calls the necessary functions to download and tag the tracks.
        Playlist must be a tuple of (playlistInfo, playlistTrack).
        """

        track_info = self._get_json('track', track_id)
        private_track_info = self._api_call('deezer.pageTrack', {'SNG_ID': track_id})['DATA']

        title = str(track_info['title']).replace('/', '')
        artist = str(track_info['artist']['name']).replace('/', '')
        track_thumbnail = track_info['album']['cover_medium']

        music_directory = 'music/{0} - {1}'.format(title, artist)

        decrypted_url = get_track_download_url(private_track_info['MD5_ORIGIN'],
                                               private_track_info['MEDIA_VERSION'],
                                               private_track_info['SNG_ID'],
                                               str(quality))

        bf_key = get_blow_fish_key(private_track_info['SNG_ID'])

        is_downloaded = self._download_track(music_directory, decrypted_url, bf_key)
        self.session.close()
        if not is_downloaded:
            return

        music_dir = music_directory + '.mp3'
        self._add_audio_tags(music_dir, title, artist, track_thumbnail)
        track_dict = {'music_dir': music_dir, 'track_info': track_info}
        return track_dict


class DeezerApi(object):
    def __init__(self, request_id=None, quality=None):
        self.request_id = request_id
        self.quality = quality

    @staticmethod
    async def _make_request(request_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as get_request:
                response = await get_request.json()
                return response

    @wrap
    def download_track(self):
        downloader = DeezerDownloader()
        try:
            track_dict = downloader.get_track(self.request_id, self.quality)
            return track_dict
        except Exception as err:
            print(err, 'downloader.get_track')
            return None

    async def get_track(self):
        get_album_url = 'https://api.deezer.com/track/{}'.format(self.request_id)
        response = await self._make_request(get_album_url)

        if 'error' in response.keys():
            return

        track_dict = {'music_dir': None, 'track_info': response}
        return track_dict


async def get_deezer_track_id(isrc_id):
    url_to_request = DEEZER_ISRC_URL.format(isrc_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(url_to_request) as get_request:
            response = await get_request.json()

            if 'error' in response.keys():
                return None

            deezer_track_id = response['id']
            return deezer_track_id


async def async_function():
    api = DeezerApi('')
    a = await api.download_track()
    print(a)


if __name__ == '__main__':
    asyncio.run(async_function())

