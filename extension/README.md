# Tiện ích kết nối Muse2API

Tiện ích lấy Cookie đăng nhập `muse.ai` trong Chrome/Edge và gửi tới máy chủ Muse2API do bạn chọn. Cookie chỉ được gửi đến địa chỉ dịch vụ đã nhập; tiện ích không liên hệ máy chủ bên thứ ba.

## Cài đặt

1. Tải `muse2api-extension.zip` từ tab **Thêm tài khoản** trong trang quản trị Muse2API rồi giải nén vào thư mục dễ tìm.
2. Mở `chrome://extensions` (Chrome) hoặc `edge://extensions` (Edge).
3. Bật **Chế độ dành cho nhà phát triển**.
4. Chọn **Tải tiện ích đã giải nén** và chọn thư mục vừa giải nén, nơi có `manifest.json`.
5. Ghim tiện ích lên thanh công cụ nếu muốn truy cập nhanh.

## Kết nối tài khoản

1. Đăng nhập `https://muse.ai/` trong cùng trình duyệt.
2. Mở trang quản trị Muse2API, vào tab **Thêm tài khoản**.
3. Khi đang ở trang quản trị, bấm biểu tượng tiện ích. Địa chỉ dịch vụ và API key sẽ được lấy tự động từ trang hiện tại.
4. Nhập tên gợi nhớ nếu cần, rồi chọn **Lấy Cookie và thêm tài khoản**.
5. Xác nhận tài khoản xuất hiện trong danh sách trên trang quản trị.

Bạn cũng có thể nhập địa chỉ dịch vụ và API key thủ công. Nếu thay đổi API key, hãy mở lại trang quản trị rồi mở tiện ích để cập nhật.

## Xử lý lỗi

- **Không tìm thấy Cookie:** đăng nhập muse.ai trong trình duyệt này rồi thử lại.
- **Thiếu Cookie:** hoàn tất đăng nhập và kiểm tra bạn vào được trang Muse.ai.
- **API key không đúng:** tải lại trang quản trị và mở tiện ích trên trang đó để lấy key mới.
- **Không kết nối được:** kiểm tra máy chủ đang chạy và địa chỉ dịch vụ chính xác.

## Quyền riêng tư

Tiện ích cần quyền đọc Cookie của muse.ai, lưu cấu hình trong bộ nhớ cục bộ của trình duyệt và gửi Cookie tới máy chủ bạn chọn. API key cũng được lưu cục bộ để tiện sử dụng. Không chia sẻ thư mục cấu hình hay thông tin Cookie của bạn.
