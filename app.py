import os
from flask import Flask, request, Response, stream_with_context
import requests

app = Flask(name)

BOT_TOKEN = "8466409837:AAGBFHvpuUNdIzMev8k2MuCR_1RFxw2dhWE"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
DOMAIN = "https://ht-tahsan-movie-1.onrender.com"

# হোমপেজ
@app.route("/")
def home():
    return "<h1>Telegram Direct Downloader Bot is Active!</h1><p>Send a video to the Telegram bot to get a direct download link.</p>"

# বোটে মেসেজ বা ভিডিও আসলে এটি কাজ করবে
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        
        # যদি ইউজার কোনো ভিডিও পাঠায়
        if "video" in data["message"]:
            file_id = data["message"]["video"]["file_id"]
            download_link = f"{DOMAIN}/dl/{file_id}"
            
            msg_text = f"✅ আপনার ডাইরেক্ট ডাউনলোড লিংক তৈরি হয়েছে:\n\n🔗 {download_link}\n\nএই লিংকে ক্লিক করলেই ব্রাউজারে অটোমেটিক ডাউনলোড শুরু হয়ে যাবে।"
            
            # ইউজারকে লিংক পাঠিয়ে দেওয়া
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": msg_text,
                "parse_mode": "Markdown"
            })
            
        # যদি ইউজার নরমাল টেক্সট বা /start দেয়
        elif "text" in data["message"]:
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "👋 হ্যালো! যেকোনো ভিডিও আমাকে ফরোয়ার্ড করুন, আমি আপনাকে ডাইরেক্ট ডাউনলোড লিংক বানিয়ে দেব।"
            })

    return "OK", 200

# সরাসরি ফাইল ডাউনলোডের রাউট (/dl/FILE_ID)
@app.route("/dl/<file_id>")
def direct_download(file_id):
    try:
        # ফাইল পাথ নেওয়া
        res = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}").json()
        if not res.get("ok"):
            return "Error: File not found or Bot cannot access it.", 400

        file_path = res["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        # ফাইল স্ট্রিম করে ডাউনলোড করানো
        req = requests.get(download_url, stream=True)
        
        def generate():
            for chunk in req.iter_content(chunk_size=8192):
                yield chunk

        return Response(
            stream_with_context(generate()),
            content_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=Telegram_Video_{file_id[:6]}.mp4"}
        )
    except Exception as e:
        return f"Download Error: {str(e)}"

if name == "main":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
