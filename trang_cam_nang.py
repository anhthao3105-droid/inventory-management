"""Cẩm nang trồng trọt chi tiết cho từng cây, kết hợp số liệu đất từ dữ liệu và đất của người dùng (nếu đã nhập)."""
import streamlit as st

import dieu_huong
from du_lieu_web import thong_ke_cay, danh_gia_dat, THU_TU_CHI_SO
from giao_dien import bieu_do_so_sanh, doc_anh, icon, rut_gon, ten_vn, ve
from noi_dung_cay import CAY, LOI_KHUYEN_DAT


def hien_thi():
    ds = sorted(CAY, key=lambda x: ten_vn(x))
    mac = st.session_state.get("cay_xem", "rice")
    cay = st.selectbox("Chọn loại cây", ds, index=ds.index(mac) if mac in ds else 0,
                       format_func=lambda x: f"{icon(x)} {ten_vn(x)}")
    st.session_state["cay_xem"] = cay
    d = CAY[cay]
    tk = thong_ke_cay()

    # ---------------- banner của cây (ảnh nền riêng)
    uri = doc_anh(cay, 1400)
    nen = (f"linear-gradient(90deg, rgba(12,45,24,.9) 0%, rgba(12,45,24,.55) 60%, rgba(12,45,24,.2) 100%), url('{uri}')"
           if uri else "linear-gradient(120deg, #123524 0%, #2F6B3A 55%, #7FB069 100%)")
    st.markdown(f"<style>.st-key-cn_banner {{ background: {nen}; background-size: cover; background-position: center; "
                f"border-radius: 24px; padding: 38px 40px; min-height: 230px; }}</style>", unsafe_allow_html=True)
    with st.container(key="cn_banner"):
        st.markdown(
            f"""<div class="cn-ten">{icon(cay) if not uri else ''} {ten_vn(cay)}</div>
<div class="cn-kh">{d['khoa_hoc']} · {cay}</div>
<span class="cn-the">{d['nhom']}</span><span class="cn-the">⏱ {rut_gon(d['thoi_gian'])}</span>
<span class="cn-the">🌡 {rut_gon(d['nhiet_do'])}</span>
<p style="color:#E8F3EA;margin-top:.9rem;max-width:640px">{d['tom_tat']}</p>""",
            unsafe_allow_html=True,
        )

    # ---------------- thông số nhanh
    st.write("")
    st.markdown(f'<div class="thong-so" style="min-height:0"><div class="l">🗓 Mùa vụ (tham khảo)</div><div class="v">{d["mua_vu"]}</div></div>',
                unsafe_allow_html=True)
    st.write("")
    t = st.columns(3)
    for hop, (l, v) in zip(t, [("🌡 Nhiệt độ", d["nhiet_do"]), ("💧 Nước", d["nuoc"]), ("🌱 Đất nền", d["dat_nen"])]):
        hop.markdown(f'<div class="thong-so"><div class="l">{l}</div><div class="v">{v}</div></div>', unsafe_allow_html=True)

    # ---------------- đất
    st.markdown("### 🧪 Điều kiện đất phù hợp (theo dữ liệu)")
    cot_a, cot_b = st.columns([1, 1.2], gap="large")
    with cot_a:
        bang = {
            "Chỉ số": THU_TU_CHI_SO,
            "Thấp (10%)": [round(tk["p10"].loc[cay, c], 1) for c in THU_TU_CHI_SO],
            "Trung vị": [round(tk["med"].loc[cay, c], 1) for c in THU_TU_CHI_SO],
            "Cao (90%)": [round(tk["p90"].loc[cay, c], 1) for c in THU_TU_CHI_SO],
        }
        st.dataframe(bang, hide_index=True)
        st.caption("Khoảng từ 10% đến 90% các mẫu của cây này trong dữ liệu. Dữ liệu không nêu đơn vị đo của N, P, K.")

    with cot_b:
        mau = st.session_state.get("luu_dat") if st.session_state.get("da_nhap") else None
        if mau:
            ve(bieu_do_so_sanh(cay, mau))
            st.caption("Dải xanh: khoảng điển hình · vạch: trung vị · hình thoi: đất của bạn (cam = trong khoảng, đỏ = ngoài).")
        else:
            st.info("Bạn chưa nhập đất. Hãy vào trang Gợi ý cây trồng để so sánh đất của bạn với cây này.")
            st.page_link(dieu_huong.PAGES["goi_y"], label="Nhập chỉ số đất", icon="🔎")

    if mau:
        st.markdown(f"##### Đất của bạn cần điều chỉnh gì để trồng {ten_vn(cay).lower()}?")
        ngoai = [x for x in danh_gia_dat(cay, mau) if x["trang_thai"] != "phu_hop"]
        if not ngoai:
            st.success("Các chỉ số bạn đã nhập đều nằm trong khoảng điển hình của cây này.")
        for x in ngoai:
            st.markdown(f'<div class="loi-khuyen {x["trang_thai"]}"><b>{x["chi_so"]} = {x["gia_tri"]:g}</b> '
                        f'(khoảng điển hình {x["lo"]:.1f} – {x["hi"]:.1f}). {LOI_KHUYEN_DAT[x["chi_so"]][x["trang_thai"]]}</div>',
                        unsafe_allow_html=True)

    # ---------------- quy trình
    st.markdown("### 🌾 Quy trình trồng từ A đến Z")
    for i, (tieu_de, noi_dung) in enumerate(d["buoc"], 1):
        st.markdown(f'<div class="buoc"><span class="stt">{i}</span><b>{tieu_de}</b><br>{noi_dung}</div>',
                    unsafe_allow_html=True)

    # ---------------- sâu bệnh và mẹo
    s, m = st.columns(2, gap="large")
    with s:
        st.markdown("### 🐛 Sâu bệnh thường gặp")
        for ten, mo_ta in d["sau_benh"]:
            st.markdown(f'<div class="sau-benh"><b>{ten}</b><br>{mo_ta}</div>', unsafe_allow_html=True)
    with m:
        st.markdown("### 💡 Mẹo nhà nông")
        for meo in d["meo"]:
            st.markdown(f'<div class="meo">{meo}</div>', unsafe_allow_html=True)

    st.caption("Nội dung tổng hợp từ kiến thức nông học phổ biến, mang tính tham khảo. Mùa vụ, giống và liều lượng phân "
               "thay đổi theo vùng; hãy tham khảo thêm khuyến nông địa phương.")
