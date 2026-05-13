# Phân tích chi tiết lỗi hiệu suất trên VPS Notebook (sotay5491.io.vn)

## Bối cảnh
Người dùng gặp phải tình trạng ứng dụng Notebook (chạy trên VPS `160.30.113.168`) thường xuyên "bị treo", vòng xoay loading lặp lại liên tục và nhận lỗi từ Cloudflare.

Qua quá trình stress test (thực hiện 10 request chat đồng thời), chúng tôi đã xác định được 3 điểm thắt cổ chai (bottlenecks) chính gây ra hiện tượng này.

---

## 1. Lỗi Cloudflare 524 (A Timeout Occurred)
### Hiện tượng
Khi người dùng bấm Chat, giao diện quay vòng tròn. Đúng 100 giây sau, trình duyệt hiển thị một trang báo lỗi có mã 524 của Cloudflare.
### Nguyên nhân
- Luồng xử lý gọi AI (ví dụ: `vertex-key.com`) hoạt động theo mô hình đồng bộ (chờ phản hồi một khối lượng văn bản lớn toàn bộ rồi mới trả về).
- Tốc độ phản hồi của Proxy AI quá chậm (thường mất hơn 100 giây cho mỗi đoạn hội thoại yêu cầu truy vấn tài liệu).
- Mạng proxy Cloudflare có giới hạn cứng (hard limit): Nếu máy chủ đích (Origin) không phản hồi bất kỳ một byte dữ liệu nào trong vòng 100 giây, Cloudflare sẽ chủ động ngắt kết nối với người dùng để bảo vệ băng thông, và hiển thị lỗi 524.
### Tác hại
Người dùng lầm tưởng VPS (máy chủ vật lý) hoặc tiến trình Backend đã chết/sập, nên nảy sinh hành vi bấm Retries (thử lại) liên tục.

---

## 2. Lỗi Cạn Kiệt Luồng Xử Lý (Thread Pool Exhaustion / Zombie Threads)
### Hiện tượng
Hệ thống hoàn toàn "đóng băng" (treo) ở diện rộng. Không một ai đăng nhập được, không bấm tải được trang và không đổi tên được tài liệu trong khoảng vài phút, sau đó lại tự hết.
### Nguyên nhân
- Khi lọt vào lỗi 524 ở trên, Cloudflare đã ngắt kết nối với trình duyệt người dùng. Tuy nhiên, **Backend Python KHÔNG nhận biết được khách đã đi**.
- Backend vẫn dồn toàn bộ nguồn lực "ngồi chờ" câu trả lời từ AI chậm chạp kia.
- Khi người dùng bấm Chat lại nhiều lần do mất kiên nhẫn, một khối lượng "Zombie Threads" (tiến trình vô nghĩa) được sinh ra. Framework FastAPI/Python chia sẻ chung các yêu cầu này vào một "Biển Luồng" (Thread pool, mặc định là ~40 luồng rảnh rỗi). Cả 40 luồng này lập tức bị lấp đầy bởi tiến trình ngồi chờ AI phản hồi.
- Kết cục: Server không tài nào nhận thêm *bất kỳ một request bình thường nào mới* cho đến khi các Zombie Threads trên bị giải tán hoặc quá hạn. 

---

## 3. Lỗi Nghẽn Thắt Cổ Chai Cơ Sở Dữ Liệu (SurrealDB Handshake Timeout)
### Hiện tượng
Hệ thống báo lỗi thẳng ra từ Python Backend:
`500 - {"detail":"Error building context: timed out during opening handshake"}`
### Nguyên nhân
- Đoạn code hệ thống (cụ thể tại `api/routers/chat.py` lúc truy xuất ngữ cảnh cho Notebook) dường như thực hiện khởi tạo Connection tới SurrealDB không tối ưu khi gặp môi trường tải đồng thời cao (Tốc độ gọi tức thì 10 request đổ lên).
- Việc quá nhiều luồng Python Threaded đồng loạt nhảy vào tạo liên kết WebSocket (handshake) cục bộ với SurrealDB Container ở cùng 1 nano-giây.
- Thư viện nội bộ không cung cấp đủ cổng giao tiếp hoặc cạn Socket cục bộ, dẫn tới sự nghẽn chai ở cổng kết nối và tự động đẩy ra lỗi Timeout DB.

---

## Tổng hợp Xử Lý & Khuyến Nghị
1. **Thay đổi nhà cung cấp AI nhanh hơn (Đã thực hiện):** Đổi sang OpenRouter giúp giảm thời gian chạy luồng xuống còn ~57 giây. Việc này ngay lập tức phá vỡ giới hạn 100 giây của Cloudflare và giảm hoàn toàn lỗi 1 ở trên.
2. **Triển khai AI Streaming (Chưa thực hiện nhưng Khuyến nghị Ưu tiên 1):** Cải tạo lại API Chat theo logic Server-Sent Events (SSE). Khi AI sinh ra từ nào, bắn thẳng về Frontend từ đó thay vì truyền trả theo khối lớn. Xử lý triệt để nguyên nhân dồn ứ Timeout 100s vì quá trình báo hiệu dữ liệu (Keep-alive) được đảm bảo.
3. **Quản lý hủy quy trình thông minh (Cancel Context Propagation):** Python cần được thêm bẫy sự kiện `request.is_disconnected()` để tự mình chấm dứt luôn tiến trình gọi LangChain nếu phát hiện Client đã đóng trình duyệt.
4. **Áp dụng Connection Pooling cho SurrealDB (Bắt buộc thiết kế lại):** Tái cấu trúc file `database.py` hoặc `chat.py`, mở sẵn "Hồ kết nối 20-50 kết nối" trước khi nhận request, thay vì tạo mới liên tục và va chạm giới hạn bắt tay (Handshake).
