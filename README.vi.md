# Muse2API Community

[English](README.md) | [Tiếng Việt](README.vi.md)

API tự host tương thích OpenAI cho Muse web app. Bản community này kế thừa dự án upstream, giữ giấy phép và ghi nhận đóng góp ban đầu, đồng thời hướng tới cách cài đặt dễ làm theo.

> Đây là tích hợp bên thứ ba, không liên kết hay được Muse xác nhận. Chỉ dùng với tài khoản và quyền truy cập mà bạn được phép sử dụng; hãy tuân thủ điều khoản của dịch vụ.

## Cài nhanh bằng Docker

1. Cài Docker Engine và Docker Compose plugin.
2. Clone repo và vào thư mục dự án:

   ```sh
   git clone https://github.com/bynne2602/muse2api.git
   cd muse2api
   ```

3. Tạo cấu hình riêng:

   ```sh
   cp .env.example .env
   ```

   Mở `.env`, đặt `MUSE2API_KEY` thành một chuỗi bí mật ngẫu nhiên, đủ dài. Không chia sẻ key và không commit file `.env`.

4. Khởi động:

   ```sh
   docker compose up -d --build
   ```

5. Mở `http://localhost:18610/admin?key=YOUR_KEY`, đăng nhập Muse theo hướng dẫn trên trình duyệt rồi thêm tài khoản của bạn. Hãy giữ dịch vụ ở chế độ riêng tư; nếu cần truy cập từ Internet, hãy dùng HTTPS và lớp kiểm soát truy cập đáng tin cậy.

Dữ liệu tài khoản và file tạo ra nằm trong `./data`. Hãy sao lưu thư mục này an toàn. Không công khai cookie, API key, browser profile hoặc media riêng tư.

## Chạy bằng Python (không cần Docker)

Cần Python 3.10 trở lên và Google Chrome hoặc Chromium. Tạo môi trường riêng, cài thư viện rồi tạo file cấu hình:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Mở `.env`, đặt `MUSE2API_KEY` thành một key bí mật của riêng bạn. Không dùng key mẫu công khai và không commit file `.env`. Sau đó chạy:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 18610
```

Mở `http://127.0.0.1:18610/admin` để vào trang quản trị. Dừng dịch vụ bằng `Ctrl+C`. Nếu dùng Linux/macOS, thay đường dẫn Python trong môi trường ảo bằng `.venv/bin/python`; các bước còn lại tương tự.

### Tự khởi động khi đăng nhập Windows

Sau khi chạy thử thành công ở trên và đã tạo `.env`, có thể dùng **Task Scheduler (Bộ lập lịch tác vụ)** để khởi động dịch vụ mỗi khi bạn đăng nhập:

1. Nhấn `Win + R`, nhập `taskschd.msc`, rồi chọn **Create Task…**.
2. Tab **General**: đặt tên `Muse2API`; chọn **Run only when user is logged on**.
3. Tab **Triggers**: chọn **New…** → **Begin the task: At log on** → **OK**.
4. Tab **Actions**: chọn **New…** rồi điền các giá trị dưới đây, thay `C:\Users\TenBan\muse2api` bằng thư mục repo thực tế:

   - **Program/script:** `C:\Users\TenBan\muse2api\.venv\Scripts\python.exe`
   - **Add arguments:** `-m uvicorn app:app --host 127.0.0.1 --port 18610`
   - **Start in:** `C:\Users\TenBan\muse2api`

5. Chọn **OK** để lưu. Có thể chọn tác vụ Muse2API trong thư viện Task Scheduler và bấm **Run** để khởi động ngay mà không cần chờ đăng nhập lần sau.

Đảm bảo `.env` nằm trong thư mục repo và chứa `MUSE2API_KEY` của bạn. Để dịch vụ truy cập riêng trên máy, giữ `--host 127.0.0.1`; không mở cổng ra Internet nếu chưa cấu hình HTTPS và kiểm soát truy cập phù hợp.

Dữ liệu tài khoản và file tạo ra nằm trong `./data`. Hãy sao lưu thư mục này an toàn. Không công khai Cookie, API key, browser profile hoặc media riêng tư.

## Gọi API

Các API được bảo vệ cần header `Authorization: Bearer YOUR_KEY`.

Liệt kê model:

```sh
curl http://localhost:18610/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

Chat:

```sh
curl http://localhost:18610/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"muse-spark","messages":[{"role":"user","content":"Xin chào"}]}'
```

Tạo ảnh dùng `/v1/images/generations`; tạo video dùng `/v1/videos`. API video trả về mã tác vụ, hãy kiểm tra trạng thái tại `/v1/videos/{task_id}`. File tạo ra được phục vụ tại `/v1/media/{filename}`.

## Cấu hình thường dùng

| Biến | Mặc định | Công dụng |
| --- | --- | --- |
| `MUSE2API_KEY` | Tự tạo khi chạy lần đầu | Key cho trang quản trị và API. Hãy đặt key riêng trước khi mở dịch vụ ra ngoài. |
| `MUSE2API_HOST` | `0.0.0.0` | Địa chỉ bind bên trong service/container. |
| `MUSE2API_PORT` | `18610` | Cổng HTTP. |
| `MUSE2API_PUBLIC_BASE` | Để trống | URL public dùng để hiển thị cho client. |
| `MUSE2API_CHROMIUM` | Tự dò | Đường dẫn tới Chromium/Chrome. |
| `MUSE2API_CDP_PORT` | `19210` | Cổng debug nội bộ của trình duyệt; không mở công khai. |
| `MUSE2API_IMAGE_TIMEOUT` | `240` | Thời gian chờ tạo ảnh, tính bằng giây. |
| `MUSE2API_VIDEO_TIMEOUT` | `600` | Thời gian chờ tạo video, tính bằng giây. |
| `MUSE2API_CHAT_TIMEOUT` | `300` | Thời gian chờ chat, tính bằng giây. |
| `MUSE2API_CONCURRENCY` | `2` | Số tác vụ tạo nội dung chạy đồng thời tối đa. |
| `MUSE2API_UPDATER_ENABLED` | `0` | Đặt `1` để bật cập nhật online từ upstream. Bản fork nên để tắt cho đến khi đã đổi và kiểm tra repo đích. |
| `MUSE2API_ALLOW_WEB_PUSH` | `0` | Đặt `1` để cho phép publish repo từ trang quản trị. Hãy để tắt khi triển khai thông thường. |

## Phát triển

Cài dependencies rồi chạy các kiểm tra cục bộ:

```sh
python -m pip install -r requirements.txt
python tests/test_admin_base_url.py
python tests/test_async_images.py
python tests/test_media_delete.py
python tests/test_media_selection.py
python tests/test_session_health.py
python tests/test_vm_wait.py engine.py --assert
python tests/test_concurrency.py
```

Các kiểm tra này không xác nhận đăng nhập Muse trực tiếp hay tạo nội dung thật. Không đưa thông tin đăng nhập thật vào dữ liệu kiểm tra.

## Giấy phép và ghi nhận

Dự án dùng [giấy phép MIT](LICENSE), được phát triển dựa trên [czg86389-hub/muse2api](https://github.com/czg86389-hub/muse2api). Khi phân phối lại, hãy giữ giấy phép và ghi nhận upstream. Lịch sử Git và repo upstream lưu thông tin các contributor.

Chào mừng issue và pull request tại repo community này.
