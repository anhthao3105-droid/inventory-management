"""
Nạp dữ liệu, huấn luyện mô hình Random Forest (tự cài đặt) và các hàm phân tích đất.
Các trang web chỉ việc gọi các hàm trong file này.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from thuat_toan import MyRandomForest, du_doan_mau_moi, THU_TU_CHI_SO  # noqa: F401  (xuất lại cho các trang dùng)

THU_MUC = Path(__file__).parent
NHAN = "Crop"                      # tên cột nhãn trong train.csv


@st.cache_data
def nap_du_lieu():
    """Trả về (train, tham số RF, thống kê bổ sung như top-3 accuracy)."""
    train = pd.read_csv(THU_MUC / "train.csv")
    with open(THU_MUC / "tham_so_RF.json", encoding="utf-8") as f:
        cau_hinh = json.load(f)
    them = {}
    if (THU_MUC / "ket_qua_them.json").exists():
        with open(THU_MUC / "ket_qua_them.json", encoding="utf-8") as f:
            them = json.load(f)
    return train, cau_hinh, them


@st.cache_data
def thong_ke_cay():
    """Thống kê N, P, K, pH của từng loại cây từ dữ liệu huấn luyện: nhỏ nhất, p10, trung vị, p90, lớn nhất."""
    train, _, _ = nap_du_lieu()
    g = train.groupby(NHAN)[THU_TU_CHI_SO]
    return {
        "min": g.min(), "p10": g.quantile(0.10), "med": g.median(),
        "p90": g.quantile(0.90), "max": g.max(),
    }


@st.cache_data
def nap_bang_phu(ten_file):
    """Đọc các bảng kết quả phụ (nếu có) để hiển thị ở trang 'Về hệ thống'."""
    duong_dan = THU_MUC / ten_file
    if not duong_dan.exists():
        return None
    return pd.read_csv(duong_dan, encoding="utf-8-sig")


@st.cache_resource(show_spinner="Đang huấn luyện Random Forest (vài giây, chỉ làm một lần)...")
def lay_mo_hinh(cot):
    """Huấn luyện mô hình theo đúng các chỉ số đã chọn. Mỗi tổ hợp chỉ huấn luyện 1 lần (cache_resource)."""
    train, cau_hinh, _ = nap_du_lieu()
    mo_hinh = MyRandomForest(**cau_hinh["tham_so"])
    mo_hinh.fit(train[list(cot)], train[NHAN])
    return mo_hinh


def goi_y(mau, top=5):
    """Dự đoán top cây cho mẫu đất `mau` (dict chỉ số -> giá trị). Trả về kết quả của du_doan_mau_moi."""
    train, _, _ = nap_du_lieu()
    cot = tuple(c for c in THU_TU_CHI_SO if c in mau)
    return cot, du_doan_mau_moi({cot: lay_mo_hinh(cot)}, mau, train, top=top)


def danh_gia_dat(cay, mau):
    """
    So sánh đất của người dùng với khoảng điển hình (p10–p90) của cây.
    Trả về list dict: chi_so, gia_tri, lo, hi, trang_thai ('thap' | 'phu_hop' | 'cao').
    """
    tk = thong_ke_cay()
    ket_qua = []
    for c in THU_TU_CHI_SO:
        if c not in mau:
            continue
        v = float(mau[c])
        lo, hi = float(tk["p10"].loc[cay, c]), float(tk["p90"].loc[cay, c])
        tt = "thap" if v < lo else ("cao" if v > hi else "phu_hop")
        ket_qua.append({"chi_so": c, "gia_tri": v, "lo": lo, "hi": hi, "trang_thai": tt})
    return ket_qua
