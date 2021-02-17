from pathlib import Path

import youtube_dl
import webvtt
import ffmpeg

# plan:
# download with match title, limit for testing e.g. 10 videos
# download hook to run function on
# save split subtitles to <yt vid id>.json
# save frames to <yt vid id>-<number>.jpeg


TOP10_TITLE_REGEX = r'.*Top 10.*'
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


def process_subtitle_file(v_fp: Path, subtitle_lang='en', subtitle_format='vtt', img_format='jpg'):
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


def process_video(progress_hook_dict):
    if progress_hook_dict['status'] != 'finished':
        return

    video_file_path = Path(progress_hook_dict['filename'])
    process_subtitle_file(video_file_path)
    # todo: process subtitles into json


ydl_args = {
    # only download few videos for testing
    # command line option is --max-downloads LIMIT
    'playlistend': 3,
    'matchtitle': TOP10_TITLE_REGEX,
    'format': 'mp4',
    'writethumbnail': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'sbutitlesformat': 'vtt',
    'subtitleslangs': ['en'],
    # default: '%(title)s-%(id)s.%(ext)s'
    'outtmpl': f'/{downloads_folder}/%(id)s.%(ext)s',
    'progress_hooks': [process_video],
}

with youtube_dl.YoutubeDL(ydl_args) as ydl:
    # ydl.download([input('Playlist link:')])
    # todo: skip videos already downloaded
    # todo: multithreading?
    ydl.download(['https://www.youtube.com/playlist?list=UUaWd5_7JhbQBe4dknZhsHJg'])
