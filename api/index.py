from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)
CORS(app)

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')

    if not video_id:
        return jsonify({"error": "Missing video_id parameter"}), 400

    try:
        # 【復古相容模式】
        # 不使用 list_transcripts (因為你的伺服器版本太舊)
        # 改用傳統方法，但我們手動加入所有可能的中文代碼
        # 'zh' 是關鍵，很多自動產生的字幕都藏在這裡！
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=['zh', 'zh-TW', 'zh-Hant', 'zh-HK', 'zh-CN', 'en']
        )
        
        # 將字幕合併成字串
        full_text = " ".join([item['text'] for item in transcript_list])
        
        return jsonify({"text": full_text})

    except Exception as e:
        # 如果還是失敗，回傳錯誤
        return jsonify({"error": str(e), "message": "無法獲取字幕，請確認影片是否有字幕"}), 500

if __name__ == '__main__':
    app.run()
