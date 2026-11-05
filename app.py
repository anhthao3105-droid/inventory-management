"""
Website "Đất & Cây": hỗ trợ lựa chọn cây trồng dựa trên điều kiện đất (N, P, K, pH).
Mô hình: Random Forest TỰ CÀI ĐẶT (file thuat_toan.py), không dùng sklearn.

Chạy:  streamlit run app.py

File này chỉ lo khung website: menu trên cùng, giao diện chung và chân trang.
Mỗi trang nằm ở một file riêng: trang_chu.py, trang_goi_y.py, trang_thu_vien.py, trang_cam_nang.py, trang_he_thong.py
"""
import streamlit as st

st.set_page_config(page_title="Đất & Cây · Gợi ý cây trồng theo đất", page_icon="🌱", layout="wide")

import dieu_huong
import giao_dien
import trang_cam_nang
import trang_chu
import trang_goi_y
import trang_he_thong
import trang_thu_vien
from du_lieu_web import lay_mo_hinh, THU_TU_CHI_SO

giao_dien.chen_css()
lay_mo_hinh(tuple(THU_TU_CHI_SO))        # huấn luyện sẵn mô hình 4 chỉ số ngay khi mở web

# Danh sách trang (menu trên cùng)
dieu_huong.PAGES.update({
    "chu": st.Page(trang_chu.hien_thi, title="Trang chủ", icon="🏡", default=True),
    "goi_y": st.Page(trang_goi_y.hien_thi, title="Gợi ý cây trồng", icon="🔎", url_path="goi-y"),
    "thu_vien": st.Page(trang_thu_vien.hien_thi, title="Thư viện cây", icon="📚", url_path="thu-vien"),
    "cam_nang": st.Page(trang_cam_nang.hien_thi, title="Cẩm nang trồng", icon="🌾", url_path="cam-nang"),
    "he_thong": st.Page(trang_he_thong.hien_thi, title="Về hệ thống", icon="🧠", url_path="he-thong"),
})

try:
    trang = st.navigation(list(dieu_huong.PAGES.values()), position="top")
except TypeError:                          # bản Streamlit cũ chưa có menu trên cùng
    trang = st.navigation(list(dieu_huong.PAGES.values()))
trang.run()

giao_dien.chan_trang()
