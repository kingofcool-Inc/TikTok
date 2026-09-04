from flask import Flask, request, jsonify, render_template_string, Response
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEON DOWNLOADER</title>
    <style>
        body { background: #000; color: #0ff; font-family: monospace; text-align: center; padding: 20px; }
        input[type="text"] { width: 90%; padding: 12px; background: #111; border: 1px solid #0ff; color: #fff; margin-bottom: 10px; border-radius: 5px; }
        button { background: #0ff; color: #000; border: none; padding: 12px 24px; font-weight: bold; cursor: pointer; border-radius: 5px; }
        #result { margin-top: 20px; }
        img { max-width: 100%; height: auto; border: 2px solid #0ff; border-radius: 8px; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>⚡ NEON DOWNLOADER ⚡</h2>
    <input id="url" type="text" placeholder="Paste Facebook / TikTok link here">
    <button onclick="doDownload()">DOWNLOAD</button>
    <div id="result"></div>

    <script>
    async function doDownload() {
        const url = document.getElementById('url').value;
        const resultDiv = document.getElementById('result');
        if (!url) return;

        resultDiv.innerHTML = "Fetching download link...";

        try {
            const res = await fetch('/api/fetch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ url: url })
            });
            const data = await res.json();

            if (data.error || !data.download_url) {
                resultDiv.innerHTML = '<p style="color:red;">Error fetching video.</p>';
                return;
            }

            // Display thumbnail only (no play controls)
            let html = '<h3>' + (data.title || 'Downloading...') + '</h3>';
            if (data.thumbnail) {
                html += '<img src="' + data.thumbnail + '">';
            }
            resultDiv.innerHTML = html;

            // Trigger backend proxy download to force full MP4 file save
            const proxyUrl = '/api/download_file?url=' + encodeURIComponent(data.download_url) + '&title=' + encodeURIComponent(data.title || 'video');
            window.location.href = proxyUrl;

        } catch (err) {
            resultDiv.innerHTML = '<p style="color:red;">Failed to initiate download.</p>';
        }
    }
    </script>
</body>
</html>
"""

def get_fb_api(url):
    res = requests.post("https://api.getgetfb.com/v1/fetch", json={"url": url}, timeout=10)
    j = res.json()
    if j.get('success'):
        data = j.get('data', {})
        video_url = data.get('hd') or data.get('sd') or data.get('video_url')
        return {
            "title": data.get('title', 'Facebook Video'),
            "thumbnail": data.get('thumbnail'),
            "download_url": video_url
        }
    return None

def get_tiktok_api(url):
    # Resolve shortened URLs (e.g., vt.tiktok.com) to full URLs first
    try:
        resolved_res = requests.head(url, allow_redirects=True, timeout=5)
        url = resolved_res.url
    except Exception:
        pass

    res = requests.post("https://www.tikwm.com/api/", data={"url": url}, timeout=10)
    j = res.json()
    if j.get('data'):
        data = j.get('data', {})
        video_url = data.get('play') or data.get('wmplay')
        if video_url and video_url.startswith('/'):
            video_url = 'https://www.tikwm.com' + video_url
            
        return {
            "title": data.get('title', 'TikTok Video'),
            "thumbnail": data.get('cover'),
            "download_url": video_url
        }
    return None
    

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/fetch', methods=['POST'])
def fetch():
    data = request.get_json()
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        if "facebook.com" in url or "fb.watch" in url:
            result = get_fb_api(url)
        elif "tiktok.com" in url:
            result = get_tiktok_api(url)
        else:
            return jsonify({'error': 'Unsupported URL'}), 400

        if result and result.get('download_url'):
            return jsonify(result)
        return jsonify({'error': 'Could not extract direct download URL'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_file')
def download_file():
    video_url = request.args.get('url')
    title = request.args.get('title', 'video')
    if not video_url:
        return "Missing URL", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Stream the full video directly to the client
    r = requests.get(video_url, headers=headers, stream=True)
    filename = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip() or 'video'
    
    return Response(
        r.iter_content(chunk_size=1024*1024),
        headers={
            "Content-Type": "video/mp4",
            "Content-Disposition": f'attachment; filename="{filename}.mp4"'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
  
