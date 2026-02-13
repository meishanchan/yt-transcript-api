from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)
CORS(app) # 允許跨域存取

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')

    if not video_id:
        return jsonify({"error": "Missing video_id parameter"}), 400

    try:
        # 1. 取得該影片所有可用的字幕列表 (包含自動產生的)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 2. 設定我們想要的語言優先順序
        # 'zh-TW': 台灣繁體
        # 'zh-Hant': 繁體中文
        # 'zh': 通用中文 (很多自動產生字幕是用這個代碼)
        # 'zh-CN': 簡體
        # 'en': 英文 (最後備案)
        languages_priority = ['zh-TW', 'zh-Hant', 'zh', 'zh-CN', 'en']
        
        # 3. 聰明搜尋：程式會自動在「手動」與「自動產生」中尋找最符合的語言
        target_transcript = transcript_list.find_transcript(languages_priority)
        
        # 4. 抓取資料並合併
        result_data = target_transcript.fetch()
        full_text = " ".join([item['text'] for item in result_data])
        
        return jsonify({"text": full_text})

    except Exception as e:
        # 若真的抓不到，回傳錯誤訊息
        return jsonify({"error": str(e), "message": "無字幕或無法存取"}), 500

if __name__ == '__main__':
    app.run()
