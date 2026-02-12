from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)
# 開啟跨域存取 (CORS)，這樣你的 GAS 才能呼叫這裡
CORS(app)

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')

    if not video_id:
        return jsonify({"error": "Missing video_id parameter"}), 400

    try:
        # 嘗試抓取字幕，優先順序：繁體 -> 簡體 -> 英文
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=['zh-TW', 'zh-Hant', 'zh-CN', 'en']
        )
        
        # 將字幕列表合併成單一字串
        full_text = " ".join([item['text'] for item in transcript_list])
        
        return jsonify({"text": full_text})

    except Exception as e:
        return jsonify({"error": str(e), "message": "無法獲取字幕，可能是該影片無字幕或權限受限。"}), 500

# 這是為了讓 Vercel 能夠正確識別 Flask app
if __name__ == '__main__':
    app.run()
