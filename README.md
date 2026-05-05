# GraphRAG Knowledge System - Tech Company Corpus

Dự án triển khai hệ thống **GraphRAG** (Graph Retrieval-Augmented Generation) để quản lý và truy vấn tri thức về các tập đoàn công nghệ lớn, so sánh hiệu quả trực tiếp với hệ thống **Flat RAG** truyền thống.

## 🚀 Tính năng chính
- **Data Collection:** Tự động lấy dữ liệu bài báo từ Wikipedia (OpenAI, Microsoft, Google, Tesla, Apple, Nvidia).
- **Indexing (LLM-based):** Sử dụng LLM để trích xuất các bộ ba thực thể - quan hệ (Entity-Relation Triples).
- **Graph Construction:** Xây dựng đồ thị tri thức trên **Neo4j** thông qua Docker.
- **Local LLM Integration:** Chạy hoàn toàn offline bằng **Ollama (Llama 3)** để đảm bảo quyền riêng tư và chi phí $0.
- **Evaluation:** Script so sánh đối đầu giữa GraphRAG (Neo4j) và Flat RAG (Vector Search - ChromaDB).

## 🛠 Tech Stack
- **Languages:** Python 3.13+
- **Frameworks:** LangChain, Pydantic
- **Databases:** Neo4j (Graph), ChromaDB (Vector)
- **LLM:** Ollama (Llama 3)
- **Infrastructure:** Docker, Docker Compose

## 📋 Hướng dẫn cài đặt

### 1. Chuẩn bị môi trường
- Cài đặt [Docker](https://www.docker.com/) và [Ollama](https://ollama.com/).
- Tải model Llama 3: `ollama run llama3`.

### 2. Khởi chạy Database
```bash
docker-compose up -d
```

### 3. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

## 🏃 Quy trình thực hiện

1. **Lấy dữ liệu:** Tải dữ liệu từ Wikipedia.
   ```bash
   python fetch_wiki_data.py
   ```
2. **Trích xuất Triples:** LLM đọc văn bản và chuyển thành dạng đồ thị.
   ```bash
   python extract_triples.py
   ```
3. **Xây dựng đồ thị:** Đẩy dữ liệu vào Neo4j.
   ```bash
   python build_graph_neo4j.py
   ```
4. **Đánh giá & So sánh:** Chạy benchmark đối đầu.
   ```bash
   python compare_rag.py
   ```

## 📊 Kết quả đánh giá (Benchmark Results)

| Tiêu chí | Flat RAG (Vector Search) | GraphRAG (Knowledge Graph) |
| :--- | :--- | :--- |
| **Độ chính xác** | Thường xuyên bỏ lỡ các thực thể nằm ở các đoạn văn khác nhau. | Kết nối hoàn hảo nhờ cơ chế duyệt đồ thị (Graph Traversal). |
| **Suy luận Multi-hop** | Kém, không trả lời được các câu hỏi về mối quan hệ gián tiếp. | Xuất sắc, tìm được đường đi giữa các thực thể cách xa nhau. |
| **Ảo giác (Hallucination)** | Dễ bị "chém gió" khi không tìm thấy chunk chính xác. | Chỉ trả lời dựa trên các quan hệ có thật trong đồ thị. |

**Kết luận:** GraphRAG vượt trội hơn hẳn trong việc trả lời các câu hỏi phức tạp về cấu trúc tổ chức và mối liên hệ giữa các nhân vật/công ty trong ngành công nghệ.

---
*Thực hiện bởi: Phan Văn Tấn - Day 19 GraphRAG Lab*
