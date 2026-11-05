"""Trang chủ: banner, điểm nổi bật, cách hoạt động, cây nổi bật, số liệu, hỏi đáp ngắn, kêu gọi hành động."""
import streamlit as st

import dieu_huong
from du_lieu_web import nap_du_lieu, NHAN
from giao_dien import anh_the, nut, rut_gon, ten_vn, tieu_de_muc
from noi_dung_cay import CAY

NOI_BAT = ["rice", "coffee", "banana", "mango"]


def hien_thi():
    train, cau_hinh, them = nap_du_lieu()
    top3 = them.get("top3", 0)

    # ---------------- banner
    with st.container(key="hero"):
        st.markdown(
            """
<div class="hero-nho">Chào mừng đến với Đất &amp; Cây</div>
<h1 class="hero-tieu-de">Chọn đúng cây,<br>trúng mùa vàng</h1>
<p class="hero-mo-ta">Nhập 4 chỉ số đất (N, P, K, pH), hệ thống gợi ý loại cây phù hợp nhất
và hướng dẫn cách trồng từ chuẩn bị đất đến thu hoạch.</p>
""",
            unsafe_allow_html=True,
        )
        c1, c2, _ = st.columns([1.1, 1.3, 2.4])
        c1.page_link(dieu_huong.PAGES["goi_y"], label="Bắt đầu gợi ý", icon="🔎")
        c2.page_link(dieu_huong.PAGES["thu_vien"], label="Xem thư viện cây", icon="📚")

    # ---------------- ô tính năng
    st.write("")
    f1, f2, f3, f4 = st.columns(4)
    muc = [
        ("📊", f"{len(train) + them.get('n_test', 440):,}".replace(",", "."), "mẫu dữ liệu đất"),
        ("🌿", f"{train[NHAN].nunique()}", "loại cây trồng"),
        ("🎯", f"{top3:.1%}".replace(".", ","), "đáp án đúng nằm trong 3 gợi ý đầu"),
        ("📖", "22", "cẩm nang trồng chi tiết"),
    ]
    for hop, (bt, so, nhan) in zip((f1, f2, f3, f4), muc):
        hop.markdown(f'<div class="tinh-nang"><div class="bieu-tuong">{bt}</div><div class="gt">{so}</div>'
                     f'<div class="nhan">{nhan}</div></div>', unsafe_allow_html=True)

    # ---------------- cách hoạt động
    tieu_de_muc("Đơn giản", "Chỉ 3 bước để biết nên trồng gì",
                "Không cần kiến thức chuyên môn, chỉ cần các chỉ số trong phiếu phân tích đất")
    b1, b2, b3 = st.columns(3, gap="large")
    buoc = [
        ("1", "Nhập chỉ số đất", "Điền N (đạm), P (lân), K (kali) và pH. Thiếu chỉ số nào có thể bỏ trống, nhưng đủ 4 chỉ số sẽ chính xác hơn."),
        ("2", "Nhận gợi ý", "Random Forest gồm 100 cây quyết định cùng bỏ phiếu, trả về các loại cây phù hợp nhất kèm tỉ lệ tin cậy."),
        ("3", "Xem cách trồng", "Mỗi cây có cẩm nang riêng: mùa vụ, bón phân, tưới, sâu bệnh, thu hoạch, và lời khuyên cải tạo đất của bạn."),
    ]
    for hop, (so, tieu_de, noi_dung) in zip((b1, b2, b3), buoc):
        hop.markdown(f'<div class="the"><div class="so-tt">{so}</div><h4>{tieu_de}</h4><div>{noi_dung}</div></div>',
                     unsafe_allow_html=True)

    # ---------------- cây nổi bật
    with st.container(key="khoi_xanh"):
        tieu_de_muc("Thư viện cây trồng", "Những cây được quan tâm nhiều",
                    "Bấm vào từng cây để xem cẩm nang trồng chi tiết")
        cot = st.columns(len(NOI_BAT), gap="medium")
        for hop, cay in zip(cot, NOI_BAT):
            with hop:
                d = CAY[cay]
                st.markdown(
                    f"""<div class="the-cay">{anh_the(cay, 160)}<div class="noi-dung">
<div class="ten">{ten_vn(cay)}</div><div class="en">{d['khoa_hoc']}</div>
<span class="nhom-tag">{d['nhom']}</span>
<div class="thong-tin">⏱ {rut_gon(d['thoi_gian'])}<br>🌡 {rut_gon(d['nhiet_do'])}</div></div></div>""",
                    unsafe_allow_html=True,
                )
                if nut("Xem cách trồng →", key=f"cn_{cay}"):
                    st.session_state["cay_xem"] = cay
                    st.switch_page(dieu_huong.PAGES["cam_nang"])
        st.write("")
        st.page_link(dieu_huong.PAGES["thu_vien"], label="Xem tất cả 22 loại cây", icon="➡️")

    # ---------------- vì sao tin cậy
    with st.container(key="khoi_so"):
        tieu_de_muc("Vì sao đáng tin", "Kết quả kiểm tra trên 440 mẫu chưa từng thấy",
                    "Mô hình được cài đặt từ công thức và đánh giá nghiêm ngặt trên tập test tách riêng")
        s1, s2, s3, s4 = st.columns(4)
        so_lieu = [
            (f"{cau_hinh['accuracy_test']:.1%}".replace(".", ","), "Đúng ngay gợi ý số 1"),
            (f"{top3:.1%}".replace(".", ","), "Đúng trong 3 gợi ý đầu"),
            (f"{cau_hinh['f1_macro_test']:.1%}".replace(".", ","), "Macro F1"),
            (f"{cau_hinh['tham_so']['n_estimators']}", "Cây quyết định bỏ phiếu"),
        ]
        for hop, (v, l) in zip((s1, s2, s3, s4), so_lieu):
            hop.markdown(f'<div class="so"><div class="v">{v}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)

    # ---------------- hỏi đáp ngắn
    tieu_de_muc("Giải đáp nhanh", "Bạn có thể thắc mắc")
    with st.expander("Tôi cần những chỉ số nào để dùng hệ thống?"):
        st.write("Bốn chỉ số có trong phiếu phân tích đất: N (đạm), P (lân), K (kali) và độ pH. "
                 "Có thể bỏ bớt chỉ số ở mục nâng cao, nhưng kết quả sẽ kém chính xác hơn.")
    with st.expander("Vì sao hệ thống đưa nhiều gợi ý chứ không chỉ một?"):
        st.write("Nhiều cây có điều kiện đất rất giống nhau (lúa và đay, nho và táo...). Đáp án số 1 đúng khoảng 79% số lần, "
                 "nhưng đáp án đúng nằm trong 3 gợi ý đầu gần như luôn luôn. Vì vậy hệ thống đưa top 3 để bạn cân nhắc thêm "
                 "theo khí hậu và thị trường của mình.")
    with st.expander("Kết quả có thay thế được tư vấn của kỹ sư nông nghiệp không?"):
        st.write("Không. Hệ thống chỉ hỗ trợ tham khảo dựa trên 4 chỉ số đất, chưa tính khí hậu, nguồn nước, thị trường "
                 "và điều kiện canh tác thực tế. Hãy hỏi thêm khuyến nông địa phương trước khi quyết định.")

    # ---------------- kêu gọi hành động
    with st.container(key="cta"):
        st.markdown("## Sẵn sàng chọn cây cho mảnh đất của bạn?\n\nChỉ mất chưa đến một phút.")
        c, _ = st.columns([1, 3])
        c.page_link(dieu_huong.PAGES["goi_y"], label="Thử ngay", icon="🌱")
