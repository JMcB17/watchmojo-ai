import re
import json
from pathlib import Path

import youtube_dl
import webvtt
import ffmpeg


# todo: burger
# todo: top 15's


TOP10_TITLE_REGEX = r'.*Top 10.*'
PROMPT_REGEX = re.compile(r'.*Top 10 (.*)')
TOP_10_NUMBERS_FROM_ONE_THROUGH_TEN = (
    ('10', 'ten'),
    ('9', 'nine'),
    ('8', 'eight'),
    ('7', 'seven'),
    ('6', 'six'),
    ('5', 'five'),
    ('4', 'four'),
    ('3', 'three'),
    ('2', 'two'),
    ('1', 'one'),
)

downloads_folder = 'downloads'


def rip_frames(v_fp: Path, subtitle_lang='en', subtitle_format='vtt', img_format='jpg'):
    # todo: fix this - if phrase is split across subtitle lines, the program won't find it.
    searches = TOP_10_NUMBERS_FROM_ONE_THROUGH_TEN
    results = {}

    # search for timestamps
    for caption in webvtt.read(v_fp.with_suffix(f'.{subtitle_lang}.{subtitle_format}')):
        for search in searches:
            for search_variant in search:
                if f'number {search_variant}' in caption.text.lower():
                    results[search[0]] = caption.start
                    break

    # get frames with ffmpeg
    for number, timestamp in results.items():
        # Take single frame from timestamp and put it in <id>-number-<number>.<img format>
        stream = ffmpeg.input(v_fp, ss=timestamp)
        stream = ffmpeg.output(stream,
                               str(v_fp.with_suffix(f'.{number}.{img_format}')),
                               frames=1)
        ffmpeg.run(stream)

    # delete video file
    v_fp.unlink()


def process_subtitles(v_fp: Path, subtitle_lang='en', subtitle_format='vtt'):
    searches = TOP_10_NUMBERS_FROM_ONE_THROUGH_TEN

    # todo: fix
    captions_block = ' '.join([c.text.replace('\n', '') for c in
                               webvtt.read(v_fp.with_suffix(f'.{subtitle_lang}.{subtitle_format}'))])

    # get indices of search terms
    captions_block_search_range = captions_block
    search_index_addition = 0
    sindices = {}
    for search in searches:
        if search[0] == '10':
            sindices[search[0]] = 0
        else:
            for search_variant in search:
                result = captions_block_search_range.find(search_variant)
                if result != -1:
                    sindices[search[0]] = search_index_addition + result
                    search_index_addition += result
                    captions_block_search_range = captions_block_search_range[result:]
                    break

    # get substrings from indices
    results = {}
    sindices_keys = sorted(sindices.keys(), key=int, reverse=True)
    for key_index, key in enumerate(sindices_keys):
        if key_index == len(sindices_keys)-1:
            results[key] = captions_block[sindices[key]:]
        else:
            results[key] = captions_block[sindices[key]:sindices[sindices_keys[key_index+1]]]

    # get prompt text from title of video
    results['prompt'] = re.match(PROMPT_REGEX, v_fp.stem).group(1)

    # dump to json
    with open(v_fp.with_suffix('.json'), 'w') as json_file:
        json.dump(results, json_file)


def process_video(progress_hook_dict):
    if progress_hook_dict['status'] != 'finished':
        return

    video_file_path = Path(progress_hook_dict['filename'])
    rip_frames(video_file_path)
    process_subtitles(video_file_path)


ydl_args = {
    # only download few videos for testing
    # command line option is --max-downloads LIMIT
    'playlistend': 3,
    'matchtitle': TOP10_TITLE_REGEX,
    'format': 'mp4',
    'writethumbnail': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitlesformat': 'vtt',
    'subtitleslangs': ['en'],
    # default: '%(title)s-%(id)s.%(ext)s'
    'outtmpl': f'/{downloads_folder}/%(id)s-%(title)s.%(ext)s',
    'progress_hooks': [process_video],
}

with youtube_dl.YoutubeDL(ydl_args) as ydl:
    # ydl.download([input('Playlist link:')])
    # todo: skip videos already downloaded
    # todo: multithreading?
    ydl.download(['https://www.youtube.com/playlist?list=UUaWd5_7JhbQBe4dknZhsHJg'])
