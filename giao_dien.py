"""
Giao diện dùng chung: màu sắc, CSS, ảnh, biểu đồ và chân trang.
Muốn đổi màu hay kiểu chữ của cả website: sửa trong file này.
"""
import base64
import io
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from du_lieu_web import thong_ke_cay, nap_du_lieu, THU_TU_CHI_SO

THU_MUC = Path(__file__).parent
XANH_DAM, XANH, XANH_NHAT, CAM, DO = "#1F4D2E", "#2F6B3A", "#A5D6A7", "#B8612C", "#C62828"

TEN_VN = {
    "rice": "Lúa", "maize": "Ngô", "chickpea": "Đậu gà", "kidneybeans": "Đậu đỏ",
    "pigeonpeas": "Đậu triều", "mothbeans": "Đậu mồ", "mungbean": "Đậu xanh",
    "blackgram": "Đậu đen", "lentil": "Đậu lăng", "pomegranate": "Lựu",
    "banana": "Chuối", "mango": "Xoài", "grapes": "Nho", "watermelon": "Dưa hấu",
    "muskmelon": "Dưa lê", "apple": "Táo", "orange": "Cam",
    "papaya": "Đu đủ", "coconut": "Dừa", "cotton": "Bông", "jute": "Đay", "coffee": "Cà phê",
}
ICON = {
    "rice": "🌾", "maize": "🌽", "chickpea": "🫘", "kidneybeans": "🫘", "pigeonpeas": "🫛",
    "mothbeans": "🫘", "mungbean": "🫛", "blackgram": "🫘", "lentil": "🫘", "pomegranate": "🔴",
    "banana": "🍌", "mango": "🥭", "grapes": "🍇", "watermelon": "🍉", "muskmelon": "🍈",
    "apple": "🍎", "orange": "🍊", "papaya": "🧡", "coconut": "🥥", "cotton": "☁️",
    "jute": "🧵", "coffee": "☕",
}
MO_TA = {"N": "Đạm (Nitrogen)", "P": "Lân (Phosphorus)", "K": "Kali (Potassium)", "pH": "Độ chua của đất"}
MAC_DINH = {"N": 100.0, "P": 80.0, "K": 50.0, "pH": 6.0}
GIOI_HAN = {"N": (0.0, 300.0), "P": (0.0, 300.0), "K": (0.0, 400.0), "pH": (0.0, 14.0)}


def ten_vn(en):
    return TEN_VN.get(en, en)


def icon(en):
    return ICON.get(en, "🌱")


# ------------------------------------------------------------------ ảnh
@st.cache_data
def doc_anh(ten, rong=700):
    """
    Đọc ảnh trong thư mục anh/ (tên file = tên tiếng Anh của cây, ví dụ rice.jpg; hoặc hero.jpg, dong_ruong.jpg).
    Thu nhỏ về chiều rộng `rong` px để web nhẹ. Không có ảnh thì trả None.
    """
    for duoi in ("jpg", "jpeg", "png", "webp"):
        f = THU_MUC / "anh" / f"{ten}.{duoi}"
        if f.exists():
            try:
                from PIL import Image
                im = Image.open(f).convert("RGB")
                if im.width > rong:
                    im = im.resize((rong, int(im.height * rong / im.width)))
                buf = io.BytesIO()
                im.save(buf, "JPEG", quality=82)
                return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
            except Exception:       # không có Pillow hoặc ảnh lỗi: dùng nguyên file
                mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}[duoi]
                return f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode()
    return None


def anh_the(en, cao=170):
    """Khối ảnh của một loại cây: ảnh thật nếu có, không thì ô gradient kèm biểu tượng."""
    uri = doc_anh(en, 640)
    if uri:
        return f'<div class="anh-the" style="height:{cao}px;background-image:url(\'{uri}\')"></div>'
    return f'<div class="anh-the trong" style="height:{cao}px"><span>{icon(en)}</span></div>'


def ve(chart):
    """Vẽ biểu đồ altair, tương thích cả bản Streamlit cũ và mới."""
    try:
        st.altair_chart(chart, width="stretch")
    except TypeError:
        st.altair_chart(chart, use_container_width=True)


def nut(nhan, **kw):
    """st.button rộng hết ô, tương thích cả bản Streamlit cũ và mới."""
    try:
        return st.button(nhan, width="stretch", **kw)
    except TypeError:
        return st.button(nhan, use_container_width=True, **kw)


# ------------------------------------------------------------------ biểu đồ
def bieu_do_xac_suat(goi_y_top):
    top = pd.DataFrame(
        [(f"{icon(c)} {ten_vn(c)}", p, i == 0) for i, (c, p) in enumerate(goi_y_top)],
        columns=["Cây", "Xác suất", "Hạng 1"],
    )
    return (
        alt.Chart(top).mark_bar(cornerRadiusEnd=6, height=26)
        .encode(
            x=alt.X("Xác suất:Q", axis=alt.Axis(format="%", title=None), scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("Cây:N", sort=None, axis=alt.Axis(title=None, labelFontSize=13)),
            color=alt.condition(alt.datum["Hạng 1"], alt.value(XANH), alt.value(XANH_NHAT)),
            tooltip=["Cây", alt.Tooltip("Xác suất:Q", format=".1%")],
        )
        .properties(height=190)
    )


def bieu_do_so_sanh(cay, mau):
    """Mỗi chỉ số một dải: dải xanh = khoảng điển hình (p10–p90) của cây, vạch = trung vị, hình thoi = giá trị của bạn."""
    train, _, _ = nap_du_lieu()
    tk = thong_ke_cay()
    hang = []
    for c in THU_TU_CHI_SO:
        if c not in mau:
            continue
        lo, med, hi = tk["p10"].loc[cay, c], tk["med"].loc[cay, c], tk["p90"].loc[cay, c]
        v = float(mau[c])
        trong = lo <= v <= hi
        mien = [min(train[c].min(), v), max(train[c].max(), v)]
        du = pd.DataFrame({"lo": [lo], "med": [med], "hi": [hi], "ban": [v]})
        truc = alt.X("lo:Q", scale=alt.Scale(domain=mien), axis=alt.Axis(title=None, labelFontSize=10))
        thanh = alt.Chart(du).mark_bar(height=12, cornerRadius=6, color=XANH_NHAT).encode(x=truc, x2="hi:Q")
        vach = alt.Chart(du).mark_tick(color=XANH, thickness=3, size=22).encode(x=alt.X("med:Q"))
        diem = alt.Chart(du).mark_point(shape="diamond", size=220, filled=True, opacity=1,
                                        color=CAM if trong else DO).encode(x=alt.X("ban:Q"))
        hang.append((thanh + vach + diem).properties(height=46, title=alt.TitleParams(
            f"{c}  ({'trong khoảng điển hình' if trong else 'NGOÀI khoảng điển hình'})", anchor="start", fontSize=12)))
    return alt.vconcat(*hang).resolve_scale(x="independent")


# ------------------------------------------------------------------ CSS
def chen_css():
    hero = doc_anh("hero", 1600)
    nen_hero = (
        f"linear-gradient(90deg, rgba(12,45,24,.88) 0%, rgba(12,45,24,.55) 55%, rgba(12,45,24,.15) 100%), url('{hero}')"
        if hero else
        "linear-gradient(120deg, #123524 0%, #2F6B3A 55%, #7FB069 100%)"
    )
    dong = doc_anh("dong_ruong", 1600)
    nen_cta = (
        f"linear-gradient(90deg, rgba(12,45,24,.9), rgba(12,45,24,.55)), url('{dong}')"
        if dong else "linear-gradient(120deg, #1F4D2E, #2F6B3A)"
    )
    st.markdown(
        f"""
<style>
.stApp {{ background: #FBF8EF; color: #1F2A1F; }}
.block-container {{ padding-top: 4.6rem; max-width: 1180px; padding-bottom: 1rem; }}
.stAppDeployButton, #MainMenu, footer {{ display: none !important; }}

/* ---------- thanh menu trên cùng ---------- */
header[data-testid="stHeader"] {{ background: #FFFFFF; box-shadow: 0 2px 14px rgba(20,60,30,.10); }}
header[data-testid="stHeader"]::before {{ content: "🌱  Đất & Cây"; position: absolute; left: 24px; top: 50%;
    transform: translateY(-50%); font-weight: 800; font-size: 1.2rem; color: {XANH_DAM}; letter-spacing: .01em; }}

header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: 190px !important; }}

/* ---------- tiêu đề ---------- */
h1, h2, h3 {{ color: {XANH_DAM}; font-weight: 800 !important; }}
.tieu-de-muc {{ text-align: center; margin: 2.2rem 0 1.2rem 0; }}
.tieu-de-muc .nho {{ color: {CAM}; font-weight: 700; letter-spacing: .14em; font-size: .82rem; text-transform: uppercase; }}
.tieu-de-muc .lon {{ color: {XANH_DAM}; font-size: 2rem; font-weight: 800; line-height: 1.2; }}
.tieu-de-muc .mo-ta {{ color: #5A6B5A; margin-top: .3rem; }}
.tieude {{ font-size: 1.25rem; font-weight: 700; color: {XANH_DAM}; margin-bottom: .6rem; }}

/* ---------- banner đầu trang chủ ---------- */
.st-key-hero {{ background: {nen_hero}; background-size: cover; background-position: center;
    border-radius: 26px; padding: 64px 52px 44px 52px; min-height: 420px; color: #fff;
    box-shadow: 0 12px 34px rgba(20,60,30,.28); }}
.hero-nho {{ color: #F3E3C3; letter-spacing: .16em; font-size: .85rem; font-weight: 700; text-transform: uppercase; }}
.hero-tieu-de {{ color: #fff !important; font-size: 3.1rem; line-height: 1.12; font-weight: 800; margin: .4rem 0 .8rem 0; max-width: 640px; }}
.hero-mo-ta {{ color: #E8F3EA; font-size: 1.1rem; max-width: 560px; margin-bottom: 1.4rem; }}
.st-key-hero a[data-testid="stPageLink-NavLink"] {{ background: {CAM}; border-radius: 10px; padding: .55rem 1rem; justify-content: center; }}
.st-key-hero a[data-testid="stPageLink-NavLink"] p, .st-key-hero a[data-testid="stPageLink-NavLink"] span {{ color: #fff !important; font-weight: 700; }}
.st-key-hero div:nth-child(n) .stColumn:nth-child(2) a[data-testid="stPageLink-NavLink"] {{ background: #FFFFFF; }}
.st-key-hero div:nth-child(n) .stColumn:nth-child(2) a[data-testid="stPageLink-NavLink"] p,
.st-key-hero div:nth-child(n) .stColumn:nth-child(2) a[data-testid="stPageLink-NavLink"] span {{ color: {CAM} !important; }}

/* ---------- ô tính năng ---------- */
.tinh-nang {{ background: #F6EBD0; border-radius: 20px; text-align: center; padding: 16px 10px;
    box-shadow: 0 3px 12px rgba(80,60,20,.10); }}
.tinh-nang .bieu-tuong {{ font-size: 1.7rem; }}
.tinh-nang .gt {{ color: {CAM}; font-weight: 800; font-size: 1.3rem; }}
.tinh-nang .nhan {{ color: #6B5836; font-size: .86rem; }}

/* ---------- thẻ chung ---------- */
.the {{ background: #fff; border: 1px solid #E7E1CC; border-radius: 20px; padding: 20px 22px;
    box-shadow: 0 3px 14px rgba(40,70,40,.08); color: #1F2A1F; height: 100%; }}
.the .so-tt {{ width: 38px; height: 38px; border-radius: 50%; background: {XANH}; color: #fff; display: flex;
    align-items: center; justify-content: center; font-weight: 800; margin-bottom: .6rem; }}
.the h4 {{ margin: 0 0 .4rem 0; color: {XANH_DAM}; }}

/* ---------- khối xanh ---------- */
.st-key-khoi_xanh, .st-key-khoi_so {{ background: linear-gradient(180deg, #2F6B3A 0%, #3B7A45 100%);
    border-radius: 26px; padding: 8px 28px 28px 28px; margin: 1.6rem 0; }}
.st-key-khoi_xanh .tieu-de-muc .lon, .st-key-khoi_so .tieu-de-muc .lon {{ color: #fff; }}
.st-key-khoi_xanh .tieu-de-muc .nho, .st-key-khoi_so .tieu-de-muc .nho {{ color: #F3D9A4; }}
.st-key-khoi_xanh .tieu-de-muc .mo-ta, .st-key-khoi_so .tieu-de-muc .mo-ta {{ color: #DCEFD9; }}
.st-key-khoi_so {{ background: linear-gradient(180deg, #123524 0%, #1F4D2E 100%); }}

/* ---------- thẻ ảnh cây ---------- */
.the-cay {{ background: #fff; border-radius: 22px; overflow: hidden; box-shadow: 0 4px 16px rgba(20,60,30,.14);
    border: 1px solid #E7E1CC; color: #1F2A1F; }}
.the-cay .anh-the {{ width: 100%; background-size: cover; background-position: center; }}
.the-cay .noi-dung {{ padding: 12px 16px 14px 16px; min-height: 142px; }}
.the-cay .ten {{ font-weight: 800; color: {XANH_DAM}; font-size: 1.1rem; }}
.the-cay .en {{ color: #7A8B7A; font-size: .82rem; font-style: italic; }}
.the-cay .thong-tin {{ font-size: .84rem; color: #4A5B4A; margin-top: .4rem; }}
.nhom-tag {{ display: inline-block; background: #E6F1DC; color: {XANH}; border-radius: 999px; padding: 2px 10px;
    font-size: .76rem; font-weight: 700; }}
.anh-the.trong {{ background: linear-gradient(135deg, #DDEBCB 0%, #BFDDB0 100%); display: flex; align-items: center;
    justify-content: center; }}
.anh-the.trong span {{ font-size: 3.4rem; }}

/* ---------- kết quả gợi ý ---------- */
.kq {{ text-align: center; background: linear-gradient(160deg, #FFFFFF 0%, #F1F8E9 100%); border: 2px solid #A5D6A7;
    border-radius: 24px; padding: 18px 20px 22px 20px; box-shadow: 0 6px 20px rgba(46,125,50,.15); color: #1F2A1F; }}
.kq .anh-the {{ border-radius: 16px; margin-bottom: .6rem; background-size: cover; background-position: center; }}
.kq .nho {{ color: #5B7A5B; font-size: .85rem; letter-spacing: .08em; text-transform: uppercase; }}
.kq .ten {{ font-size: 2.2rem; font-weight: 800; color: {XANH_DAM}; line-height: 1.15; }}
.kq .en {{ color: #6B8A6B; font-style: italic; margin-bottom: .6rem; }}
.badge {{ display: inline-block; border-radius: 999px; padding: 5px 16px; font-weight: 600; font-size: .92rem; }}
.badge.cao {{ background: #DCEDC8; color: #1B5E20; }}
.badge.tb {{ background: #FFE0B2; color: #E65100; }}
.badge.thap {{ background: #FFCDD2; color: #B71C1C; }}
.mini {{ text-align: center; background: #fff; border: 1px solid #E7E1CC; border-radius: 18px; padding: 8px 8px 12px 8px;
    box-shadow: 0 2px 8px rgba(30,70,30,.07); color: #1F2A1F; overflow: hidden; }}
.mini .anh-the {{ border-radius: 12px; margin-bottom: .4rem; background-size: cover; background-position: center; }}
.mini .hang {{ font-size: .78rem; color: #6B8A6B; text-transform: uppercase; letter-spacing: .06em; }}
.mini .ten {{ font-weight: 700; color: {XANH_DAM}; }}
.mini .pt {{ color: {CAM}; font-weight: 700; }}

/* ---------- số liệu ---------- */
.so {{ text-align: center; background: #fff; border: 1px solid #E7E1CC; border-radius: 16px; padding: 14px 8px;
    box-shadow: 0 2px 8px rgba(30,70,30,.07); color: #1F2A1F; }}
.so .v {{ font-size: 1.9rem; font-weight: 800; color: {XANH}; }}
.so .l {{ font-size: .85rem; color: #5B7A5B; }}
.st-key-khoi_so .so {{ background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.2); }}
.st-key-khoi_so .so .v {{ color: #C7F0A8; }}
.st-key-khoi_so .so .l {{ color: #DCEFD9; }}

/* ---------- cẩm nang ---------- */
.cn-ten {{ font-size: 2.6rem; font-weight: 800; color: #fff; line-height: 1.1; }}
.cn-kh {{ color: #E8F3EA; font-style: italic; margin-bottom: .6rem; }}
.cn-the {{ display: inline-block; background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.4); color: #fff;
    border-radius: 999px; padding: 4px 14px; margin-right: 8px; font-size: .88rem; }}
.thong-so {{ background: #F6EBD0; border-radius: 18px; padding: 14px 16px; min-height: 108px; }}
.thong-so .l {{ color: #7A6535; font-size: .8rem; text-transform: uppercase; letter-spacing: .06em; font-weight: 700; }}
.thong-so .v {{ color: #3F3320; font-weight: 700; margin-top: .2rem; }}
.buoc {{ background: #fff; border-left: 6px solid #66BB6A; border-radius: 14px; padding: 14px 18px; margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(30,70,30,.07); color: #1F2A1F; }}
.buoc b {{ color: {XANH_DAM}; }}
.buoc .stt {{ display: inline-block; background: {XANH}; color: #fff; border-radius: 50%; width: 26px; height: 26px;
    text-align: center; line-height: 26px; font-weight: 800; margin-right: 8px; font-size: .85rem; }}
.sau-benh {{ background: #FFF4E5; border: 1px solid #F3D9A4; border-radius: 14px; padding: 12px 16px; margin-bottom: 8px; color: #3F3320; }}
.sau-benh b {{ color: {CAM}; }}
.loi-khuyen {{ border-radius: 14px; padding: 12px 16px; margin-bottom: 8px; color: #1F2A1F; }}
.loi-khuyen.thap {{ background: #FFF3E0; border-left: 6px solid #FB8C00; }}
.loi-khuyen.cao {{ background: #FDECEA; border-left: 6px solid #E53935; }}
.loi-khuyen.phu_hop {{ background: #E8F5E9; border-left: 6px solid #43A047; }}
.meo {{ background: #E8F5E9; border-radius: 14px; padding: 12px 16px; margin-bottom: 8px; color: #1F3A1F; }}

/* ---------- kêu gọi hành động ---------- */
.st-key-cta {{ background: {nen_cta}; background-size: cover; background-position: center; border-radius: 26px;
    padding: 40px 44px; margin: 1.6rem 0; color: #fff; }}
.st-key-cta h2 {{ color: #fff !important; margin: 0 0 .4rem 0; }}
.st-key-cta p {{ color: #E8F3EA; }}
.st-key-cta a[data-testid="stPageLink-NavLink"] {{ background: {CAM}; border-radius: 10px; padding: .55rem 1rem; justify-content: center; }}
.st-key-cta a[data-testid="stPageLink-NavLink"] p, .st-key-cta a[data-testid="stPageLink-NavLink"] span {{ color: #fff !important; font-weight: 700; }}

/* ---------- chân trang ---------- */
.chan-trang {{ background: #123524; color: #CFE5CF; border-radius: 22px; padding: 26px 32px; margin-top: 2rem; }}
.chan-trang b {{ color: #fff; font-size: 1.1rem; }}
.chan-trang .luu-y {{ color: #9FBF9F; font-size: .82rem; margin-top: .6rem; }}

div[data-testid="stTabs"] button[role="tab"] {{ font-size: 1.02rem; font-weight: 600; }}
</style>
""",
        unsafe_allow_html=True,
    )


def rut_gon(chuoi):
    """Lấy phần đầu của một chuỗi dài (trước dấu ; hoặc ,) để vừa trong thẻ nhỏ."""
    return chuoi.replace(";", ",").split(",")[0].strip()


def tieu_de_muc(nho, lon, mo_ta=""):
    st.markdown(
        f'<div class="tieu-de-muc"><div class="nho">{nho}</div><div class="lon">{lon}</div>'
        + (f'<div class="mo-ta">{mo_ta}</div>' if mo_ta else "") + "</div>",
        unsafe_allow_html=True,
    )


def chan_trang():
    st.markdown(
        """
<div class="chan-trang">
  <b>🌱 Đất & Cây</b><br>
  Hệ thống hỗ trợ lựa chọn cây trồng dựa trên điều kiện đất (N, P, K, pH), dùng Random Forest tự cài đặt.<br>
  <div class="luu-y">Kết quả và cẩm nang chỉ mang tính tham khảo. Mùa vụ và kỹ thuật thay đổi theo vùng và giống;
  nên hỏi thêm khuyến nông địa phương. Dữ liệu: Crop Recommendation (có dấu hiệu là dữ liệu mô phỏng).</div>
</div>
""",
        unsafe_allow_html=True,
    )
