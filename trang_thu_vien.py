"""Thư viện cây trồng: lưới thẻ 22 cây, lọc theo nhóm và tìm kiếm."""
import streamlit as st

import dieu_huong
from giao_dien import anh_the, nut, rut_gon, ten_vn, tieu_de_muc
from noi_dung_cay import CAY, NHOM_CAY


def hien_thi():
    st.markdown("## 📚 Thư viện cây trồng")
    st.caption("22 loại cây trong hệ thống. Bấm vào từng cây để xem cẩm nang trồng chi tiết.")

    c1, c2 = st.columns([1, 2.2])
    tim = c1.text_input("Tìm theo tên", placeholder="Ví dụ: chuối, banana...")
    nhom = c2.radio("Nhóm cây", ["Tất cả"] + NHOM_CAY, horizontal=True)

    danh_sach = []
    for en, d in CAY.items():
        if nhom != "Tất cả" and d["nhom"] != nhom:
            continue
        if tim and tim.strip().lower() not in f"{ten_vn(en)} {en} {d['khoa_hoc']}".lower():
            continue
        danh_sach.append(en)
    danh_sach.sort(key=lambda x: ten_vn(x))

    if not danh_sach:
        st.info("Không tìm thấy cây phù hợp. Thử bỏ bớt bộ lọc.")
        return
    st.write(f"Tìm thấy **{len(danh_sach)}** cây.")

    so_cot = 4
    for i in range(0, len(danh_sach), so_cot):
        cot = st.columns(so_cot, gap="medium")
        for hop, cay in zip(cot, danh_sach[i:i + so_cot]):
            with hop:
                d = CAY[cay]
                st.markdown(
                    f"""<div class="the-cay">{anh_the(cay, 150)}<div class="noi-dung">
<div class="ten">{ten_vn(cay)}</div><div class="en">{d['khoa_hoc']}</div>
<span class="nhom-tag">{d['nhom']}</span>
<div class="thong-tin">⏱ {rut_gon(d['thoi_gian'])}<br>🌡 {rut_gon(d['nhiet_do'])}</div></div></div>""",
                    unsafe_allow_html=True,
                )
                if nut("Xem cách trồng →", key=f"tv_{cay}"):
                    st.session_state["cay_xem"] = cay
                    st.switch_page(dieu_huong.PAGES["cam_nang"])
        st.write("")
