# Hướng Dẫn Sử Dụng Discord Python Quiz Bot (Độ Khó & Chống Trùng Lặp 100%)

## ✨ Các tính năng mới:
1. **Lựa chọn 3 cấp độ code**:
   - 🟢 **Dễ (`easy` / `de`)**: Toán tử cơ bản, chuỗi, danh sách, vòng lặp cơ bản, biểu thức `if/else`, kiểm tra giá trị logic.
   - 🟡 **Trung bình (`medium` / `tb`)**: List/Dict comprehension, Set, Slicing nâng cao, Lambda, phép toán Bitwise (`<<`, `>>`, `^`, `&`), hàm và tham chiếu biến.
   - 🔴 **Khó (`hard` / `kho`)**: Các bẫy kinh điển Python (Mutable default argument, Closure late binding, Unpacking `*head`, Shallow/Deep copy, Generator exhaustion, Float precision `0.1 + 0.2 == 0.3`, Thuật toán đệ quy Euclid, Binary Search, Fold accumulator).
   - 🎲 **Ngẫu nhiên (`random`)**: Trộn tất cả độ khó.

2. **Cơ chế chống trùng lặp tuyệt đối 100%**:
   - Sử dụng **SQLite Database (`seen_questions.db`)** và mã băm **SHA-256** của từng khối mã code.
   - Khi sinh một đoạn code, bot kiểm tra hàm băm. Nếu đã từng xuất hiện ở bất kỳ lần nào trước đó, bot lập tức bỏ qua và sinh một code hoàn toàn mới.
   - **Tổ hợp sinh động (Combinatorial Space)**: Với hàng chục template kết hợp biến số, toán tử, danh sách từ vựng, số lượng câu hỏi khác biệt thực tế vượt xa hàng chục nghìn đến hàng triệu biến thể, đảm bảo không bao giờ hết câu hỏi.

---

## 🎮 Cách sử dụng lệnh trong Discord:

### 1. Dùng lệnh gõ thông thường:
- `!quiz`: Sinh ngẫu nhiên câu hỏi ở bất kỳ độ khó nào.
- `!quiz easy` (hoặc `!quiz de`): Sinh câu hỏi chế độ **Dễ**.
- `!quiz med` (hoặc `!quiz tb`): Sinh câu hỏi chế độ **Trung bình**.
- `!quiz hard` (hoặc `!quiz kho`): Sinh câu hỏi chế độ **Khó**.

### 2. Dùng Slash Command:
- Gõ `/quiz` -> Discord sẽ hiện ra danh sách chọn trực quan:
  - `🟢 Dễ (Beginner)`
  - `🟡 Trung bình (Intermediate)`
  - `🔴 Khó (Advanced / Tricky)`
  - `🎲 Ngẫu nhiên (All Levels)`

### 3. Các lệnh phụ trợ:
- `!stats`: Xem tổng số lượng code khác biệt mà hệ thống đã từng sinh ra.
- `!rank`: Xem bảng xếp hạng điểm số và tỷ lệ trả lời đúng của server.

---

## 🚀 Khởi động Bot:
1. Mở file [`.env`](file:///C:/Users/LENOVO/.gemini/antigravity/scratch/discord-quiz-bot/.env) và dán Token Discord Bot.
2. Chạy bot:
```bash
python bot.py
```
