# Enhanced Dynamic Content System v6.1 - Backend

## 🚀 Quick Start

### 1. Setup
```bash
# Run the setup script
python setup.py

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the parent directory with:
```env
GEMINI_API_KEY=your-api-key-here
```

### 3. Run the Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Test Gemini integration
python test_api.py
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models/          # Database models
│   │   ├── __init__.py
│   │   └── database.py
│   ├── api/             # API endpoints
│   │   ├── __init__.py
│   │   ├── categories.py
│   │   ├── papers.py
│   │   └── content.py
│   └── services/        # Business logic
│       ├── __init__.py
│       └── gemini_client.py
├── data/                # SQLite database
├── cache/               # File-based cache
├── requirements.txt
├── setup.py
└── README.md
```

## 🔧 Key Features

- **FastAPI** for high-performance REST API
- **SQLite** database (no installation required)
- **Gemini 2.0 Flash** for AI content generation
- **Native Thinking Mode** for enhanced content quality
- **Automatic paper discovery** with quality validation
- **Multi-format content generation** (shorts, articles, reports)

## 🛠️ Development

### Add New Endpoints
1. Create a new router in `app/api/`
2. Import and include it in `app/main.py`

### Database Migrations
SQLite automatically creates tables on startup. To reset:
```bash
rm data/app.db
# Restart the server
```

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `OUTPUT_FOLDER`: Content output directory (default: generated_content)