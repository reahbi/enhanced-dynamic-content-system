# 🚀 Enhanced Dynamic Content System v6.1

AI 기반 학술 논문 콘텐츠 생성 시스템 - Google Gemini API를 활용한 신뢰성 있는 건강/피트니스 콘텐츠 자동 생성 플랫폼

## 📋 주요 기능

- **🎯 실용적 카테고리 자동 생성**: 사용자 관심사에 맞는 즉시 클릭하고 싶은 카테고리 생성
- **📚 논문 기반 콘텐츠**: 100% 실제 학술 논문을 기반으로 한 신뢰성 있는 콘텐츠
- **🤖 Gemini 2.0 Flash 활용**: Native Thinking Mode로 심층적인 콘텐츠 분석
- **📝 멀티포맷 지원**: 숏츠 스크립트(45-60초), 상세 아티클(2000-3000자), 종합 리포트
- **⭐ 품질 평가 시스템**: A+ ~ C 등급의 논문 품질 자동 평가

## 🛠️ 기술 스택

### Backend
- Python 3.10+ with FastAPI
- SQLite Database (내장, 별도 설치 불필요)
- Google Gemini API
- SQLAlchemy ORM

### Frontend
- React 18 with TypeScript
- Tailwind CSS (NOT Material-UI)
- Redux Toolkit
- Vite

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 1. 저장소 클론
git clone <repository-url>
cd logic

# 2. 환경 변수 설정
# .env 파일에 Gemini API 키 추가
GEMINI_API_KEY=your-api-key-here
```

### 2. Backend 실행

```bash
cd backend
python setup.py  # 또는 수동으로 venv 생성 및 패키지 설치
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

Backend API: http://localhost:8000/docs

### 3. Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

Frontend App: http://localhost:3000

## 📁 프로젝트 구조

```
logic/
├── backend/                # FastAPI 백엔드
│   ├── app/
│   │   ├── api/           # API 엔드포인트
│   │   ├── models/        # 데이터베이스 모델
│   │   └── services/      # 비즈니스 로직
│   ├── data/              # SQLite 데이터베이스
│   └── requirements.txt
│
├── frontend/              # React 프론트엔드
│   ├── src/
│   │   ├── components/    # UI 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   └── store/         # Redux 상태 관리
│   └── package.json
│
├── test_results/          # 테스트 결과
├── CLAUDE.md             # Claude Code 가이드
├── PRODUCT_PRD.md        # 제품 요구사항 문서
└── DEVELOPMENT_MILESTONES.md  # 개발 마일스톤

```

## 💡 사용 방법

1. **카테고리 생성**: 관심 키워드를 입력하면 AI가 실용적인 카테고리 5개를 자동 생성
2. **논문 검색**: 선택한 카테고리에서 세부 주제를 입력하면 관련 논문 자동 검색
3. **콘텐츠 생성**: 검색된 논문을 기반으로 원하는 형식의 콘텐츠 생성
4. **라이브러리 관리**: 생성된 콘텐츠 조회, 필터링, 다운로드

## 🔧 개발 가이드

### API 엔드포인트

- `POST /api/v1/categories/generate` - 카테고리 생성
- `POST /api/v1/papers/discover` - 논문 검색
- `POST /api/v1/content/generate` - 콘텐츠 생성
- `GET /api/v1/content` - 콘텐츠 목록 조회

### 주요 설정

- **Gemini Model**: `gemini-2.0-flash-exp` (최신 모델 사용)
- **Database**: SQLite (`./backend/data/app.db`)
- **Cache**: File-based (`./backend/cache/`)

## 📊 성능 지표

- 카테고리 생성: ~2초
- 논문 검색: ~3-5초
- 콘텐츠 생성: ~5-10초 (형식별)
- 품질 점수: 평균 80점 이상

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 라이선스

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- FastAPI for high-performance backend
- React & Tailwind CSS for modern UI

---

**Enhanced Dynamic Content System v6.1** - AI와 학술 논문의 완벽한 결합으로 신뢰할 수 있는 콘텐츠를 자동 생성합니다.