# -*- coding: utf-8 -*-
"""
SAVICO Dashboard trên Streamlit.

Chạy trên máy:      streamlit run app.py
Streamlit Cloud:    đẩy cả thư mục lên GitHub → share.streamlit.io → chọn repo, file chính = app.py

Nguồn số liệu (theo thứ tự ưu tiên):
  1. File Excel tải lên ở thanh bên (chỉ hiển thị trong phiên của người tải)
  2. File Excel mới nhất trong thư mục input/ (khi chạy trên máy)
  3. Bản tổng hợp mới nhất trong docs/history/ (do update.bat tạo và đẩy lên GitHub — không chứa tên KH / số đơn)

Đặt mật khẩu (tuỳ chọn): Streamlit Cloud → App settings → Secrets:  APP_PASSWORD = "matkhau"
"""
import base64, glob, json, os, sys, tempfile

import streamlit as st
import streamlit.components.v1 as components

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_data  # noqa: E402

st.set_page_config(page_title="SAVICO · Báo cáo kinh doanh", page_icon="📊", layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown("""<style>
#MainMenu, header[data-testid="stHeader"], footer {visibility:hidden;height:0}
.block-container {padding:0 !important; max-width:100% !important}
iframe {display:block}
.stApp {background:#f3f5f9}
</style>""", unsafe_allow_html=True)


def password_ok():
    try:
        pw = st.secrets.get("APP_PASSWORD")
    except Exception:
        pw = None
    if not pw or st.session_state.get("auth"):
        return True
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<div style='height:18vh'></div>", unsafe_allow_html=True)
        st.subheader("SAVICO · Báo cáo kinh doanh")
        v = st.text_input("Mật khẩu", type="password")
        if v:
            if v == pw:
                st.session_state["auth"] = True
                st.rerun()
            st.error("Mật khẩu không đúng")
    return False


@st.cache_data(show_spinner="Đang đọc file Excel…")
def build_from_bytes(data: bytes, name: str):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, name)
        with open(path, "wb") as f:
            f.write(data)
        try:
            return build_data.build(path), None
        except SystemExit as e:  # build_data báo lỗi bằng sys.exit("[LỖI] ...")
            return None, str(e)


@st.cache_data
def build_from_path(path: str, mtime: float):
    try:
        return build_data.build(path), None
    except SystemExit as e:
        return None, str(e)


def load_data(upload):
    if upload is not None:
        return build_from_bytes(upload.getvalue(), upload.name)
    files = [f for f in glob.glob(os.path.join(ROOT, "input", "*.xls*")) if not os.path.basename(f).startswith("~$")]
    if files:
        p = max(files, key=os.path.getmtime)
        return build_from_path(p, os.path.getmtime(p))
    hist = sorted(glob.glob(os.path.join(ROOT, "docs", "history", "data-*.json")))
    if hist:
        with open(hist[-1], encoding="utf-8") as f:
            return json.load(f), None
    return None, "Chưa có dữ liệu. Mở thanh bên (») và tải file Excel Doanh thu Savico lên."


def data_uri(path):
    ext = os.path.splitext(path)[1].lstrip(".").replace("jpg", "jpeg").replace("svg", "svg+xml")
    with open(path, "rb") as f:
        return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode()


def page_html(data):
    with open(os.path.join(ROOT, "docs", "index.html"), encoding="utf-8") as f:
        html = f.read()
    payload = json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/")
    html = html.replace('<script src="data.js"></script>',
                        f"<script>window.SAVICO_EMBED=true;window.SAVICO_DATA={payload};</script>")
    for name in ("logo-pvi.png", "logo-savico.png"):
        p = os.path.join(ROOT, "docs", "assets", name)
        if os.path.exists(p):
            html = html.replace(f'src="assets/{name}"', f'src="{data_uri(p)}"')
    return html


if password_ok():
    with st.sidebar:
        st.markdown("### Cập nhật số liệu")
        upload = st.file_uploader("File Excel Doanh thu Savico", type=["xlsx", "xlsm"])
        st.caption("File tải lên chỉ dùng trong phiên xem của bạn, không lưu lên máy chủ.")
    data, err = load_data(upload)
    if err:
        st.error(err)
    if data:
        if hasattr(st, "iframe"):  # Streamlit ≥ 1.52: tự co giãn theo chiều cao nội dung
            st.iframe(page_html(data), height="content")
        else:
            components.html(page_html(data), height=2400, scrolling=True)
