from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

# 嘗試匯入
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

app = Flask(__name__)
CORS(app)

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400

    try:
        # --- 最終修正邏輯 ---
        
        # 1. 優先嘗試標準新版 (list_transcripts)
        if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
            try:
                tx_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = tx_list.find_transcript(['zh-TW', 'zh-Hant', 'zh', 'en'])
                result = transcript.fetch()
                full_text = " ".join([item['text'] for item in result])
                return jsonify({"text": full_text, "method": "standard_new"})
            except Exception as e:
                # 如果標準版失敗，往下走
                pass

        # 2. 嘗試「實例化」後的 fetch (針對你的錯誤訊息修正)
        if hasattr(YouTubeTranscriptApi, 'fetch'):
            try:
                # 關鍵修正：先加括號 () 建立實體，再呼叫 fetch
                yt_instance = YouTubeTranscriptApi() 
                transcript_data = yt_instance.fetch(video_id)
                
                # 處理回傳資料 (怕格式不同，做防呆)
                if isinstance(transcript_data, list):
                    full_text = " ".join([item.get('text', '') for item in transcript_data])
                else:
                    full_text = str(transcript_data)
                    
                return jsonify({"text": full_text, "method": "instance_fetch"})
            except TypeError:
                # 如果實例化失敗，試試看舊版靜態呼叫 (Static Call)
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                full_text = " ".join([item['text'] for item in transcript_data])
                return jsonify({"text": full_text, "method": "static_fallback"})

        # 3. 如果以上都沒中，最後一搏
        # 有些古老版本直接用 class 呼叫 get_transcript
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
             transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
             full_text = " ".join([item['text'] for item in transcript_list])
             return jsonify({"text": full_text, "method": "old_standard"})

        return jsonify({"error": "No method worked"}), 500

    except Exception as e:
        # 回傳詳細錯誤，方便我們看是不是成功突破了「缺少參數」那一關
        return jsonify({"error": str(e), "message": "字幕抓取失敗"}), 500

if __name__ == '__main__':
    app.run()
