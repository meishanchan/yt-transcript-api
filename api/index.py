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
        # 1. 取得所有可用的字幕清單
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript = None
        
        # 2. 策略：層層過濾
        try:
            # 優先嘗試找中文系 (手動或自動皆可)
            transcript = transcript_list.find_transcript(['zh-TW', 'zh-Hant', 'zh', 'zh-CN'])
        except:
            try:
                # 找不到中文，試試看英文
                transcript = transcript_list.find_transcript(['en'])
            except:
                # 3. 最終大絕招：直接抓取「列表中的第一個」，不管它是什麼語言
                # (通常是自動產生的該影片原語言)
                transcript = next(iter(transcript_list))

        # 4. 抓取內容
        result_data = transcript.fetch()
        full_text = " ".join([item['text'] for item in result_data])
        
        return jsonify({
            "text": full_text, 
            "language_code": transcript.language_code, # 回傳抓到的語言代碼，方便除錯
            "is_generated": transcript.is_generated    # 回傳是否為自動產生
        })

    except Exception as e:
        # 若失敗，回傳詳細錯誤訊息
        return jsonify({"error": str(e), "message": "此影片真的完全無字幕，或 Vercel IP 被阻擋"}), 500

if __name__ == '__main__':
    app.run()
