# HƯỚNG DẪN DỰNG WEBSITE "ĐẤT & CÂY" BẰNG STREAMLIT (cho người chưa biết gì)

Website nhiều trang: nhập 4 chỉ số đất (N, P, K, pH), nhận gợi ý cây bằng **Random Forest tự cài đặt**, rồi xem
**cẩm nang trồng từ A đến Z** của từng cây, kèm lời khuyên cải tạo đất theo đất của chính người dùng.
Hướng dẫn viết cho **Windows**. Máy Mac/Linux làm tương tự, chỉ khác vài lệnh (có ghi chú).

---

## PHẦN 0. Thư mục `web/` có gì?

```
web/
├── app.py               ← KHUNG website: menu trên cùng, CSS chung, chân trang. File CHẠY.
├── trang_chu.py         ← Trang chủ (banner, 3 bước, cây nổi bật, số liệu, hỏi đáp)
├── trang_goi_y.py       ← Trang Gợi ý cây trồng (nhập đất, kết quả, biểu đồ, lời khuyên cải tạo đất)
├── trang_thu_vien.py    ← Thư viện 22 cây (lọc theo nhóm, tìm kiếm)
├── trang_cam_nang.py    ← Cẩm nang trồng chi tiết từng cây
├── trang_he_thong.py    ← Về hệ thống (độ chính xác, so sánh, hạn chế, hỏi đáp)
├── noi_dung_cay.py      ← NỘI DUNG chữ của 22 cây (mùa vụ, bón phân, sâu bệnh...). Sửa chữ ở đây.
├── giao_dien.py         ← Màu sắc, CSS, hàm vẽ biểu đồ dùng chung
├── du_lieu_web.py       ← Nạp dữ liệu và huấn luyện mô hình
├── dieu_huong.py        ← Danh sách trang để các nút chuyển trang
├── thuat_toan.py        ← Random Forest viết từ công thức (từ notebook của nhóm)
├── train.csv            ← 1760 mẫu huấn luyện (kết quả bước B4)
├── tham_so_RF.json      ← Bộ tham số tốt nhất tìm được ở notebook 02
├── ket_qua_them.json    ← Top-2, top-3 accuracy trên tập test
├── rf_bao_cao_theo_lop.csv, so_sanh_4_chi_so.csv  ← Bảng kết quả cho trang "Về hệ thống"
├── anh/                 ← (tuỳ chọn) ẢNH THẬT: hero.jpg, rice.jpg, banana.jpg... xem Phần 6B
├── tai_anh.py           ← (tuỳ chọn) tải ảnh từ Wikipedia vào anh/
├── .streamlit/config.toml ← Màu giao diện. Thư mục ẩn, đừng xoá.
├── requirements.txt     ← Thư viện cần cài (streamlit, numpy, pandas)
└── HUONG_DAN.md         ← File này
```

Quy tắc quan trọng nhất: **tất cả file `.py`, `train.csv`, `tham_so_RF.json` phải nằm CÙNG MỘT THƯ MỤC**. Đừng tách ra.
Thiếu các file `.csv` phụ hoặc thư mục `anh/` thì web vẫn chạy (chỉ thiếu biểu đồ hoặc hiện biểu tượng thay ảnh).

---

## PHẦN 1. Cài Python (làm một lần)

1. Vào https://www.python.org/downloads/ và bấm **Download Python 3.12** (hoặc 3.11, 3.13 đều được).
2. Mở file vừa tải. **Ở màn hình đầu tiên, TICK vào ô "Add python.exe to PATH"** (ở dưới cùng). Bước này hay bị bỏ sót nhất và gây lỗi "python is not recognized".
3. Bấm **Install Now**, chờ xong, bấm Close.
4. Kiểm tra: bấm phím Windows, gõ `cmd`, Enter. Trong cửa sổ đen gõ:

```
python --version
```

Thấy `Python 3.12.x` là thành công. Nếu báo "not recognized": cài lại Python và nhớ tick ô PATH ở bước 2.

*(Mac: dùng `python3 --version`; Linux thường đã có sẵn.)*

---

## PHẦN 2. Chuẩn bị thư mục

1. Giải nén file `web.zip` (chuột phải → Extract All).
2. Đặt thư mục `web` ở nơi dễ nhớ, ví dụ `D:\DoAn\web`. **Đường dẫn nên không dấu, không khoảng trắng.**

---

## PHẦN 3. Mở cửa sổ lệnh ngay trong thư mục `web`

Cách dễ nhất:
1. Mở thư mục `web` trong File Explorer.
2. Bấm vào **thanh địa chỉ** phía trên (chỗ hiện `D:\DoAn\web`), xoá hết, gõ `cmd`, nhấn Enter.
3. Một cửa sổ đen hiện ra với dòng đầu dạng `D:\DoAn\web>`. Mọi lệnh bên dưới gõ vào cửa sổ này.

Kiểm tra đúng thư mục chưa, gõ `dir`. Phải thấy `app.py`, `thuat_toan.py`, `train.csv`... trong danh sách.

---

## PHẦN 4. Tạo môi trường ảo và cài thư viện (làm một lần)

"Môi trường ảo" là một hộp riêng để cài thư viện, tránh làm rối Python của máy.

Gõ lần lượt từng dòng (mỗi dòng xong nhấn Enter, chờ chạy xong rồi mới gõ dòng sau):

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

- Sau dòng 2, đầu dòng lệnh có thêm chữ `(venv)`. Đó là dấu hiệu đã vào môi trường ảo.
- Dòng 3 tải và cài streamlit, numpy, pandas; mất 1–3 phút, cần có mạng.

*(Mac/Linux: dòng 2 là `source venv/bin/activate`.)*

**Nếu dòng 2 báo lỗi đỏ về "execution policy" (khi dùng PowerShell):** đổi sang dùng `cmd` như bước ở Phần 3, hoặc gõ `Set-ExecutionPolicy -Scope Process Bypass` rồi chạy lại dòng 2.

---

## PHẦN 5. Chạy web

Vẫn trong cửa sổ có `(venv)`, gõ:

```
streamlit run app.py
```

- Lần đầu Streamlit có thể hỏi email, **bấm Enter để bỏ qua**.
- Trình duyệt tự mở trang `http://localhost:8501`. Nếu không tự mở, copy địa chỉ này dán vào trình duyệt.
- Lần đầu mở web, màn hình hiện dòng "Đang huấn luyện Random Forest" khoảng 3–5 giây. Sau đó mọi thao tác gần như tức thì (nhờ bộ nhớ đệm).

**Tắt web:** quay lại cửa sổ đen, nhấn `Ctrl + C`.

**Lần sau muốn chạy lại** (không cần cài lại): mở cmd trong thư mục `web` (Phần 3), rồi gõ:

```
venv\Scripts\activate
streamlit run app.py
```

Nếu gõ `streamlit` mà báo "not recognized", dùng: `python -m streamlit run app.py`.

---

## PHẦN 6. Các trang của website

Menu trên cùng có 5 trang:

1. **Trang chủ**: banner lớn, 4 ô số liệu (2.200 mẫu, 22 cây, 98,9% đáp án đúng nằm trong 3 gợi ý đầu...), 3 bước sử dụng,
   4 cây nổi bật (bấm là sang cẩm nang), khối số liệu độ tin cậy, hỏi đáp ngắn và nút kêu gọi "Thử ngay".
2. **Gợi ý cây trồng**: bên trái nhập N, P, K, pH (có ô "Điền nhanh" điền sẵn đất điển hình của một cây). Bên phải hiện cây hạng 1
   kèm độ tin cậy (xanh cao từ 70%, cam 50–70%, đỏ dưới 50%), hạng 2, 3, và nút **Xem cách trồng**. Phía dưới có biểu đồ xác suất,
   biểu đồ so sánh đất với đất điển hình của cây, và **lời khuyên cải tạo đất** (ví dụ: pH thấp thì bón vôi, K thấp thì bổ sung kali).
   Kết quả tự cập nhật, không có nút "Dự đoán".
3. **Thư viện cây**: lưới thẻ 22 cây, lọc theo nhóm (Ngũ cốc, Đậu đỗ, Cây ăn quả, Dưa, Cây công nghiệp) và tìm theo tên.
4. **Cẩm nang trồng**: mỗi cây có mùa vụ, nhiệt độ, nước, đất nền, bảng đất phù hợp lấy từ dữ liệu, so sánh với đất của bạn,
   5 bước trồng, sâu bệnh thường gặp và mẹo.
5. **Về hệ thống**: cách Random Forest hoạt động, độ chính xác, so sánh với Decision Tree, F1 từng cây, hạn chế và hỏi đáp.

**Luồng của một khách hàng thật:** vào Trang chủ → Gợi ý (nhập đất) → thấy cây phù hợp → bấm "Xem cách trồng" → đọc cẩm nang,
trong đó có lời khuyên chỉnh đất theo đúng chỉ số vừa nhập.

**Ví dụ minh hoạ vì sao hiện nhiều gợi ý:** chọn ô "Điền nhanh" là **Lúa**; đất điển hình của lúa ra **Đay** hạng 1 và Lúa hạng 2,
vì hai cây này có đất rất giống nhau. Ở 22 mẫu điển hình, mô hình đoán trúng 18 cây. Còn trên tập test, đáp án đúng nằm trong 3 gợi ý đầu tới 98,9%.

---

## PHẦN 6B. Thêm ảnh thật

Khi chưa có ảnh, web hiện biểu tượng và nền xanh. Khi có ảnh trong thư mục `anh/`, web **tự dùng**. Web tự thu nhỏ ảnh nên không cần nén trước.

Tên file ảnh (đuôi `.jpg`, `.jpeg`, `.png` hoặc `.webp`):

| Tên file | Dùng ở đâu | Gợi ý ảnh |
|---|---|---|
| `hero.jpg` | Nền banner Trang chủ | Cánh đồng, vườn cây, ngang, khoảng 1600×900, vùng bên trái ít chi tiết vì có chữ |
| `dong_ruong.jpg` | Nền khối "Sẵn sàng chọn cây..." cuối Trang chủ | Người nông dân, đồng ruộng |
| `<tên cây>.jpg` | Thẻ cây, kết quả gợi ý, banner cẩm nang | Ảnh cây hoặc quả, ngang tỉ lệ khoảng 16:10 |

Tên cây (22 tên, viết thường, tiếng Anh):

```
rice  maize  chickpea  kidneybeans  pigeonpeas  mothbeans  mungbean  blackgram  lentil  pomegranate  banana
mango  grapes  watermelon  muskmelon  apple  orange  papaya  coconut  cotton  jute  coffee
```

Ví dụ: `anh/banana.jpg`, `anh/rice.png`, `anh/hero.jpg`.

**Tự động:** `python tai_anh.py` tải ảnh 22 cây từ Wikipedia (cần có mạng, ghi nguồn vào `anh/NGUON.txt`). Không tải `hero.jpg`.
Sau khi thêm ảnh, nhấn Ctrl + C rồi chạy lại `streamlit run app.py`.

**Bản quyền:** dùng ảnh của chính nhóm hoặc ảnh miễn phí (Unsplash, Pexels, Wikimedia Commons), ghi nguồn vào tài liệu tham khảo.
Khi đưa lên GitHub, nhớ tải cả thư mục `anh`.

---

## PHẦN 7. Hiểu code (để trả lời vấn đáp)

| File | Làm gì |
|---|---|
| `app.py` | `st.navigation(..., position="top")` tạo menu trên cùng; mỗi `st.Page(...)` là một trang. |
| `du_lieu_web.py` | `nap_du_lieu()` đọc dữ liệu (có `@st.cache_data` nên chỉ đọc một lần); `lay_mo_hinh()` huấn luyện `MyRandomForest` với tham số trong json (có `@st.cache_resource` nên chỉ huấn luyện một lần); `danh_gia_dat()` so đất với khoảng điển hình. |
| `trang_goi_y.py` | Gọi `du_doan_mau_moi` trong `thuat_toan.py` để lấy top cây, xác suất và cảnh báo. |
| `giao_dien.py` | Đoạn CSS trang trí và các hàm vẽ biểu đồ (thư viện altair, đi kèm Streamlit). |
| `noi_dung_cay.py` | Chỉ chứa chữ: bảng `CAY` và `LOI_KHUYEN_DAT`. |

**Vì sao cần cache?** Streamlit chạy lại mã mỗi lần người dùng bấm gì đó. Không cache thì mỗi lần bấm lại đọc dữ liệu và huấn luyện lại (3 giây).

**Khoảng "đất điển hình" lấy ở đâu?** Từ `train.csv`: với mỗi cây, lấy phân vị 10% đến 90% của từng chỉ số. Chỉ số của người dùng nằm ngoài khoảng này thì web đưa lời khuyên.
Đây là **quy tắc dựa trên dữ liệu**, không phải mô hình học máy; lời khuyên (bón vôi, bổ sung kali...) là kiến thức nông học phổ biến, không đưa liều lượng vì dữ liệu không nêu đơn vị đo.

**Câu hỏi thầy có thể hỏi:**
- *Web dự đoán thế nào?* Mỗi trong 100 cây cho vector xác suất 22 loại cây, mô hình lấy trung bình rồi chọn các cây cao nhất.
- *Vì sao hiện top-3?* Top-1 đúng 79,1% nhưng đáp án đúng nằm trong top-3 tới 98,9%; nhiều cây có đất giống nhau.
- *Nội dung cẩm nang lấy ở đâu?* Tổng hợp từ kiến thức nông học phổ biến, mang tính tham khảo. Nhóm nên đối chiếu thêm và ghi nguồn (ví dụ tài liệu khuyến nông, FAO).
- *Web có dùng tập test không?* Không. Web chỉ huấn luyện bằng `train.csv`. Tập test chỉ dùng một lần để báo cáo độ chính xác.
- *Mô hình có học thêm từ dữ liệu người dùng không?* Không. Mô hình cố định và dữ liệu nhập không được lưu lại.

---

## PHẦN 8. Tuỳ chỉnh thường gặp

| Muốn | Sửa ở đâu |
|---|---|
| Đổi tên website ("Đất & Cây") | `content:` trong `giao_dien.py` (dòng `header[data-testid="stHeader"]::before`) và `chan_trang()` |
| Đổi câu chữ banner | `trang_chu.py`, khối `hero-tieu-de` |
| Đổi cây nổi bật trên Trang chủ | Danh sách `NOI_BAT` trong `trang_chu.py` |
| Sửa/bổ sung nội dung trồng trọt | `noi_dung_cay.py` |
| Đổi màu chủ đạo | Các mã màu trong `giao_dien.py` (`XANH_DAM`, `XANH`, `CAM`) và `.streamlit/config.toml` |
| Đổi giá trị mặc định ô nhập | `MAC_DINH` trong `giao_dien.py` |
| Thêm tên nhóm, thành viên | `chan_trang()` trong `giao_dien.py` hoặc cuối `trang_he_thong.py` |

Sau khi sửa và lưu, trang web hiện nút **Rerun** ở góc phải; bấm vào là thấy thay đổi.

---

## PHẦN 9. Đưa web lên mạng (Streamlit Community Cloud, miễn phí)

1. Tạo tài khoản GitHub (https://github.com), tạo kho **Public** mới, ví dụ `dat-va-cay`.
2. Bấm **uploading an existing file**, kéo thả **toàn bộ nội dung thư mục `web`** vào (gồm cả thư mục `anh` và thư mục ẩn `.streamlit`;
   nếu không thấy thư mục ẩn, vào tab View của File Explorer và bật **Hidden items**). **Không** tải thư mục `venv`. Bấm **Commit changes**.
3. Vào https://share.streamlit.io, đăng nhập bằng GitHub, bấm **Create app**, chọn kho, nhánh `main`, **Main file path: `app.py`**, bấm **Deploy**.
4. Chờ 2–5 phút, nhận link dạng `https://ten-app.streamlit.app`.

Lưu ý: app miễn phí tự "ngủ" khi lâu không ai dùng; mở link trước buổi bảo vệ 5 phút để nó dậy, và luôn chuẩn bị cách chạy `localhost` trên laptop phòng khi mất mạng.

---

## PHẦN 10. Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách sửa |
|---|---|---|
| `'python' is not recognized` | Quên tick "Add to PATH" | Cài lại Python, tick ô PATH |
| `'streamlit' is not recognized` | Chưa vào venv hoặc chưa cài | Chạy `venv\Scripts\activate` rồi `pip install -r requirements.txt`; hoặc dùng `python -m streamlit run app.py` |
| `ModuleNotFoundError: No module named 'thuat_toan'` | Cmd không mở trong thư mục `web`, hoặc thiếu file | Làm lại Phần 3, gõ `dir` kiểm tra có `thuat_toan.py` |
| `FileNotFoundError: train.csv` | Thiếu `train.csv` hoặc để sai thư mục | Đặt `train.csv` cùng chỗ với `app.py` |
| `ModuleNotFoundError: No module named 'streamlit'` | Chưa vào venv | `venv\Scripts\activate` |
| Cổng 8501 đã bị dùng | Đang chạy một web khác | Tắt cửa sổ cũ, hoặc `streamlit run app.py --server.port 8502` |
| Trang trắng / không mở trình duyệt | Trình duyệt chặn | Tự mở `http://localhost:8501` |
| Lỗi thiếu module trên Streamlit Cloud | `requirements.txt` thiếu hoặc không được tải lên | Kiểm tra có file này trong GitHub |
| Menu trên cùng không hiện, lỗi `position` | Streamlit cũ | `pip install -U streamlit` (cần từ 1.46 trở lên) |
| Ảnh không hiện | Sai tên file hoặc sai thư mục | Đúng dạng `anh/banana.jpg`, tên viết thường, tiếng Anh |
| Kết quả khác notebook | Sửa `tham_so_RF.json` hoặc dùng `train.csv` khác | Dùng lại đúng file gốc |

---

## PHẦN 11. Tóm tắt 6 lệnh cần nhớ

```
cd D:\DoAn\web                       (hoặc mở cmd từ thanh địa chỉ)
python -m venv venv                  (một lần)
venv\Scripts\activate                (mỗi lần mở cmd mới)
pip install -r requirements.txt      (một lần)
streamlit run app.py                 (mỗi lần muốn chạy)
Ctrl + C                             (tắt web)
```
