import youtube_dl

# plan:
# download with match title, limit for testing e.g. 10 videos
# download hook to run function on
# save split subtitles to <yt vid id>.json
# save frames to <yt vid id>-<number>.jpeg


TOP10_TITLE_REGEX = r'.*Top 10.*'


def process_video(progress_hook_dict):
    if progress_hook_dict['status'] != 'finished':
        return

    # todo: process videos


ydl_args = {
    # only download 5 videos for testing
    # command line option is --max-downloads LIMIT
    'playlistend': 5,
    'matchtitle': TOP10_TITLE_REGEX,
    'format': 'mp4',
    'writethumbnail': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'sbutitlesformat': 'vtt',
    'subtitleslangs': ['en'],
    # default: '%(title)s-%(id)s.%(ext)s'
    'outtmpl': '/downloads/%(id)s.%(ext)s',
    'progress_hooks': [process_video],
}

with youtube_dl.YoutubeDL(ydl_args) as ydl:
    # ydl.download([input('Playlist link:')])
    ydl.download(['https://www.youtube.com/channel/UCaWd5_7JhbQBe4dknZhsHJg'])
