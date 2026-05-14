<a id="readme-top"></a>

<!-- [![Contributors][contributors-shield]][contributors-url] -->
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
<!-- [![LinkedIn][linkedin-shield]][linkedin-url] -->


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/lfnovo/open-notebook">
    <img src="docs/assets/hero.svg" alt="Logo">
  </a>

  <h3 align="center">Open Notebook</h3>

  <p align="center">
    An open source, privacy-focused alternative to Google's Notebook LM!
    <br /><strong>Join our <a href="https://discord.gg/37XJPXfz2w">Discord server</a> for help, to share workflow ideas, and suggest features!</strong>
    <br />
    <a href="https://www.open-notebook.ai"><strong>Checkout our website »</strong></a>
    <br />
    <br />
    <a href="docs/0-START-HERE/index.md">📚 Get Started</a>
    ·
    <a href="docs/3-USER-GUIDE/index.md">📖 User Guide</a>
    ·
    <a href="docs/2-CORE-CONCEPTS/index.md">✨ Features</a>
    ·
    <a href="docs/1-INSTALLATION/index.md">🚀 Deploy</a>
  </p>
</div>

<p align="center">
<a href="https://trendshift.io/repositories/14536" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14536" alt="lfnovo%2Fopen-notebook | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

<div align="center">
  <!-- Keep these links. Translations will automatically update with the README. -->
  <a href="https://zdoc.app/de/lfnovo/open-notebook">Deutsch</a> | 
  <a href="https://zdoc.app/es/lfnovo/open-notebook">Español</a> | 
  <a href="https://zdoc.app/fr/lfnovo/open-notebook">français</a> | 
  <a href="https://zdoc.app/ja/lfnovo/open-notebook">日本語</a> | 
  <a href="https://zdoc.app/ko/lfnovo/open-notebook">한국어</a> | 
  <a href="https://zdoc.app/pt/lfnovo/open-notebook">Português</a> | 
  <a href="https://zdoc.app/ru/lfnovo/open-notebook">Русский</a> | 
  <a href="https://zdoc.app/zh/lfnovo/open-notebook">中文</a>
</div>

## A private, multi-model, 100% local, full-featured alternative to Notebook LM

![New Notebook](docs/assets/asset_list.png)

In a world dominated by Artificial Intelligence, having the ability to think 🧠 and acquire new knowledge 💡, is a skill that should not be a privilege for a few, nor restricted to a single provider.

**Open Notebook empowers you to:**
- 🔒 **Control your data** - Keep your research private and secure
- 🤖 **Choose your AI models** - Support for 16+ providers including OpenAI, Anthropic, Ollama, LM Studio, and more
- 📚 **Organize multi-modal content** - PDFs, videos, audio, web pages, and more
- 🎙️ **Generate professional podcasts** - Advanced multi-speaker podcast generation
- 🔍 **Search intelligently** - Full-text and vector search across all your content
- 💬 **Chat with context** - AI conversations powered by your research
- 🌐 **Multi-language UI** - English, Portuguese, Chinese (Simplified & Traditional), Japanese, and Russian support

Learn more about our project at [https://www.open-notebook.ai](https://www.open-notebook.ai)

---

## 🆚 Open Notebook vs Google Notebook LM

| Feature | Open Notebook | Google Notebook LM | Advantage |
|---------|---------------|--------------------|-----------|
| **Privacy & Control** | Self-hosted, your data | Google cloud only | Complete data sovereignty |
| **AI Provider Choice** | 16+ providers (OpenAI, Anthropic, Ollama, LM Studio, etc.) | Google models only | Flexibility and cost optimization |
| **Podcast Speakers** | 1-4 speakers with custom profiles | 2 speakers only | Extreme flexibility |
| **Content Transformations** | Custom and built-in | Limited options | Unlimited processing power |
| **API Access** | Full REST API | No API | Complete automation |
| **Deployment** | Docker, cloud, or local | Google hosted only | Deploy anywhere |
| **Citations** | Basic references (will improve) | Comprehensive with sources | Research integrity |
| **Customization** | Open source, fully customizable | Closed system | Unlimited extensibility |
| **Cost** | Pay only for AI usage | Free tier + Monthly subscription | Transparent and controllable |

**Why Choose Open Notebook?**
- 🔒 **Privacy First**: Your sensitive research stays completely private
- 💰 **Cost Control**: Choose cheaper AI providers or run locally with Ollama
- 🎙️ **Better Podcasts**: Full script control and multi-speaker flexibility vs limited 2-speaker deep-dive format
- 🔧 **Unlimited Customization**: Modify, extend, and integrate as needed
- 🌐 **No Vendor Lock-in**: Switch providers, deploy anywhere, own your data

### Built With

[![Python][Python]][Python-url] [![Next.js][Next.js]][Next-url] [![React][React]][React-url] [![SurrealDB][SurrealDB]][SurrealDB-url] [![LangChain][LangChain]][LangChain-url]

## 🚀 Quick Start

Choose your installation method:

### 🐳 **Docker (Recommended)**

**Best for most users** - Fast setup with Docker Compose:

→ **[Docker Compose Installation Guide](docs/1-INSTALLATION/docker-compose.md)**
- Multi-container setup (recommended)
- 5-10 minutes setup time
- Requires Docker Desktop

**Quick Start:**
- Get an API key (OpenAI, Anthropic, Google, etc.) or setup Ollama
- Create docker-compose.yml (example in guide)
- Run: docker compose up -d
- Access: http://localhost:8502

---

### 💻 **From Source (Developers)**

**For development and contributors:**

→ **[From Source Installation Guide](docs/1-INSTALLATION/from-source.md)**
- Clone and run locally
- 10-15 minutes setup time
- Requires: Python 3.11+, Node.js 18+, Docker, uv

**Quick Start:**

```bash
git clone https://github.com/lfnovo/open-notebook.git
uv sync
make start-all
```

Access: http://localhost:3000 (dev) or http://localhost:8502 (production)

---

### 📖 Need Help?

- **🤖 AI Installation Assistant**: [CustomGPT to help you install](https://chatgpt.com/g/g-68776e2765b48191bd1bae3f30212631-open-notebook-installation-assistant)
- **🆘 Troubleshooting**: [5-minute troubleshooting guide](docs/6-TROUBLESHOOTING/quick-fixes.md)
- **💬 Community Support**: [Discord Server](https://discord.gg/37XJPXfz2w)
- **🐛 Report Issues**: [GitHub Issues](https://github.com/lfnovo/open-notebook/issues)

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=lfnovo/open-notebook&type=date&legend=top-left)](https://www.star-history.com/#lfnovo/open-notebook&type=date&legend=top-left)


## Provider Support Matrix

Thanks to the [Esperanto](https://github.com/lfnovo/esperanto) library, we support this providers out of the box!

| Provider     | LLM Support | Embedding Support | Speech-to-Text | Text-to-Speech |
|--------------|-------------|------------------|----------------|----------------|
| OpenAI       | ✅          | ✅               | ✅             | ✅             |
| Anthropic    | ✅          | ❌               | ❌             | ❌             |
| Groq         | ✅          | ❌               | ✅             | ❌             |
| Google (GenAI) | ✅          | ✅               | ❌             | ✅             |
| Vertex AI    | ✅          | ✅               | ❌             | ✅             |
| Ollama       | ✅          | ✅               | ❌             | ❌             |
| Perplexity   | ✅          | ❌               | ❌             | ❌             |
| ElevenLabs   | ❌          | ❌               | ✅             | ✅             |
| Azure OpenAI | ✅          | ✅               | ❌             | ❌             |
| Mistral      | ✅          | ✅               | ❌             | ❌             |
| DeepSeek     | ✅          | ❌               | ❌             | ❌             |
| Voyage       | ❌          | ✅               | ❌             | ❌             |
| xAI          | ✅          | ❌               | ❌             | ❌             |
| OpenRouter   | ✅          | ❌               | ❌             | ❌             |
| OpenAI Compatible* | ✅          | ❌               | ❌             | ❌             |

*Supports LM Studio and any OpenAI-compatible endpoint

## ✨ Key Features

### Core Capabilities
- **🔒 Privacy-First**: Your data stays under your control - no cloud dependencies
- **🎯 Multi-Notebook Organization**: Manage multiple research projects seamlessly
- **📚 Universal Content Support**: PDFs, videos, audio, web pages, Office docs, and more
- **🤖 Multi-Model AI Support**: 16+ providers including OpenAI, Anthropic, Ollama, Google, LM Studio, and more
- **🎙️ Professional Podcast Generation**: Advanced multi-speaker podcasts with Episode Profiles
- **🔍 Intelligent Search**: Full-text and vector search across all your content
- **💬 Context-Aware Chat**: AI conversations powered by your research materials
- **📝 AI-Assisted Notes**: Generate insights or write notes manually

### Advanced Features
- **⚡ Reasoning Model Support**: Full support for thinking models like DeepSeek-R1 and Qwen3
- **🔧 Content Transformations**: Powerful customizable actions to summarize and extract insights
- **🌐 Comprehensive REST API**: Full programmatic access for custom integrations [![API Docs](https://img.shields.io/badge/API-Documentation-blue?style=flat-square)](http://localhost:5055/docs)
- **🔐 Optional Password Protection**: Secure public deployments with authentication
- **📊 Fine-Grained Context Control**: Choose exactly what to share with AI models
- **📎 Citations**: Get answers with proper source citations


## Podcast Feature

[![Check out our podcast sample](https://img.youtube.com/vi/D-760MlGwaI/0.jpg)](https://www.youtube.com/watch?v=D-760MlGwaI)

## 📚 Documentation

### Getting Started
- **[📖 Introduction](docs/0-START-HERE/index.md)** - Learn what Open Notebook offers
- **[⚡ Quick Start](docs/0-START-HERE/quick-start.md)** - Get up and running in 5 minutes
- **[🔧 Installation](docs/1-INSTALLATION/index.md)** - Comprehensive setup guide
- **[🎯 Your First Notebook](docs/0-START-HERE/first-notebook.md)** - Step-by-step tutorial

### User Guide
- **[📱 Interface Overview](docs/3-USER-GUIDE/interface-overview.md)** - Understanding the layout
- **[📚 Notebooks](docs/3-USER-GUIDE/notebooks.md)** - Organizing your research
- **[📄 Sources](docs/3-USER-GUIDE/sources.md)** - Managing content types
- **[📝 Notes](docs/3-USER-GUIDE/notes.md)** - Creating and managing notes
- **[💬 Chat](docs/3-USER-GUIDE/chat.md)** - AI conversations
- **[🔍 Search](docs/3-USER-GUIDE/search.md)** - Finding information

### Advanced Topics
- **[🎙️ Podcast Generation](docs/2-CORE-CONCEPTS/podcasts.md)** - Create professional podcasts
- **[🔧 Content Transformations](docs/2-CORE-CONCEPTS/transformations.md)** - Customize content processing
- **[🤖 AI Models](docs/4-AI-PROVIDERS/index.md)** - AI model configuration
- **[🔌 MCP Integration](docs/5-CONFIGURATION/mcp-integration.md)** - Connect with Claude Desktop, VS Code and other MCP clients
- **[🔧 REST API Reference](docs/7-DEVELOPMENT/api-reference.md)** - Complete API documentation
- **[🔐 Security](docs/5-CONFIGURATION/security.md)** - Password protection and privacy
- **[🚀 Deployment](docs/1-INSTALLATION/index.md)** - Complete deployment guides for all scenarios

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🔄 Tính năng Transformations (Chuyển đổi)

### Transformations là gì?

**Transformations** (Chuyển đổi) là công cụ **xử lý hàng loạt bằng AI** — cho phép bạn áp dụng cùng một phân tích cho nhiều nguồn (sources) cùng lúc. Thay vì hỏi đi hỏi lại cùng một câu hỏi trong Chat, bạn định nghĩa một **mẫu prompt** (template) rồi chạy nó trên các nguồn. Kết quả được lưu tự động thành **ghi chú có cấu trúc** trong notebook.

**Ví dụ đơn giản:** Bạn có 10 bài viết và muốn tóm tắt từng bài. Thay vì chat 10 lần, bạn tạo 1 transformation "Tóm tắt" rồi áp dụng cho tất cả — mỗi bài tự động tạo ra một ghi chú tóm tắt.

---

### Khi nào dùng Transformations? (So sánh Chat, Ask, Transformations)

| Tình huống | Dùng | Lý do |
|------------|------|-------|
| Muốn hội thoại khám phá, hỏi tiếp | **Chat** | Hội thoại qua lại, bạn chọn ngữ cảnh |
| Cần câu trả lời toàn diện cho một câu hỏi phức tạp | **Ask (Hỏi)** | Hệ thống tự tìm nguồn liên quan, trả lời một lần |
| Muốn trích xuất cùng thông tin từ nhiều nguồn | **Transformations** | Mẫu tái sử dụng, định dạng nhất quán |
| So sánh hai nguồn cụ thể | **Chat** | Chọn 2 nguồn đó rồi thảo luận |
| Phân loại mỗi nguồn theo tiêu chí X | **Transformations** | Trích xuất phân loại từ từng nguồn |
| Xây dựng cơ sở tri thức | **Transformations** | Tạo ghi chú cấu trúc nhất quán |

> 💡 **Quy tắc nhanh:** Nếu bạn cần làm **cùng một việc** cho **nhiều nguồn** → dùng **Transformations**. Nếu cần **hội thoại** → dùng **Chat**. Nếu cần **tìm kiếm toàn diện** → dùng **Ask**.

---

### Hướng dẫn sử dụng từng bước

#### 1. Xem danh sách Transformations

```
1. Vào notebook của bạn
2. Nhấn "Transformations" trong thanh điều hướng
3. Xem danh sách các mẫu có sẵn (built-in) và mẫu tùy chỉnh
```

#### 2. Tạo Transformation mới

```
1. Vào trang "Transformations"
2. Nhấn "Create New" (Tạo mới)
3. Điền thông tin:
   - Name: Tên ngắn (ví dụ: "academic-analysis")
   - Title: Tiêu đề hiển thị (ví dụ: "Phân tích bài báo học thuật")
   - Description: Mô tả ngắn mục đích
   - Prompt: Nội dung prompt (mẫu AI sẽ thực thi)
4. Nhấn "Save" (Lưu)
```

#### 3. Chỉnh sửa Transformation

```
1. Vào trang "Transformations"
2. Tìm mẫu cần sửa
3. Nhấn "Edit" (Chỉnh sửa)
4. Cập nhật prompt hoặc thông tin
5. Nhấn "Save" (Lưu)
```

#### 4. Xóa Transformation

```
1. Vào trang "Transformations"
2. Tìm mẫu cần xóa
3. Nhấn "Delete" (Xóa)
4. Xác nhận
```

#### 5. Thực thi (chạy) Transformation trên nguồn

```
1. Chọn nguồn (source) cần xử lý:
   - Từ bảng Sources, nhấn menu (⋮) → "Transform"
   - Hoặc vào trang Transformations → chọn nguồn
2. Chọn mẫu transformation muốn áp dụng
3. Chọn model AI (ví dụ: GPT-4o, Claude Sonnet...)
4. Nhấn "Apply" (Áp dụng)
5. Đợi xử lý (30 giây - vài phút tùy độ dài nguồn)
6. Kết quả tự động lưu thành ghi chú mới trong notebook
```

**Thời gian xử lý ước tính:**

| Số nguồn | Thời gian ước tính |
|----------|-------------------|
| 1 nguồn | 30 giây - 1 phút |
| 5 nguồn | 2-3 phút |
| 10 nguồn | 4-5 phút |
| 20+ nguồn | 8-10 phút |

---

### Ví dụ mẫu Prompt thực tế

#### Mẫu 1: Tóm tắt nội dung

```
Tóm tắt nội dung này trong 200-300 từ:

1. **Ý chính**: Nội dung này nói về vấn đề gì?
2. **Luận điểm chính**: 3-5 điểm quan trọng nhất (dạng bullet)
3. **Kết luận**: Kết luận hoặc đề xuất chính

Trích dẫn số trang nếu có thể.
```

#### Mẫu 2: Trích xuất khái niệm chính

```
Từ nội dung này, trích xuất các khái niệm và thuật ngữ quan trọng:

1. Liệt kê 5-10 khái niệm/thuật ngữ chính
2. Cho mỗi khái niệm, giải thích ngắn gọn (1-2 câu)
3. Nếu có mối liên hệ giữa các khái niệm, mô tả ngắn

Định dạng: **Thuật ngữ**: Giải thích
```

#### Mẫu 3: Phân tích bài viết/bài báo

```
Phân tích bài viết này và trích xuất:

1. **Câu hỏi nghiên cứu**: Bài viết giải quyết vấn đề gì?
2. **Phương pháp**: Cách tiếp cận được sử dụng
3. **Phát hiện chính**: Kết quả quan trọng (danh sách đánh số)
4. **Hạn chế**: Điểm yếu hoặc thiếu sót
5. **Ứng dụng**: Có thể áp dụng vào thực tế thế nào?

Mỗi phần 2-3 câu. Trích dẫn số trang khi có thể.
```

---

### Mẹo viết Prompt hiệu quả

| Nên | Không nên |
|-----|-----------|
| ✅ "Liệt kê 5 điểm chính dạng bullet" | ❌ "Các điểm chính là gì?" |
| ✅ "Tạo các phần: Tóm tắt, Phương pháp, Kết quả" | ❌ "Nói về bài viết này" |
| ✅ "Trong 200-300 từ, tóm tắt..." | ❌ "Tóm tắt cái này" |
| ✅ "Trích dẫn số trang cho mỗi nhận định" | ❌ (không yêu cầu trích dẫn) |

**4 nguyên tắc vàng:**
1. **Cụ thể về định dạng** — Yêu cầu bullet, bảng, heading rõ ràng
2. **Cấu trúc rõ ràng** — Chia prompt thành các phần/mục
3. **Yêu cầu trích dẫn** — Giúp kiểm chứng kết quả
4. **Giới hạn độ dài** — Tránh kết quả quá dài hoặc quá ngắn

---

### Xử lý lỗi thường gặp

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-------------|-----------|
| Kết quả quá mơ hồ | Prompt chung chung | Viết prompt cụ thể hơn, thêm yêu cầu định dạng |
| Thiếu thông tin quan trọng | Prompt không yêu cầu rõ | Liệt kê cụ thể thông tin cần trích xuất |
| Định dạng không nhất quán giữa các ghi chú | Prompt thiếu hướng dẫn format | Thêm hướng dẫn định dạng rõ ràng (heading, bullet, bảng) |
| Kết quả quá dài/ngắn | Không chỉ định độ dài | Thêm giới hạn số từ hoặc số câu |
| Chuyển đổi không hoàn tất | Nguồn chưa xử lý xong hoặc quá lớn | Kiểm tra nguồn đã processed; thử prompt đơn giản hơn; xử lý từng nguồn |

> 📖 **Tài liệu chi tiết:** Xem thêm hướng dẫn đầy đủ tại [docs/3-USER-GUIDE/transformations.md](docs/3-USER-GUIDE/transformations.md) và so sánh chi tiết giữa Chat, Ask và Transformations tại [docs/2-CORE-CONCEPTS/chat-vs-transformations.md](docs/2-CORE-CONCEPTS/chat-vs-transformations.md).

---

## 🏦 Bộ Prompt Transformations cho Văn bản Nội bộ Agribank

Dưới đây là bộ 5 prompt Transformations chuyên biệt để xử lý văn bản nội bộ Agribank — bao gồm quyết định, quy chế, quy định, hướng dẫn, và các văn bản sửa đổi/bổ sung/thay thế.

> 💡 **Cách sử dụng:** Tạo từng prompt bên dưới thành một Transformation riêng (vào **Transformations → Create New**), sau đó áp dụng cho các nguồn văn bản đã upload.

---

### Prompt 1: Trích xuất Metadata văn bản

**Mục đích:** Trích xuất thông tin nhận dạng cơ bản của văn bản.

**Name:** `agribank-metadata`  
**Title:** Trích xuất metadata văn bản Agribank

```
Phân tích văn bản này và trích xuất các thông tin sau theo định dạng bảng:

| Trường | Giá trị |
|--------|---------|
| Số hiệu văn bản | (VD: 1234/QĐ-NHNo-CSTT) |
| Loại văn bản | (Quyết định / Quy chế / Quy định / Hướng dẫn / Thông báo / Công văn) |
| Cơ quan ban hành | (VD: Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam) |
| Ngày ban hành | (DD/MM/YYYY) |
| Ngày hiệu lực | (DD/MM/YYYY, hoặc "kể từ ngày ký" nếu ghi vậy) |
| Người ký | (Họ tên, chức vụ) |
| Phạm vi áp dụng | (Toàn hệ thống / Chi nhánh / Phòng ban cụ thể) |
| Lĩnh vực | (Tín dụng / Kế toán / Nhân sự / Công nghệ / Khác) |

Nếu không tìm thấy thông tin cho trường nào, ghi "N/A".
Trích dẫn vị trí trong văn bản nơi tìm thấy thông tin (số trang, điều khoản nếu có).
```

---

### Prompt 2: Phân tích Quan hệ văn bản (Sửa đổi / Bổ sung / Thay thế)

**Mục đích:** Xác định văn bản này có quan hệ gì với các văn bản khác (sửa đổi, bổ sung, thay thế).

**Name:** `agribank-doc-relations`  
**Title:** Phân tích quan hệ sửa đổi/bổ sung/thay thế

```
Phân tích văn bản này và xác định mối quan hệ với các văn bản khác:

## 1. Loại văn bản
Xác định đây là:
- [ ] Văn bản GỐC (ban hành lần đầu, không sửa đổi/thay thế văn bản nào)
- [ ] Văn bản SỬA ĐỔI, BỔ SUNG (thay đổi một phần văn bản cũ)
- [ ] Văn bản THAY THẾ (thay thế hoàn toàn văn bản cũ)

## 2. Văn bản bị ảnh hưởng
Nếu là văn bản sửa đổi/bổ sung/thay thế, liệt kê:

| Văn bản bị ảnh hưởng | Số hiệu | Ngày ban hành gốc | Tính chất (Sửa đổi / Bổ sung / Thay thế / Bãi bỏ) |
|----------------------|---------|-------------------|------------------------------------------------------|

## 3. Chi tiết điều khoản bị ảnh hưởng
Liệt kê từng điều khoản bị sửa đổi/bổ sung/bãi bỏ:

| Điều khoản | Thuộc văn bản | Tính chất thay đổi | Tóm tắt nội dung thay đổi |
|------------|--------------|---------------------|---------------------------|

## 4. Căn cứ pháp lý
Liệt kê các văn bản được viện dẫn trong phần "Căn cứ" (nếu có):
- Văn bản 1: ...
- Văn bản 2: ...

Nếu đây là văn bản gốc, không sửa đổi/thay thế văn bản nào, ghi rõ: "Đây là văn bản gốc, ban hành lần đầu."
Trích dẫn điều khoản và số trang cho mỗi nhận định.
```

---

### Prompt 3: Tóm tắt Nội dung quy định

**Mục đích:** Tóm tắt các quy định, điều khoản, quy trình chính trong văn bản.

**Name:** `agribank-content-summary`  
**Title:** Tóm tắt nội dung quy định Agribank

```
Tóm tắt nội dung chính của văn bản Agribank này:

## 1. Tổng quan
Mô tả mục đích và phạm vi của văn bản trong 2-3 câu.

## 2. Các quy định chính
Liệt kê theo từng chương/phần (nếu có):

### [Tên chương/phần]
- **Điều X**: Tóm tắt nội dung (1-2 câu)
- **Điều Y**: Tóm tắt nội dung (1-2 câu)

## 3. Nghĩa vụ và trách nhiệm
Liệt kê ai phải làm gì:

| Đối tượng | Nghĩa vụ/Trách nhiệm | Điều khoản |
|-----------|----------------------|------------|

## 4. Quy trình (nếu có)
Mô tả các bước quy trình chính theo thứ tự:
1. Bước 1: ...
2. Bước 2: ...

## 5. Mức xử lý vi phạm (nếu có)
Tóm tắt các hình thức xử lý khi vi phạm.

## 6. Điểm đáng lưu ý
Liệt kê 3-5 điểm quan trọng nhất mà người đọc cần nhớ.

Trích dẫn số điều khoản cho mỗi nội dung.
```

---

### Prompt 4: Xác định Hiệu lực văn bản

**Mục đích:** Phân tích trạng thái hiệu lực, điều kiện áp dụng, và các văn bản bị bãi bỏ.

**Name:** `agribank-validity`  
**Title:** Xác định hiệu lực văn bản Agribank

```
Phân tích hiệu lực pháp lý của văn bản này:

## 1. Thông tin hiệu lực

| Trường | Giá trị |
|--------|---------|
| Ngày có hiệu lực | (DD/MM/YYYY hoặc "kể từ ngày ký") |
| Điều kiện có hiệu lực | (Không điều kiện / Có điều kiện — mô tả) |
| Phạm vi hiệu lực | (Toàn hệ thống / Chi nhánh / Đơn vị cụ thể) |

## 2. Văn bản bị bãi bỏ / hết hiệu lực
Liệt kê tất cả văn bản được tuyên bố bãi bỏ hoặc hết hiệu lực bởi văn bản này:

| Số hiệu văn bản bị bãi bỏ | Ngày ban hành gốc | Bãi bỏ toàn bộ hay một phần | Điều khoản quy định việc bãi bỏ |
|---------------------------|-------------------|------------------------------|-------------------------------|

## 3. Điều khoản chuyển tiếp (nếu có)
Mô tả các quy định chuyển tiếp giữa văn bản cũ và mới:
- Thời hạn chuyển tiếp: ...
- Quy định áp dụng trong thời gian chuyển tiếp: ...

## 4. Trạng thái tổng hợp
Kết luận trạng thái hiệu lực của văn bản:
- [ ] Đang có hiệu lực toàn bộ
- [ ] Đã bị sửa đổi một phần (bởi văn bản: ...)
- [ ] Đã bị thay thế hoàn toàn (bởi văn bản: ...)
- [ ] Đã hết hiệu lực

Trích dẫn điều khoản cụ thể cho mỗi nhận định. Nếu không có thông tin về hiệu lực, ghi "Không tìm thấy quy định về hiệu lực trong văn bản."
```

---

### Prompt 5: So sánh Thay đổi giữa các văn bản

**Mục đích:** Liệt kê chi tiết các điểm thay đổi khi văn bản sửa đổi/bổ sung văn bản gốc.

**Name:** `agribank-change-comparison`  
**Title:** So sánh thay đổi văn bản Agribank

```
Phân tích văn bản sửa đổi/bổ sung này và liệt kê CHI TIẾT tất cả các thay đổi:

## 1. Tổng quan thay đổi
- Văn bản sửa đổi: (số hiệu, ngày ban hành)
- Văn bản gốc bị sửa đổi: (số hiệu, ngày ban hành)
- Tổng số điều khoản thay đổi: X
- Tổng số điều khoản bổ sung mới: X
- Tổng số điều khoản bãi bỏ: X

## 2. Chi tiết từng thay đổi

Liệt kê theo bảng:

| # | Điều khoản | Loại thay đổi | Nội dung CŨ (tóm tắt) | Nội dung MỚI (tóm tắt) | Lý do thay đổi (nếu ghi) |
|---|-----------|---------------|----------------------|----------------------|--------------------------|

Với loại thay đổi:
- **Sửa đổi**: Thay đổi nội dung điều khoản có sẵn
- **Bổ sung**: Thêm nội dung mới vào điều khoản có sẵn
- **Thêm mới**: Thêm điều khoản hoàn toàn mới
- **Bãi bỏ**: Xóa bỏ điều khoản

## 3. Tác động chính
Tóm tắt 3-5 thay đổi có tác động lớn nhất và lý do.

## 4. Điều khoản giữ nguyên
Liệt kê các phần/chương KHÔNG bị thay đổi (nếu có thể xác định).

Nếu đây KHÔNG phải là văn bản sửa đổi/bổ sung (mà là văn bản gốc), ghi: "Văn bản này không phải văn bản sửa đổi/bổ sung. Không có so sánh thay đổi."
Trích dẫn số điều khoản và trang cho mỗi thay đổi.
```

---

### 📋 Quy trình sử dụng kết hợp các Prompt

Để khai thác tối đa bộ prompt, áp dụng theo thứ tự:

```
Bước 1: Chạy "Trích xuất metadata" cho TẤT CẢ văn bản
         → Có bảng tổng quan toàn bộ văn bản

Bước 2: Chạy "Phân tích quan hệ văn bản" cho TẤT CẢ văn bản
         → Biết văn bản nào sửa đổi/thay thế văn bản nào

Bước 3: Chạy "Xác định hiệu lực" cho TẤT CẢ văn bản
         → Biết văn bản nào còn hiệu lực, văn bản nào đã hết

Bước 4: Chạy "Tóm tắt nội dung" cho các văn bản CÒN HIỆU LỰC
         → Có tóm tắt đầy đủ các quy định đang áp dụng

Bước 5: Chạy "So sánh thay đổi" cho các văn bản SỬA ĐỔI/BỔ SUNG
         → Biết chính xác thay đổi gì so với bản gốc
```

> ⚠️ **Lưu ý quan trọng:**
> - Kết quả AI mang tính tham khảo — luôn đối chiếu với văn bản gốc
> - Với văn bản dài (>50 trang), nên chia nhỏ hoặc dùng prompt đơn giản hơn
> - Nên chạy Prompt 1 & 2 trước để có cái nhìn tổng quan trước khi phân tích chi tiết

---

## 🗺️ Roadmap

### Upcoming Features
- **Live Front-End Updates**: Real-time UI updates for smoother experience
- **Async Processing**: Faster UI through asynchronous content processing
- **Cross-Notebook Sources**: Reuse research materials across projects
- **Bookmark Integration**: Connect with your favorite bookmarking apps

### Recently Completed ✅
- **Next.js Frontend**: Modern React-based frontend with improved performance
- **Comprehensive REST API**: Full programmatic access to all functionality
- **Multi-Model Support**: 16+ AI providers including OpenAI, Anthropic, Ollama, LM Studio
- **Advanced Podcast Generator**: Professional multi-speaker podcasts with Episode Profiles
- **Content Transformations**: Powerful customizable actions for content processing
- **Enhanced Citations**: Improved layout and finer control for source citations
- **Multiple Chat Sessions**: Manage different conversations within notebooks

See the [open issues](https://github.com/lfnovo/open-notebook/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## 📖 Need Help?
- **🤖 AI Installation Assistant**: We have a [CustomGPT built to help you install Open Notebook](https://chatgpt.com/g/g-68776e2765b48191bd1bae3f30212631-open-notebook-installation-assistant) - it will guide you through each step!
- **New to Open Notebook?** Start with our [Getting Started Guide](docs/0-START-HERE/index.md)
- **Need installation help?** Check our [Installation Guide](docs/1-INSTALLATION/index.md)
- **Want to see it in action?** Try our [Quick Start Tutorial](docs/0-START-HERE/quick-start.md)

## 🤝 Community & Contributing

### Join the Community
- 💬 **[Discord Server](https://discord.gg/37XJPXfz2w)** - Get help, share ideas, and connect with other users
- 🐛 **[GitHub Issues](https://github.com/lfnovo/open-notebook/issues)** - Report bugs and request features
- ⭐ **Star this repo** - Show your support and help others discover Open Notebook

### Contributing
We welcome contributions! We're especially looking for help with:
- **Frontend Development**: Help improve our modern Next.js/React UI
- **Testing & Bug Fixes**: Make Open Notebook more robust
- **Feature Development**: Build the coolest research tool together
- **Documentation**: Improve guides and tutorials

**Current Tech Stack**: Python, FastAPI, Next.js, React, SurrealDB
**Future Roadmap**: Real-time updates, enhanced async processing

See our [Contributing Guide](CONTRIBUTING.md) for detailed information on how to get started.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## 📄 License

Open Notebook is MIT licensed. See the [LICENSE](LICENSE) file for details.


**Community Support**:
- 💬 [Discord Server](https://discord.gg/37XJPXfz2w) - Get help, share ideas, and connect with users
- 🐛 [GitHub Issues](https://github.com/lfnovo/open-notebook/issues) - Report bugs and request features
- 🌐 [Website](https://www.open-notebook.ai) - Learn more about the project

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/lfnovo/open-notebook.svg?style=for-the-badge
[contributors-url]: https://github.com/lfnovo/open-notebook/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/lfnovo/open-notebook.svg?style=for-the-badge
[forks-url]: https://github.com/lfnovo/open-notebook/network/members
[stars-shield]: https://img.shields.io/github/stars/lfnovo/open-notebook.svg?style=for-the-badge
[stars-url]: https://github.com/lfnovo/open-notebook/stargazers
[issues-shield]: https://img.shields.io/github/issues/lfnovo/open-notebook.svg?style=for-the-badge
[issues-url]: https://github.com/lfnovo/open-notebook/issues
[license-shield]: https://img.shields.io/github/license/lfnovo/open-notebook.svg?style=for-the-badge
[license-url]: https://github.com/lfnovo/open-notebook/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/lfnovo
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white
[Next-url]: https://nextjs.org/
[React]: https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black
[React-url]: https://reactjs.org/
[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[LangChain]: https://img.shields.io/badge/LangChain-3A3A3A?style=for-the-badge&logo=chainlink&logoColor=white
[LangChain-url]: https://www.langchain.com/
[SurrealDB]: https://img.shields.io/badge/SurrealDB-FF5E00?style=for-the-badge&logo=databricks&logoColor=white
[SurrealDB-url]: https://surrealdb.com/

# Chạy local
docker compose up -d surrealdb

backend: uv run --env-file .env python run_api.py
woker: uv run --env-file .env surreal-commands-worker --import-modules commands
frontend: cd frontend && npm run dev

git add . && git commit -m "Update chat components and source chat API" && git push origin main

# Kéo code về: git pull origin main
Bước 1: Truy cập vào VPS
ssh root@your-server-ip
Bước 2: Di chuyển vào thư mục Open Notebook
cd /root/5400-NoteBook_final
Bước 3: Dừng các container đang chạy
docker compose down
Bước 4: Kéo code mới nhất từ GitHub
git pull origin main
Bước 5: Khởi động lại các container
docker compose up -d  hoặc
docker compose up -d --build


Xem log trên VPS:
docker compose logs -f
