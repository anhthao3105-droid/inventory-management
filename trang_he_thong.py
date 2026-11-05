"""Trang Về hệ thống: cách hoạt động, độ chính xác, so sánh thuật toán, hạn chế và hỏi đáp."""
import altair as alt
import pandas as pd
import streamlit as st

from du_lieu_web import nap_du_lieu, nap_bang_phu, lay_mo_hinh, THU_TU_CHI_SO
from giao_dien import CAM, XANH, icon, ten_vn, tieu_de_muc, ve


def hien_thi():
    train, cau_hinh, them = nap_du_lieu()
    tham_so = cau_hinh["tham_so"]

    st.markdown("## 🧠 Về hệ thống")
    st.caption("Dành cho người muốn biết hệ thống hoạt động và đáng tin đến đâu.")

    # ---------------- cách hoạt động
    tieu_de_muc("Cách hoạt động", "Random Forest: 100 cây quyết định cùng bỏ phiếu")
    cot = st.columns(4, gap="medium")
    buoc = [
        ("1", "Nhập", "Người dùng nhập N, P, K, pH của đất."),
        ("2", "100 cây cùng xét", f"Mỗi cây được huấn luyện trên một mẫu bootstrap khác nhau, mỗi lần tách nút chỉ nhìn {tham_so['max_features']} chỉ số ngẫu nhiên."),
        ("3", "Bỏ phiếu mềm", "Mỗi cây cho xác suất của 22 loại cây; rừng lấy trung bình các xác suất đó."),
        ("4", "Gợi ý", "Chọn các cây có xác suất cao nhất, kèm cảnh báo nếu đất nằm ngoài miền dữ liệu hoặc độ tin cậy thấp."),
    ]
    for hop, (so, tieu_de, nd) in zip(cot, buoc):
        hop.markdown(f'<div class="the"><div class="so-tt">{so}</div><h4>{tieu_de}</h4><div>{nd}</div></div>',
                     unsafe_allow_html=True)

    # ---------------- độ chính xác
    tieu_de_muc("Độ chính xác", "Kết quả trên 440 mẫu chưa từng dùng khi huấn luyện")
    m = st.columns(5)
    so_lieu = [
        (cau_hinh["accuracy_test"], "Đúng ngay gợi ý số 1"),
        (them.get("top2", 0), "Đúng trong 2 gợi ý đầu"),
        (them.get("top3", 0), "Đúng trong 3 gợi ý đầu"),
        (cau_hinh["f1_macro_test"], "Macro F1"),
        (cau_hinh["oob_accuracy"], "OOB accuracy"),
    ]
    for hop, (v, nhan) in zip(m, so_lieu):
        hop.markdown(
                     f'<div class="so"><div class="v">{f"{v:.1%}".replace(".", ",")}</div><div class="l">{nhan}</div></div>',
                     unsafe_allow_html=True)
    st.write("")
    st.write(
        f"Mô hình gồm **{tham_so['n_estimators']} cây**, tiêu chí **{tham_so['criterion']}**, độ sâu tối đa **{tham_so['max_depth']}**, "
        f"bỏ phiếu **{tham_so['vote']}**, huấn luyện trên **{len(train)}** mẫu. Các tham số được chọn bằng kiểm định chéo 5 lần trên tập huấn luyện, "
        "tập test chỉ dùng một lần để báo cáo."
    )

    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("##### Chỉ số nào quan trọng nhất?")
        mh4 = lay_mo_hinh(tuple(THU_TU_CHI_SO))
        qt = pd.DataFrame({"Chỉ số": THU_TU_CHI_SO, "Độ quan trọng": mh4.feature_importances_})
        ve(
            alt.Chart(qt).mark_bar(cornerRadiusEnd=6, color=XANH)
            .encode(x=alt.X("Độ quan trọng:Q", axis=alt.Axis(format="%", title=None)),
                    y=alt.Y("Chỉ số:N", sort="-x", axis=alt.Axis(title=None, labelFontSize=14)),
                    tooltip=["Chỉ số", alt.Tooltip("Độ quan trọng:Q", format=".1%")])
            .properties(height=170)
        )
        st.caption("Tính theo mức giảm tạp chất (MDI), trung bình trên các cây.")
    with b:
        so_sanh = nap_bang_phu("so_sanh_4_chi_so.csv")
        st.markdown("##### Random Forest so với Decision Tree")
        if so_sanh is not None:
            so_sanh = so_sanh.rename(columns={so_sanh.columns[0]: "Chỉ số"})
            st.dataframe(so_sanh.round(4), hide_index=True)
            st.caption("Trên tập test RF nhỉnh hơn khoảng 3 điểm phần trăm; chênh lệch này chưa đạt ý nghĩa thống kê (McNemar p ≈ 0,096).")

    theo_lop = nap_bang_phu("rf_bao_cao_theo_lop.csv")
    if theo_lop is not None:
        st.markdown("##### F1 theo từng loại cây (cây nào dễ nhầm?)")
        theo_lop = theo_lop.copy()
        theo_lop["Cây"] = theo_lop["Lớp"].map(lambda x: f"{icon(x)} {ten_vn(x)}")
        ve(
            alt.Chart(theo_lop).mark_bar(cornerRadiusEnd=4)
            .encode(x=alt.X("Cây:N", sort="-y", axis=alt.Axis(title=None, labelAngle=-45)),
                    y=alt.Y("F1:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(title="F1")),
                    color=alt.condition(alt.datum.F1 < 0.7, alt.value(CAM), alt.value(XANH)),
                    tooltip=["Cây", "Precision", "Recall", "F1", "Số mẫu"])
            .properties(height=280)
        )
        st.caption("Cột cam: F1 dưới 0,7, thường là các cặp cây có đất giống nhau.")

    # ---------------- hạn chế
    tieu_de_muc("Minh bạch", "Hạn chế cần biết")
    st.markdown(
        """
- Chỉ chọn được trong **22 loại cây** có trong dữ liệu.
- Chỉ dùng **4 chỉ số đất**, không có khí hậu, lượng mưa, nhiệt độ, nên độ chính xác ngay gợi ý số 1 chỉ khoảng 80%.
- Dữ liệu có dấu hiệu là **dữ liệu mô phỏng**, chưa kiểm chứng ngoài thực địa; đơn vị đo của N, P, K không được nêu.
- Một số cặp cây có đất rất giống nhau (dưa lê và dưa hấu, nho và táo, lúa và đay), vì vậy hệ thống đưa nhiều gợi ý.
- Nội dung cẩm nang là kiến thức nông học phổ biến, mang tính tham khảo, không thay thế tư vấn của kỹ sư nông nghiệp.
"""
    )

    # ---------------- hỏi đáp
    tieu_de_muc("Hỏi đáp", "Câu hỏi thường gặp")
    hoi_dap = [
        ("Vì sao chọn Random Forest?", "Random Forest cho xác suất mượt hơn một cây quyết định, nên danh sách gợi ý top-3 đáng tin hơn; "
         "kết quả cũng tốt hơn nhẹ và ít quá khớp hơn. Decision Tree vẫn được dùng làm mốc so sánh vì dễ đọc luật."),
        ("Hệ thống có học thêm từ dữ liệu tôi nhập không?", "Không. Mô hình cố định, chỉ dùng để dự đoán; dữ liệu bạn nhập không được lưu lại."),
        ("Vì sao cùng một đất mà có lúc ra cây khác nhau?", "Mô hình luôn cho kết quả giống nhau với cùng dữ liệu nhập. "
         "Nếu bạn bỏ bớt chỉ số thì hệ thống dùng một mô hình khác (huấn luyện với ít chỉ số hơn) nên kết quả có thể khác."),
        ("Tôi nhập giá trị ngoài khoảng thì sao?", "Hệ thống vẫn trả kết quả nhưng kèm cảnh báo, vì cây quyết định không ngoại suy được ngoài miền đã học."),
    ]
    for q, a_ in hoi_dap:
        with st.expander(q):
            st.write(a_)
