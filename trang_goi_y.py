"""Trang Gợi ý cây trồng: nhập N, P, K, pH rồi nhận top cây kèm biểu đồ và lời khuyên cải tạo đất."""
import streamlit as st

import dieu_huong
from du_lieu_web import nap_du_lieu, thong_ke_cay, goi_y, danh_gia_dat, NHAN, THU_TU_CHI_SO
from giao_dien import (MAC_DINH, GIOI_HAN, MO_TA, anh_the, bieu_do_so_sanh, bieu_do_xac_suat, icon,
                       nut, ten_vn, ve)
from noi_dung_cay import LOI_KHUYEN_DAT


def khoi_tao_trang_thai():
    """Streamlit xoá giá trị ô nhập khi rời trang, nên ta lưu bản sao ở khoá 'luu_dat' rồi nạp lại khi quay về."""
    luu = st.session_state.get("luu_dat", {})
    for c in THU_TU_CHI_SO:
        st.session_state.setdefault(f"in_{c}", float(luu.get(c, MAC_DINH[c])))
    st.session_state.setdefault("chon_chi_so", list(st.session_state.get("luu_cot", THU_TU_CHI_SO)))


def hien_thi():
    train, cau_hinh, them = nap_du_lieu()
    tk = thong_ke_cay()
    khoi_tao_trang_thai()

    def dien_mau_nhanh():
        """Chọn một loại cây ở ô 'Điền nhanh' thì gán giá trị trung vị của cây đó vào các ô nhập."""
        cay = st.session_state["mau_nhanh"]
        if cay is not None:
            for c in THU_TU_CHI_SO:
                st.session_state[f"in_{c}"] = float(tk["med"].loc[cay, c])

    st.markdown("## 🔎 Gợi ý cây trồng theo đất")
    st.caption("Kết quả tự cập nhật mỗi khi bạn thay đổi giá trị.")
    cot_trai, cot_phai = st.columns([1, 1.35], gap="large")

    # ---------------- cột trái: nhập liệu
    with cot_trai:
        st.markdown('<div class="tieude">① Nhập chỉ số đất</div>', unsafe_allow_html=True)
        st.selectbox(
            "Điền nhanh bằng đất điển hình của một loại cây (tuỳ chọn)",
            options=[None] + sorted(train[NHAN].unique()),
            format_func=lambda x: "— Tự nhập —" if x is None else f"{icon(x)} {ten_vn(x)}",
            key="mau_nhanh", on_change=dien_mau_nhanh,
        )
        st.caption("Lưu ý: một số cây có đất rất giống nhau (lúa/đay, nho/táo...), nên điền mẫu cây này vẫn có thể ra cây kia.")
        with st.expander("Tuỳ chọn nâng cao: bỏ bớt chỉ số"):
            st.multiselect("Chỉ số dùng để dự đoán (nên dùng đủ cả 4)", THU_TU_CHI_SO, key="chon_chi_so")
        chon = st.session_state["chon_chi_so"]

        mau = {}
        for c in chon:
            lo, hi = GIOI_HAN[c]
            mau[c] = st.number_input(
                f"{c} · {MO_TA[c]}", min_value=lo, max_value=hi,
                step=0.1 if c == "pH" else 1.0, format="%.2f" if c == "pH" else "%.1f",
                key=f"in_{c}",
                help=f"Khoảng trong dữ liệu huấn luyện: {train[c].min():.1f} – {train[c].max():.1f}",
            )

    # ---------------- cột phải: kết quả
    with cot_phai:
        if not chon:
            st.error("Hãy chọn ít nhất một chỉ số đất (mở mục 'Tuỳ chọn nâng cao').")
            return
        cot, kq = goi_y(mau, top=5)
        st.session_state["luu_dat"] = {**st.session_state.get("luu_dat", {}), **mau}
        st.session_state["luu_cot"] = list(chon)
        st.session_state["da_nhap"] = True

        (cay1, xs1) = kq["gợi ý"][0]
        if xs1 >= 0.7:
            nhan, lop = "Độ tin cậy cao", "cao"
        elif xs1 >= 0.5:
            nhan, lop = "Độ tin cậy trung bình", "tb"
        else:
            nhan, lop = "Độ tin cậy thấp", "thap"

        st.markdown(
            f"""<div class="kq">{anh_the(cay1, 190)}
<div class="nho">Gợi ý số 1</div><div class="ten">{ten_vn(cay1)}</div><div class="en">{cay1}</div>
<span class="badge {lop}">{xs1:.0%} · {nhan}</span></div>""",
            unsafe_allow_html=True,
        )
        if nut(f"📖 Xem cách trồng {ten_vn(cay1).lower()}", key="xem_1", type="primary"):
            st.session_state["cay_xem"] = cay1
            st.switch_page(dieu_huong.PAGES["cam_nang"])

        c2, c3 = st.columns(2)
        for hop, hang, (cay, xs) in zip((c2, c3), (2, 3), kq["gợi ý"][1:3]):
            with hop:
                st.markdown(
                    f"""<div class="mini"><div class="hang">Hạng {hang}</div>{anh_the(cay, 90)}
<div class="ten">{ten_vn(cay)}</div><div class="pt">{xs:.0%}</div></div>""",
                    unsafe_allow_html=True,
                )
                if nut("Xem cách trồng", key=f"xem_{hang}"):
                    st.session_state["cay_xem"] = cay
                    st.switch_page(dieu_huong.PAGES["cam_nang"])

        for canh_bao in kq["cảnh báo"]:
            st.warning(canh_bao)

    # ---------------- phía dưới: biểu đồ và lời khuyên
    st.write("")
    bd_trai, bd_phai = st.columns(2, gap="large")
    with bd_trai:
        st.markdown("##### Xác suất của 5 cây đứng đầu")
        ve(bieu_do_xac_suat(kq["gợi ý"]))
    with bd_phai:
        st.markdown(f"##### Đất của bạn so với đất điển hình của {ten_vn(cay1)}")
        ve(bieu_do_so_sanh(cay1, mau))
        st.caption("Dải xanh nhạt: khoảng điển hình (10%–90% mẫu) của cây này · vạch đậm: trung vị · "
                   "hình thoi: giá trị của bạn (cam = trong khoảng, đỏ = ngoài khoảng).")

    st.markdown(f"##### Đất của bạn cần điều chỉnh gì để trồng {ten_vn(cay1).lower()}?")
    danh_gia = danh_gia_dat(cay1, mau)
    ngoai = [d for d in danh_gia if d["trang_thai"] != "phu_hop"]
    if not ngoai:
        st.success("Các chỉ số bạn nhập đều nằm trong khoảng điển hình của cây này, đất đã khá phù hợp.")
    for d in ngoai:
        st.markdown(
            f'<div class="loi-khuyen {d["trang_thai"]}"><b>{d["chi_so"]} = {d["gia_tri"]:g}</b> '
            f'(khoảng điển hình {d["lo"]:.1f} – {d["hi"]:.1f}). {LOI_KHUYEN_DAT[d["chi_so"]][d["trang_thai"]]}</div>',
            unsafe_allow_html=True,
        )
    st.caption(f"Mô hình đang dùng: {kq['mô hình dùng']} · Chỉ mang tính tham khảo; liều lượng phân bón nên dựa trên phân tích đất thực tế.")
