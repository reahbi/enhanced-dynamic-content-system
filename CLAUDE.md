# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a **complete full-stack implementation** of the Enhanced Dynamic Content System v6.1 - a hybrid paper-based content generation system that uses Google's Gemini API to create fitness and health content based on academic research papers. The system generates multiple content formats (shorts scripts, articles, reports) across 10 specialized categories.

### 🏗️ Current Implementation Status (Week 10 Complete)
- ✅ **Backend**: FastAPI-based REST API with 6 major modules
- ✅ **Frontend**: React TypeScript with Tailwind CSS and Redux Toolkit
- ✅ **Services**: 15+ specialized services including Native Thinking Mode
- ✅ **API**: 30+ endpoints across categories, papers, contents, health, cache, analytics
- ✅ **Development Environment**: Complete setup with scripts and configurations
- ✅ **Server**: Running at http://127.0.0.1:8000 (Backend) and http://localhost:5173 (Frontend)

## Key Architecture Components

### Core System Design
- **Ultra-Simple Paper Discovery**: Uses Gemini API to find relevant academic papers with automatic filtering for paper-less topics
- **Enhanced Content Generation**: Leverages Gemini's Native Thinking Mode for detailed content analysis and generation
- **Category System**: 10 predefined fitness/health categories with specialized content approaches
- **Hybrid Workflow**: Combines simple paper discovery with sophisticated content generation

### Content Categories (10 total)
Basic categories:
- 💪 근성장 & 근력 (Muscle Growth & Strength)
- 🔥 다이어트 & 체지방감소 (Diet & Fat Loss)  
- 🍽️ 식단 & 영양 (Nutrition & Diet)
- 🏃 운동방법 & 기법 (Exercise Methods & Techniques)
- 📋 운동계획 & 설계 (Workout Planning & Design)

Extended categories:
- 🧘 회복 & 컨디셔닝 (Recovery & Conditioning)
- 🧠 멘탈 & 동기부여 (Mindset & Motivation)
- 🚑 부상 방지 & 재활 (Injury Prevention & Rehab)
- 💡 운동 장비 & 보조제 (Gear & Supplements)
- 👩‍🏫 특정 그룹별 맞춤 정보 (For Specific Groups)

## Implementation Approach

### Main Classes (as designed)
```python
class HybridPaperContentSystem:
    # Main orchestrator combining all components
    
class UltraSimplePaperDiscovery:
    # Handles paper discovery with automatic filtering
    
class EnhancedContentGenerator:
    # Generates specialized content using Native Thinking Mode
    
class IntegratedCategorySystem:
    # Manages the 10-category structure
```

### Content Generation Pipeline
1. User selects from 10 predefined categories
2. Gemini discovers papers and generates creative topics for the category
3. System automatically filters out topics without valid papers (max 15 attempts)
4. User selects preferred topic
5. Enhanced generation creates multiple content formats using Native Thinking Mode
6. Results saved as organized files

## Gemini API Integration

The system extensively uses Google's Gemini API for:
- Paper discovery and topic generation
- Content analysis using Native Thinking Mode
- Category-specific content generation
- Automatic quality filtering

### Key API Patterns
- Use `google.genai.Client` for API interactions
- **Using Gemini 2.5 Flash model (`gemini-2.5-flash`) for cost optimization**
- Implement Native Thinking Mode with `<thinking>` tags in prompts
- Category-specific prompt engineering for specialized content
- Automatic retry mechanisms for paper discovery
- **Token usage tracking and cost calculation enabled**

### Model Configuration
```python
# Using Gemini 2.5 Flash for cost optimization:
self.model_name = "gemini-2.5-flash"

# Token tracking and cost calculation is enabled
# Pricing (per 1M tokens):
# - Input: $0.075 (up to 1M), $0.15 (over 1M)
# - Output: $0.30 (up to 1M), $0.60 (over 1M)
# - Conversion rate: 1 USD = 1,300 KRW
```

## File Organization

The repository contains:
- `Enhanced_Content_Generator_상세구현.md`: Detailed implementation of the content generator
- `geminiapi.md`: Collection of Gemini API usage examples and patterns
- `하이브리드_Paper-Based_Content_System_v5_설계서.md`: System architecture and design specifications
- `PRODUCT_PRD.md`: Complete Product Requirements Document
- `DEVELOPMENT_MILESTONES.md`: 12-month development roadmap
- `CATEGORY_IMPROVEMENT_GUIDE.md`: Category generation optimization guide
- `test_results/`: Directory containing system test results and performance data

## Technology Stack (Updated for Solo Development)

### Backend Technology
```python
# Core Backend Stack
Language: Python 3.10+
Framework: FastAPI 0.104+
AI Integration: Google Gemini API 1.24+
Database: SQLite (built-in with Python)
ORM: SQLAlchemy 2.0+
Cache: File-based caching (./cache/ directory)
```

### Frontend Technology
```javascript
// Frontend Stack
Framework: React 18+ with TypeScript
Styling: Tailwind CSS v3 (NOT Material-UI)
Component Library: Headless UI (Tailwind compatible)
State Management: Redux Toolkit
Build Tool: Vite
```

### Database Schema (SQLite)
```sql
-- Main tables for SQLite
CREATE TABLE categories (
    id TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    emoji VARCHAR(10),
    practicality_score REAL,
    interest_score REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE papers (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    journal VARCHAR(255),
    publication_year INTEGER,
    doi VARCHAR(255),
    impact_factor REAL,
    citations INTEGER,
    quality_score REAL,
    quality_grade VARCHAR(10),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE contents (
    id TEXT PRIMARY KEY,
    category_id TEXT REFERENCES categories(id),
    paper_id TEXT REFERENCES papers(id),
    content_type VARCHAR(50), -- 'shorts', 'article', 'report'
    title VARCHAR(500),
    content TEXT,
    thinking_process TEXT,
    quality_score REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### Development Environment (Solo Developer) - CURRENT STRUCTURE
```bash
# Actual Project Structure (as implemented)
/home/nosky/logic/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API 모듈 (6개)
│   │   │   ├── categories.py  # 카테고리 관리 API
│   │   │   ├── papers.py      # 논문 검색/평가 API
│   │   │   ├── contents.py    # 콘텐츠 생성 API
│   │   │   ├── health.py      # 헬스체크 API
│   │   │   ├── cache.py       # 캐시 관리 API
│   │   │   └── analytics.py   # 분석/통계 API
│   │   ├── services/          # 비즈니스 로직 (15개 서비스)
│   │   │   ├── content_generators/  # 콘텐츠 생성기
│   │   │   │   ├── base_generator.py
│   │   │   │   ├── shorts_generator.py
│   │   │   │   ├── article_generator.py
│   │   │   │   └── report_generator.py
│   │   │   ├── thinking/            # Native Thinking Mode
│   │   │   │   ├── native_thinking_engine.py
│   │   │   │   ├── prompt_engineering.py
│   │   │   │   └── thinking_analyzer.py
│   │   │   ├── advanced_cache_manager.py
│   │   │   ├── paper_quality_evaluator.py
│   │   │   ├── performance_optimizer.py
│   │   │   └── system_monitor.py
│   │   └── utils/             # 유틸리티
│   │       └── token_tracker.py  # 토큰 사용량 추적 및 비용 계산
│   ├── main.py               # FastAPI 메인 앱
│   ├── minimal_main.py       # 최소 실행용
│   ├── run_server.py         # 서버 실행기
│   ├── requirements.txt      # 의존성 목록
│   ├── .env                  # 환경 변수 (Gemini API Key 포함)
│   ├── data/                 # SQLite 데이터베이스
│   ├── cache/                # 파일 기반 캐시
│   ├── logs/                 # 로그 파일
│   └── exports/              # 내보내기 파일
├── frontend/                 # React TypeScript Frontend
│   ├── src/
│   │   ├── components/       # React 컴포넌트
│   │   │   ├── CategoryCard.tsx
│   │   │   ├── ContentViewer.tsx
│   │   │   └── Layout.tsx
│   │   ├── pages/           # 페이지 컴포넌트
│   │   │   ├── HomePage.tsx
│   │   │   ├── CategoriesPage.tsx
│   │   │   ├── ContentGeneratorPage.tsx
│   │   │   └── LibraryPage.tsx
│   │   ├── store/           # Redux Toolkit 상태 관리
│   │   │   ├── categoriesSlice.ts
│   │   │   ├── contentSlice.ts
│   │   │   └── index.ts
│   │   ├── App.tsx          # 메인 앱 컴포넌트
│   │   └── main.tsx         # 앱 진입점
│   ├── package.json         # 프론트엔드 의존성
│   ├── vite.config.ts       # Vite 설정
│   ├── tailwind.config.js   # Tailwind CSS 설정
│   └── tsconfig.json        # TypeScript 설정
├── DOCS/                    # 설계 문서들
│   ├── Enhanced_Dynamic_System_v6.1_설계서.md
│   ├── Enhanced_Content_Generator_상세구현.md
│   └── CATEGORY_IMPROVEMENT_GUIDE.md
├── test_results/            # 테스트 결과
├── .env                     # 루트 환경 변수
└── README.md
```

## Development Guidelines

### When implementing the system:
1. **Solo Development Optimized**: Simple, direct execution without Docker complexity
2. **SQLite First**: Use SQLite for local development (no server setup required)
3. **Tailwind CSS Styling**: Use utility-first CSS framework, avoid Material-UI
4. **File-based Caching**: Store cache in ./cache/ directory instead of Redis
5. **Follow the hybrid approach**: keep paper discovery simple, make content generation sophisticated
6. **Implement strict paper validation** - never generate content without valid academic sources
7. **Use category-specific prompting strategies** for each of the 10 categories
8. **Implement the automatic retry mechanism** (max 15 attempts) for paper discovery
9. **Utilize Gemini's Native Thinking Mode** for deep content analysis
10. **Generate multiple content formats**: shorts scripts (45-60 seconds), detailed articles (2000-3000 characters), comprehensive reports

### Environment Setup (CURRENT - READY TO RUN)
```bash
# 🔥 QUICK START - 시스템이 이미 구현되어 있습니다!

# 1. 백엔드 서버 시작 (Gemini API Key 설정됨)
cd /home/nosky/logic/backend
python3 minimal_main.py
# 또는
python3 run_server.py

# 2. 프론트엔드 서버 시작 (별도 터미널)
cd /home/nosky/logic/frontend
npm run dev

# 🌐 접속 주소:
# Backend API: http://127.0.0.1:8000
# API 문서: http://127.0.0.1:8000/docs
# Frontend: http://localhost:5173

# 📦 의존성 설치 (필요시)
# Backend
cd backend && pip3 install -r requirements.txt --user

# Frontend (Node.js 필요)
cd frontend && npm install
```

### 🚀 Current Running Status
- ✅ **Backend Server**: http://127.0.0.1:8000 (실행 중)
- ✅ **Gemini API**: 설정 완료 (API Key 로드됨)
- ✅ **Environment**: development 모드
- ⏳ **Frontend**: 준비 완료 (npm run dev로 시작 가능)

### 📊 API Endpoints Available
```bash
# 카테고리 관리
GET  /api/v1/categories/trending
POST /api/v1/categories/generate

# 논문 검색/평가
POST /api/v1/papers/search
GET  /api/v1/papers/{paper_id}
POST /api/v1/papers/evaluate

# 콘텐츠 생성 (Native Thinking Mode 지원)
POST /api/v1/contents/generate
GET  /api/v1/contents/list
POST /api/v1/contents/batch/generate

# 시스템 모니터링
GET  /api/v1/health/
GET  /api/v1/health/detailed
GET  /api/v1/cache/stats
GET  /api/v1/analytics/overview
```

### Tailwind CSS Usage Guidelines
```javascript
// Example React component with Tailwind
function CategoryCard({ category }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center mb-4">
        <span className="text-2xl mr-3">{category.emoji}</span>
        <h3 className="text-lg font-semibold text-gray-800">{category.name}</h3>
      </div>
      <p className="text-gray-600 text-sm mb-4">{category.description}</p>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">
          실용성: {category.practicality_score}/10
        </span>
        <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
          선택하기
        </button>
      </div>
    </div>
  );
}
```

### Quality Assurance
- **All content must be based on actual academic papers**
- **SQLite data integrity**: Use foreign key constraints and proper indexing
- **Implement automatic filtering** for "no paper" indicators
- **Use paper-first principles** throughout the system
- **Ensure category-specific tone and style** for different content types
- **File-based caching** for improved performance
- **Tailwind CSS consistency** across all UI components