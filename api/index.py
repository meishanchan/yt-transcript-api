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
        # --- 變色龍策略開始 ---
        
        # 1. 檢查是否有標準方法 'get_transcript'
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=['zh-TW', 'zh-Hant', 'zh', 'zh-CN', 'en']
            )
            # 整理結果
            full_text = " ".join([item['text'] for item in transcript_list])
            return jsonify({"text": full_text, "method": "standard"})

        # 2. 檢查是否有怪異方法 'fetch' (根據你的診斷結果)
        elif hasattr(YouTubeTranscriptApi, 'fetch'):
            # 嘗試直接呼叫 fetch
            # 注意：這裡假設 fetch 的用法跟標準差不多
            transcript_list = YouTubeTranscriptApi.fetch(video_id)
            
            # 有些變體回傳的是物件，有些是列表，這裡做防呆
            if isinstance(transcript_list, list):
                full_text = " ".join([item.get('text', '') for item in transcript_list])
            else:
                # 如果回傳的是單一物件
                full_text = str(transcript_list)
                
            return jsonify({"text": full_text, "method": "fetch_variant"})

        # 3. 檢查是否有 'list_transcripts' (新版標準)
        elif hasattr(YouTubeTranscriptApi, 'list_transcripts'):
            tx_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # 嘗試抓中文，抓不到抓英文，再抓不到隨便抓一個
            try:
                transcript = tx_list.find_transcript(['zh-TW', 'zh-Hant', 'zh', 'en'])
            except:
                transcript = next(iter(tx_list))
            
            result = transcript.fetch()
            full_text = " ".join([item['text'] for item in result])
            return jsonify({"text": full_text, "method": "list_transcripts"})
            
        else:
            return jsonify({
                "error": "Unknown library version", 
                "available_methods": dir(YouTubeTranscriptApi)
            }), 500

    except Exception as e:
        return jsonify({"error": str(e), "message": "字幕抓取失敗"}), 500

if __name__ == '__main__':
    app.run()
