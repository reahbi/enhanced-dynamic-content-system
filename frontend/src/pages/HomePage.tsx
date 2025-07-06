import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="animate-fade-in">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          AI 기반 콘텐츠 생성 시스템
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600">
          학술 논문을 기반으로 신뢰할 수 있는 건강 및 피트니스 콘텐츠를 자동으로 생성합니다.
          <br />
          Gemini 2.0 Flash의 Native Thinking Mode를 활용하여 고품질 콘텐츠를 제공합니다.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link to="/categories" className="btn-primary">
            시작하기
          </Link>
          <Link to="/about" className="text-sm font-semibold leading-6 text-gray-900">
            사용 방법 보기 <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>

      <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
        <div className="card animate-slide-up">
          <h3 className="text-lg font-semibold mb-2">📚 논문 기반 신뢰성</h3>
          <p className="text-gray-600">
            모든 콘텐츠는 실제 학술 논문을 기반으로 생성되어 과학적 근거가 확실합니다.
          </p>
        </div>
        <div className="card animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <h3 className="text-lg font-semibold mb-2">🎯 실용적 카테고리</h3>
          <p className="text-gray-600">
            즉시 관심을 끌 수 있는 구체적이고 실용적인 10개 카테고리를 제공합니다.
          </p>
        </div>
        <div className="card animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <h3 className="text-lg font-semibold mb-2">📝 다양한 포맷</h3>
          <p className="text-gray-600">
            숏츠 스크립트, 상세 아티클, 종합 리포트 등 다양한 형태로 콘텐츠를 생성합니다.
          </p>
        </div>
      </div>

      <div className="mt-16 bg-primary-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">주요 기능</h2>
        <ul className="space-y-3">
          <li className="flex items-start">
            <span className="text-primary-600 mr-2">✓</span>
            <span>AI 기반 카테고리 자동 생성 (실용성 우선)</span>
          </li>
          <li className="flex items-start">
            <span className="text-primary-600 mr-2">✓</span>
            <span>논문 품질 평가 시스템 (A+ ~ C 등급)</span>
          </li>
          <li className="flex items-start">
            <span className="text-primary-600 mr-2">✓</span>
            <span>Native Thinking Mode를 활용한 심층 분석</span>
          </li>
          <li className="flex items-start">
            <span className="text-primary-600 mr-2">✓</span>
            <span>자동 논문 검증 및 필터링</span>
          </li>
          <li className="flex items-start">
            <span className="text-primary-600 mr-2">✓</span>
            <span>멀티포맷 동시 생성 (45-60초 숏츠, 2000-3000자 아티클)</span>
          </li>
        </ul>
      </div>
    </div>
  )
}