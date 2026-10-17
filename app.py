import os
from flask import Flask, render_template_string, request, Response, stream_with_context
import requests

app = Flask(__name__)

# বোট টোকেনটি এখানে সরাসরি বা এনভায়রনমেন্ট থেকে সেট করা হলো
BOT_TOKEN = "8466409837:AAGBFHvpuUNdIzMev8k2MuCR_1RFxw2dhWE"

@app.route("/")
def home():
    return "Telegram Video Downloader System is running successfully!"

@app.route("/download/<file_id>")
def download_video(file_id):
    try:
        # ১. টেলিগ্রাম API থেকে ফাইলের পাথ বা লিংক বের করা
        file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
        response = requests.get(file_info_url)
        res_data = response.json()

        if not res_data.get("ok"):
            return "Error: Invalid File ID or Bot cannot access the file.", 400

        file_path = res_data["result"]["file_path"]
        
        # ২. টেলিগ্রাম সার্ভার থেকে সরাসরি ভিডিও ডাউনলোড লিংক তৈরি
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        # ৩. ব্রাউজারে স্ট্রিম করে ভিডিও ডাউনলোড করার ব্যবস্থা করা
        req = requests.get(download_url, stream=True)
        
        def generate():
            for chunk in req.iter_content(chunk_size=4096):
                yield chunk

        return Response(stream_with_context(generate()), content_type=req.headers.get("content-type", "video/mp4"))

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
