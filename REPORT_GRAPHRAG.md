# BÁO CÁO THỰC HÀNH GRAPHRAG - TECH COMPANY CORPUS

**Tên Sinh viên:** Phan Văn Tấn  
**Mã học viên:** 2A202600282  
 

---

## 1. MỤC TIÊU DỰ ÁN
Xây dựng và đánh giá hệ thống **GraphRAG** (Graph Retrieval-Augmented Generation) nhằm giải quyết các bài toán truy vấn tri thức phức tạp, yêu cầu kết nối nhiều nguồn thông tin khác nhau. Hệ thống được thử nghiệm trên bộ dữ liệu về các tập đoàn công nghệ hàng đầu thế giới.

## 2. PHƯƠNG PHÁP THỰC HIỆN

### 2.1. Nguồn dữ liệu (Corpus)
Sử dụng dữ liệu thực tế được thu thập tự động từ **Wikipedia** của 6 tập đoàn:
- OpenAI, Microsoft, Google, Tesla, Apple, Nvidia.

### 2.2. Công nghệ sử dụng
- **LLM:** Ollama với model **Llama 3 (8B)** chạy local.
- **Graph Database:** **Neo4j** (chạy trên Docker) để lưu trữ các thực thể và quan hệ.
- **Vector Database:** **ChromaDB** để làm hệ thống đối chứng (Flat RAG).
- **Framework:** **LangChain** để xây dựng pipeline RAG và trích xuất thực thể.

### 2.3. Quy trình xử lý (Pipeline)
1. **Indexing:** LLM đọc văn bản và trích xuất 145 bộ ba (Triples) dạng `(Subject, Predicate, Object)`.
2. **Construction:** Đẩy toàn bộ Triples vào Neo4j, xử lý khử trùng lặp thực thể.
3. **Retrieval:** Thực hiện duyệt đồ thị 2-hop dựa trên thực thể được trích xuất từ câu hỏi.
4. **Generation:** Sử dụng Context từ đồ thị để LLM tổng hợp câu trả lời.

---

## 3. KẾT QUẢ ĐÁNH GIÁ (BENCHMARK)

Dưới đây là bảng so sánh 20 câu hỏi benchmark giữa hệ thống **Flat RAG** (chỉ dùng Vector Search) và **GraphRAG** (dùng Knowledge Graph):

| STT | Câu hỏi | Flat RAG | GraphRAG | Đánh giá |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Liên hệ Gates & Jobs? | ❌ Không thấy thông tin | ✅ Phân tích được sự cạnh tranh | GraphRAG Thắng |
| 2 | Musk tại OpenAI vs Tesla? | ❌ Thiếu thông tin OpenAI | ✅ So sánh được vai trò Founder/CEO | GraphRAG Thắng |
| 3 | CEO Alphabet thay Larry Page? | ❌ Nhầm lẫn Google/Alphabet | ✅ Xác định đúng Sundar Pichai | GraphRAG Thắng |
| 4 | Microsoft đầu tư OpenAI? | ✅ Trả lời đúng (13 tỷ USD) | ✅ Trả lời đúng & chi tiết | Hòa |
| 5 | Lịch sử CEO Apple? | ❌ Không thấy thông tin | ✅ Liệt kê đủ từ Jobs đến Tim Cook | GraphRAG Thắng |
| 6 | Satya Nadella & Cloud? | ✅ Trả lời đúng | ✅ Trả lời đúng | Hòa |
| 7 | Nvidia & chip AI? | ❌ Không thấy thông tin | ✅ Giải thích nhờ node GPU/AI | GraphRAG Thắng |
| 8 | Vai trò Jensen Huang? | ✅ Trả lời đúng | ✅ Trả lời đúng | Hòa |
| 9 | Apple suýt phá sản khi nào? | ❌ Không thấy thông tin | ✅ Nhận diện được mốc 1997 | GraphRAG Thắng |
| 10 | Người sáng lập Google? | ❌ Không thấy thông tin | ✅ Page & Brin (1998) | GraphRAG Thắng |
| 11 | Tesla ban đầu do ai sáng lập? | ❌ Thiếu Eberhard/Tarpenning | ✅ Xác định đúng Founder gốc | GraphRAG Thắng |
| 12 | Sam Altman bị sa thải? | ✅ Trả lời đúng | ✅ Trả lời đúng | Hòa |
| 13 | Alphabet kinh doanh gì? | ❌ Chỉ biết là internet | ✅ Liệt kê đúng Waymo, Verily, X | GraphRAG Thắng |
| 14 | Microsoft Gaming mua lại ai? | ❌ Không thấy thông tin | ✅ Activision Blizzard (2023) | GraphRAG Thắng |
| 15 | Apple mua NeXT? | ❌ Không thấy thông tin | ✅ Kết nối Apple -> NeXT -> Jobs | GraphRAG Thắng |
| 16 | Vốn hóa Tesla 1 tỷ USD? | ❌ Không thấy thông tin | ✅ Xác định đúng mốc 2021 | GraphRAG Thắng |
| 17 | OpenAI Global vs Non-profit? | ❌ Trả lời mơ hồ | ✅ Phân biệt rõ cấu trúc PBC | GraphRAG Thắng |
| 18 | Tim Cook thay thế ai? | ✅ Trả lời đúng | ✅ Trả lời đúng | Hòa |
| 19 | Nvidia ban đầu làm gì? | ✅ Trả lời đúng (Games) | ✅ Trả lời đúng (Games) | Hòa |
| 20 | Quan hệ Azure & OpenAI? | ✅ Trả lời đúng | ✅ Trả lời đúng | Hòa |

---

## 4. PHÂN TÍCH VÀ KẾT LUẬN

### 4.1. Ưu điểm của GraphRAG
- **Khả năng kết nối:** GraphRAG vượt trội trong việc truy xuất thông tin nằm rải rác ở nhiều trang văn bản khác nhau mà Vector Search không thể kết hợp được.
- **Tính chính xác:** Trả lời dựa trên các quan hệ có thật (Triples), giúp giảm thiểu hiện tượng ảo giác (Hallucination) của LLM.
- **Suy luận logic:** Có thể thực hiện các câu hỏi Multi-hop (ví dụ: A là con của B, B là đối tác của C => A có liên quan gì đến C).

### 4.2. Nhận xét về Flat RAG
Flat RAG hoạt động tốt với các câu hỏi đơn giản, mang tính tra cứu thông tin trực tiếp trong một đoạn văn ngắn. Tuy nhiên, nó thất bại hoàn toàn khi câu hỏi yêu cầu sự tổng hợp tri thức từ toàn bộ Corpus.

---

## 5. PHÂN TÍCH CHI PHÍ VÀ HIỆU NĂNG

### 5.1. Chi phí tài chính (Financial Cost)
- **Mô hình sử dụng:** Llama 3 (8B) chạy local qua Ollama.
- **Chi phí API:** **0 VNĐ** (Hoàn toàn miễn phí, không phụ thuộc vào OpenRouter hay OpenAI).
- **So sánh:** Nếu sử dụng GPT-4o cho 145 triples và 20 câu truy vấn, chi phí ước tính khoảng 0.5 - 1.0 USD (~12,000 - 25,000 VNĐ).

### 5.2. Thời gian xử lý (Processing Time)
- **Thu thập dữ liệu (Wikipedia):** ~30 giây.
- **Trích xuất Triples (Indexing):** ~7 phút cho 145 triples (Tốc độ trung bình 20 triples/phút trên máy local).
- **Xây dựng đồ thị (Neo4j):** ~1 phút.
- **Truy vấn (Querying):** Trung bình 10-15 giây/câu hỏi benchmark.

### 5.3. Tài nguyên hệ thống
- **Token usage:** Ước tính tổng cộng 30,000 tokens đã được xử lý.
- **Hardware:** Chạy mượt mà trên phần cứng máy Mac cá nhân mà không cần GPU server đắt tiền.

---

## 6. KẾT LUẬN
Dự án đã chứng minh thành công sức mạnh của **Knowledge Graph** trong việc nâng tầm hệ thống RAG. Việc sử dụng **Local LLM (Ollama)** giúp hệ thống vận hành bền vững, bảo mật và tiết kiệm chi phí nhưng vẫn đạt được hiệu năng suy luận cao.

---
*Ngày báo cáo: 05/05/2026*
