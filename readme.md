# 🚀 Assist AI — Personal AI Assistant (Django + Transformer Model)

Assist AI is a modern ChatGPT-like web application built using **Django**, **Bootstrap**, and a **local transformer AI model** (Phi-2 / Llama / GGUF / any model you plug in).  
It supports real-time chat, conversation history, renaming chats, deleting chats, system/dark/light themes, and clean minimal UI similar to ChatGPT.

---

## ✨ FEATURES

### 🧠 AI Features
- Local transformer-based assistant (Phi-2 / TinyLlama or any HF model)
- Fast response with short, clean English
- Strict ChatGPT-style behavior
- Configurable system prompt
- Noise removal (`<s>`, `</s>`, `[USER]`, etc.)

### 💬 Chat System
- Multiple conversations
- Auto-rename chats
- Search chat history
- Right-click rename/delete
- Chat splash screen: *“Meet Assist AI, your personal AI assistant”*

### 🎨 UI (ChatGPT-like)
- Dark Mode / Light Mode / System Theme
- Smooth animations
- Responsive Bootstrap UI
- Sidebar icons: New Chat, History, Settings
- Auto-scroll chat window

---

## 🛠️ TECH STACK

| Component | Technology |
|----------|------------|
| Backend | Django 5.x |
| AI Engine | Transformers (Microsoft Phi-2 / custom) |
| Frontend | HTML, Bootstrap 5, JS |
| Database | SQLite / MySQL |
| Model Format | `.bin`, `.safetensors`, HuggingFace models |

---

## 📂 PROJECT STRUCTURE

```
Assist_AI/
│── ai/
│   ├── views.py
│   ├── models.py
│   ├── urls.py
│   ├── templates/
│   │   └── ai/chat.html
│── requirements.txt
│── manage.py
└── README.md
```

---

## 🚀 INSTALLATION

### 1️⃣ Clone the repository
```sh
git clone https://github.com/YOUR_USERNAME/Assist_AI.git
cd Assist_AI
```

### 2️⃣ Create virtual environment
```sh
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Run migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Start development server
```sh
python manage.py runserver
```

---

## 🤖 USING YOUR OWN AI MODEL

Change only **one file**:

### `ai/ai_engine.py`
```python
MODEL_NAME = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
```

You can replace it with any HuggingFace model.

---

## 🧩 API ENDPOINTS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/chat/conversations/` | Get all chats |
| POST | `/chat/new/` | Create new chat |
| GET | `/chat/conversation/<id>/` | Load conversation |
| POST | `/chat/rename/<id>/` | Rename chat |
| POST | `/chat/delete/<id>/` | Delete chat |
| POST | `/chat/ask/` | Chat with AI |

---

## 🌓 THEME ENGINE

Assist AI supports:
- **Light Theme**
- **Dark Theme**
- **System Auto Mode**

Theme preference is saved in **localStorage**.

---

## 📸 UI PREVIEW (description)

- Left sidebar with icons
- Right-click conversation options
- Settings modal
- Clean message bubbles
- Auto-scroll chat feed

---

## 🧑‍💻 CONTRIBUTING

Pull requests are welcome!  
If you want to add:
- More themes
- Model selection menu
- Voice input
- Streaming chat responses  
Let me know — contributions are appreciated ❤️

---

## 📜 LICENSE

MIT License © 2025 — You are free to use, modify, and distribute.

---

# ⭐ If you like Assist AI — give the repo a Star on GitHub!