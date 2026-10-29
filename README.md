# SAVICO Dashboard — Bảng xếp hạng BH XCG qua showroom SAVICO

Dựng theo mẫu OCARCARE Grand Prix. Đầu vào: file Excel thô **"Doanh thu Savico"**
(Báo cáo hiệu quả kinh doanh nghiệp vụ bảo hiểm xe cơ giới, sheet `Doanh thu` + sheet `Mã đơn vị`).

```
SAVICO_Dashboard/
├─ input/               ← thả file Excel thô vào đây (lấy file MỚI NHẤT)
├─ docs/                ← trang web (GitHub Pages)
│   ├─ index.html
│   ├─ data.js          ← script tạo tự động, không sửa tay
│   └─ history/         ← lưu số liệu từng ngày
├─ tools/build_data.py  ← đọc Excel → data.js (CẤU HÌNH thể lệ ở đầu file)
├─ app.py               ← ứng dụng Streamlit
├─ xem_thu.bat          ← tạo dữ liệu + mở trang trên máy
└─ update.bat           ← tạo dữ liệu + đẩy lên GitHub
```

## Cách 0 — Streamlit (khuyên dùng để chia sẻ link)
**Chạy thử trên máy:** `pip install -r requirements.txt` rồi `streamlit run app.py`.

**Đưa lên Streamlit Community Cloud:**
1. Đẩy cả thư mục lên một repo GitHub (`update.bat` làm việc này; thư mục `input/` và file Excel không bao giờ bị đẩy lên).
2. Vào https://share.streamlit.io → **Create app** → chọn repo, nhánh `main`, file chính `app.py` → **Deploy**.
3. (Nên làm) App settings → **Secrets**, thêm dòng `APP_PASSWORD = "matkhau"` để người xem phải nhập mật khẩu.

Số liệu app hiển thị = bản tổng hợp mới nhất trong `docs/history/` (mỗi lần chạy `update.bat` sẽ tạo bản mới và app tự cập nhật).
Ngoài ra ở thanh bên (») có ô tải file Excel để xem ngay số liệu mới — chỉ trong phiên của người tải, không lưu lại.

## Cách 1 — Không cần cài gì
Mở `docs/index.html` bằng Chrome/Edge → bấm **📂 Chọn file Excel thô** → chọn file Doanh thu Savico.
Bảng dựng ngay trên máy (cần Internet để tải thư viện đọc Excel). Số liệu không gửi đi đâu.

## Cách 2 — Cập nhật trang web chung (GitHub Pages)
1. Cài Python 3.9+ (tick "Add Python to PATH"), Git; chạy `pip install openpyxl`.
2. Lưu file Excel mới vào `input/`.
3. Nhấp đúp `xem_thu.bat` để xem trước, hoặc `update.bat` để đẩy lên GitHub.
4. Repo → Settings → Pages → Branch `main`, thư mục `/docs`.

`input/` và mọi file Excel bị chặn trong `.gitignore` → tên khách hàng, số đơn **không lên web**.
`data.js` chỉ chứa số tổng hợp theo showroom / đơn vị PVI / cán bộ.

## Nội dung trang
0. **Trang chọn đơn vị** (landing): thẻ "Toàn hệ thống" + thẻ từng đơn vị có phát sinh; đơn vị chưa phát sinh gom vào 1 dòng thu gọn.
1. Chỉ tiêu chính: doanh thu luỹ kế, số HĐBH, phí bình quân, số đơn vị / showroom có phát sinh (kèm phát sinh ngày báo cáo).
2. Bảng **theo đơn vị BH PVI**: Phát sinh ngày · Luỹ kế (HĐBH, doanh thu, tỷ trọng) · ngày phát sinh gần nhất. Đơn vị chưa phát sinh gom vào 1 dòng thu gọn cuối bảng.
3. Bảng **theo showroom SAVICO** (cùng cấu trúc).
4. Biểu đồ doanh thu theo ngày + luỹ kế. 5. Cơ cấu theo sản phẩm / chương trình KM / hãng xe / loại xe. 6. Cán bộ khai thác.

**Phạm vi xem:** chọn đơn vị ở thanh trên cùng (hoặc bấm tên đơn vị trong bảng) → toàn trang lọc theo đơn vị đó.
Link riêng cho từng đơn vị (bản GitHub Pages): thêm `#Tên đơn vị` vào cuối link, VD `.../index.html#PVI Hải Hưng`; `#all` = toàn hệ thống.
Nút **In / Lưu PDF** in khổ A4 ngang.

## Quy tắc tính
- Kỳ: theo dòng "Từ ngày … Đến ngày …" trong file (đổi được ở `CONFIG.program`).
- Doanh thu = cột **Phí BH (không VAT) – VNĐ** (`metric: "premium"`), hoặc **Doanh thu (không VAT)** (`metric: "revenue"`).
- Showroom = cột **Kênh bán hàng**, chuẩn hoá theo danh sách showroom ở sheet `Mã đơn vị` (cột D).
- Đơn vị = cột **Đơn vị cấp đơn**; danh sách theo dõi lấy ở sheet `Mã đơn vị` (cột A), **bỏ PVI Link** (đơn vị đối soát).
- Số HĐBH = số "Số đơn BH" không trùng (bỏ dòng sửa đổi bổ sung).
- "Ngày" = ngày cấp đơn mới nhất trong file.

## Khi cần chỉnh (đầu file `tools/build_data.py`)
| Việc | Sửa |
|---|---|
| Bỏ thêm đơn vị khỏi danh sách | `CONFIG["exclude_units"] = ["PVI Link", ...]` |
| Chỉ tính một số mã KM | `CONFIG["program"]["promo_codes"] = ["KM229", "KM230"]` |
| Ẩn bảng cán bộ | `CONFIG["show_staff"] = False` |
| Tên showroom trong báo cáo khác danh mục | thêm vào `SHOWROOM_ALIAS` (script sẽ cảnh báo) |

## Logo & ảnh nền (`docs/assets/`)
| File | Dùng cho |
|---|---|
| `logo-pvi.png`, `logo-savico.png` | Logo ở đầu trang (chép đè file cùng tên để thay) |

Giao diện nền sáng; màu thương hiệu: navy PVI `#183665`, đỏ SAVICO `#ED1C24`.
