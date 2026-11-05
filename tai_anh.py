"""
Tải ảnh thật của 22 loại cây từ Wikipedia vào thư mục anh/  (chạy MỘT LẦN trên máy bạn, cần có mạng).

Cách chạy (trong thư mục web, đã vào venv):
    python tai_anh.py

Kết quả: anh/rice.jpg, anh/maize.jpg, ... và file anh/NGUON.txt ghi nguồn từng ảnh (để ghi vào báo cáo).
Không cần cài thêm thư viện. Ảnh nào tải lỗi sẽ được báo, bạn tự bỏ ảnh đó vào thư mục anh/ với đúng tên file.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

THU_MUC = Path(__file__).parent / "anh"
THU_MUC.mkdir(exist_ok=True)

# tên cây trong dữ liệu  ->  tên bài trên Wikipedia tiếng Anh
BAI_WIKI = {
    "rice": "Rice", "maize": "Maize", "chickpea": "Chickpea", "kidneybeans": "Kidney bean",
    "pigeonpeas": "Pigeon pea", "mothbeans": "Vigna aconitifolia", "mungbean": "Mung bean",
    "blackgram": "Vigna mungo", "lentil": "Lentil", "pomegranate": "Pomegranate",
    "banana": "Banana", "mango": "Mango", "grapes": "Grape", "watermelon": "Watermelon",
    "muskmelon": "Cucumis melo", "apple": "Apple", "orange": "Orange (fruit)",
    "papaya": "Papaya", "coconut": "Coconut", "cotton": "Cotton", "jute": "Jute", "coffee": "Coffee",
}
HEADERS = {"User-Agent": "CropRecommendationStudentProject/1.0 (hoc tap; python urllib)"}


def lay(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


nguon = []
for cay, bai in BAI_WIKI.items():
    if any((THU_MUC / f"{cay}.{d}").exists() for d in ("jpg", "jpeg", "png", "webp")):
        print(f"[bỏ qua] {cay}: đã có ảnh")
        continue
    try:
        api = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(bai.replace(" ", "_"))
        info = json.loads(lay(api))
        url = info["thumbnail"]["source"]
        url = re.sub(r"/\d+px-", "/640px-", url)          # lấy bản rộng 640px cho nét
        duoi = "png" if url.lower().split("?")[0].endswith(".png") else "jpg"
        (THU_MUC / f"{cay}.{duoi}").write_bytes(lay(url))
        trang = info.get("content_urls", {}).get("desktop", {}).get("page", "")
        nguon.append(f"{cay}.{duoi}\t{trang}")
        print(f"[ok]     {cay}: {bai}")
    except Exception as loi:
        print(f"[LỖI]    {cay}: {loi}  -> hãy tự bỏ ảnh vào anh/{cay}.jpg")
    time.sleep(1.5)                                        # nghỉ giữa các lần để không bị chặn

if nguon:
    with open(THU_MUC / "NGUON.txt", "a", encoding="utf-8") as f:
        f.write("Ảnh lấy từ Wikipedia / Wikimedia Commons (giấy phép Creative Commons). Trang nguồn:\n")
        f.write("\n".join(nguon) + "\n")
print("Xong. Mở lại web (Ctrl + C rồi streamlit run app.py) để thấy ảnh.")
