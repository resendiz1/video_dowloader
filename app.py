import os
from flask import Flask, render_template, request, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/info', methods=['POST'])
def info():
    url = request.form['url']
    
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])

    # Filtramos para que solo se vean formatos de video con resolución
    video_formats = [
        {
            'format_id': f['format_id'],
            'ext': f['ext'],
            'resolution': f.get('resolution') or f'{f.get("width", "?")}x{f.get("height", "?")}',
            'filesize': f.get('filesize', 0)
        }
        for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
    ]

    return render_template('select.html', url=url, formats=video_formats, title=info.get('title'))

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_id = request.form['format_id']
    
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': format_id,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    app.run(debug=True)
