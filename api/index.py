from flask import Flask, jsonify
import sys
import os

app = Flask(__name__)

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    debug_info = {}
    try:
        # 1. 嘗試匯入庫
        import youtube_transcript_api
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # 2. 檢查庫的來源位置 (這能看出是不是讀到你自己的檔案)
        debug_info['library_location'] = getattr(youtube_transcript_api, '__file__', 'unknown')
        
        # 3. 檢查庫裡面有哪些功能 (列出所有屬性)
        debug_info['available_attributes'] = dir(YouTubeTranscriptApi)
        
        # 4. 檢查 Python 版本
        debug_info['python_version'] = sys.version

        return jsonify(debug_info)

    except Exception as e:
        return jsonify({"error": str(e), "trace": "Import failed"})

if __name__ == '__main__':
    app.run()
