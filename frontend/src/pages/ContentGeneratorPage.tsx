import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import axios from 'axios'
import { RootState, AppDispatch } from '../store'
import { generateContent } from '../store/contentSlice'

interface Paper {
  title: string
  authors: string
  journal: string
  publication_year: number
  doi: string
  impact_factor: number
  citations: number
  paper_type: string
}

interface Subcategory {
  name: string
  description: string
  papers: Paper[]
  expected_effect: string
  quality_score: number
  quality_grade: string
}

export default function ContentGeneratorPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  const { loading, error } = useSelector((state: RootState) => state.content)
  
  const [category] = useState(location.state?.category || null)
  const [topic, setTopic] = useState('')
  const [subcategory, setSubcategory] = useState<Subcategory | null>(null)
  const [discovering, setDiscovering] = useState(false)
  const [selectedFormats, setSelectedFormats] = useState(['shorts', 'article', 'report'])
  const [subcategories, setSubcategories] = useState<any[]>([])
  const [loadingSubcategories, setLoadingSubcategories] = useState(false)
  const [hasGeneratedSubcategories, setHasGeneratedSubcategories] = useState(false)
  const [workflowSummary, setWorkflowSummary] = useState<any>(null)
  const [showWorkflowSummary, setShowWorkflowSummary] = useState(false)

  useEffect(() => {
    if (!category) {
      // 카테고리 없이 접근한 경우 카테고리 페이지로 리다이렉트
      console.log('카테고리가 선택되지 않았습니다. 카테고리 페이지로 이동합니다.')
      navigate('/categories', { replace: true })
    }
  }, [category, navigate])
  
  // 자동 서브카테고리 생성 비활성화 - 사용자가 버튼을 클릭해야만 생성
  // useEffect(() => {
  //   if (category && !hasGeneratedSubcategories && !loadingSubcategories) {
  //     generateSubcategories()
  //   }
  // }, [category, hasGeneratedSubcategories, loadingSubcategories])
  
  const generateSubcategories = async () => {
    if (!category?.name || hasGeneratedSubcategories) return
    
    setLoadingSubcategories(true)
    setHasGeneratedSubcategories(true) // 중복 호출 방지
    
    try {
      const response = await axios.post('/api/v1/categories/generate-subcategories', {
        category_name: category.name
      })
      
      if (response.data?.subcategories) {
        setSubcategories(response.data.subcategories)
      }
    } catch (error) {
      console.error('서브카테고리 생성 실패:', error)
      setHasGeneratedSubcategories(false) // 실패 시 재시도 가능하도록
    } finally {
      setLoadingSubcategories(false)
    }
  }

  const handleDiscoverPapers = async () => {
    if (!topic.trim()) return

    setDiscovering(true)
    try {
      const response = await axios.post('/api/v1/papers/discover', {
        category: category.name,
        topic
      })
      
      if (response.data) {
        setSubcategory(response.data)
      } else {
        alert('해당 주제에 대한 논문을 찾을 수 없습니다. 다른 주제를 시도해보세요.')
      }
    } catch (error) {
      console.error('Error discovering papers:', error)
      alert('논문 검색 중 오류가 발생했습니다.')
    } finally {
      setDiscovering(false)
    }
  }

  // 카테고리가 없으면 아무것도 렌더링하지 않음
  if (!category) {
    return null
  }

  const handleGenerateContent = async () => {
    if (!subcategory) {
      console.error('subcategory가 없습니다')
      return
    }

    console.log('콘텐츠 생성 시작:', { subcategory, selectedFormats })

    try {
      // 생성 성공 개수 추적
      let successCount = 0
      
      // 각 콘텐츠 타입별로 개별 요청 생성
      for (const format of selectedFormats) {
        try {
          // papers가 있는지 확인
          const papers = subcategory.papers || []
          console.log(`${format} 생성 중, papers:`, papers)
          
          const data = {
            topic: subcategory.name,
            category_id: category.id,
            content_type: format,
            paper_ids: papers.length > 0 
              ? papers.map((_, index) => `paper_${index + 1}`)
              : ['paper_1'], // 논문이 없으면 기본값
            thinking_mode: 'enhanced',
            additional_context: JSON.stringify({
              subcategory_description: subcategory.description,
              papers: papers,
              expected_effect: subcategory.expected_effect || '',
              quality_score: subcategory.quality_score || 0,
              quality_grade: subcategory.quality_grade || 'B'
            })
          }

          console.log('생성 요청 데이터:', data)
          
          // unwrap을 사용하여 결과 직접 받기
          const result = await dispatch(generateContent(data)).unwrap()
          console.log('생성 성공:', format, result)
          successCount++
          
        } catch (error: any) {
          console.error(`${format} 생성 실패:`, error)
          alert(`${format} 생성 실패: ${error.message || error || '알 수 없는 오류'}`)
        }
      }
      
      // 하나라도 성공했으면 워크플로우 요약 가져오기
      if (successCount > 0) {
        try {
          const summaryResponse = await axios.get('/api/v1/contents/workflow/summary')
          setWorkflowSummary(summaryResponse.data)
          setShowWorkflowSummary(true)
        } catch (error) {
          console.error('워크플로우 요약 가져오기 실패:', error)
        }
        
        alert(`${successCount}개의 콘텐츠가 성공적으로 생성되었습니다.`)
        // navigate('/library') // 요약을 보여주기 위해 일단 이동하지 않음
      }
    } catch (error) {
      console.error('콘텐츠 생성 중 전체 에러:', error)
      alert('콘텐츠 생성 중 오류가 발생했습니다.')
    }
  }

  const toggleFormat = (format: string) => {
    setSelectedFormats(prev =>
      prev.includes(format)
        ? prev.filter(f => f !== format)
        : [...prev, format]
    )
  }

  if (!category) return null

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">콘텐츠 생성</h1>
        <div className="bg-primary-50 rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-700">
            선택된 카테고리: <span className="font-semibold">{category.emoji} {category.name}</span>
          </p>
          <p className="text-xs text-gray-600 mt-1">{category.description}</p>
        </div>
      </div>

      {/* Step 1: Subcategory Selection */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">1단계: 세부 주제 선택</h2>
        
        {subcategories.length === 0 && !loadingSubcategories ? (
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">
              선택한 카테고리에 대한 논문 기반 서브카테고리를 생성하시겠습니까?
            </p>
            <button
              onClick={generateSubcategories}
              className="btn-primary"
            >
              서브카테고리 생성하기
            </button>
          </div>
        ) : loadingSubcategories ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <p className="mt-2 text-gray-600">논문 기반 서브카테고리 생성 중...</p>
          </div>
        ) : subcategories.length > 0 ? (
          <div className="space-y-3">
            {subcategories.map((sub, index) => (
              <div
                key={index}
                onClick={() => setSubcategory(sub)}
                className={`border rounded-lg p-4 cursor-pointer transition ${
                  subcategory?.name === sub.name
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <h3 className="font-semibold text-lg mb-1">{sub.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{sub.description}</p>
                <div className="flex items-center space-x-4 text-xs">
                  <span className="bg-white px-2 py-1 rounded">
                    논문 {sub.papers_count}개
                  </span>
                  <span className="bg-white px-2 py-1 rounded">
                    품질 {sub.quality_grade}
                  </span>
                  <span className="text-gray-500">{sub.topic}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-gray-600">서브카테고리를 불러오는 중 오류가 발생했습니다.</p>
            <div>
              <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-2">
                직접 주제 입력
              </label>
              <input
                type="text"
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="input"
                placeholder="예: 7분 운동법, 아침 운동 효과, 근력 운동 세트수"
              />
            </div>
            <button
              onClick={handleDiscoverPapers}
              disabled={discovering || !topic.trim()}
              className="btn-primary"
            >
              {discovering ? '논문 검색 중...' : '논문 검색하기'}
            </button>
          </div>
        )}
      </div>

      {/* Step 2: Paper Results */}
      {subcategory && subcategory.papers && (
        <div className="bg-white rounded-lg shadow p-6 mb-6 animate-slide-up">
          <h2 className="text-xl font-semibold mb-4">2단계: 논문 검색 결과</h2>
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-lg mb-2">{subcategory.name}</h3>
            <p className="text-gray-600 text-sm mb-3">{subcategory.description}</p>
            <div className="flex items-center space-x-4 text-sm">
              <span className="bg-white px-3 py-1 rounded-full">
                품질 등급: <span className="font-semibold text-primary-600">{subcategory.quality_grade}</span>
              </span>
              <span className="bg-white px-3 py-1 rounded-full">
                품질 점수: <span className="font-semibold">{subcategory.quality_score}/100</span>
              </span>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-medium text-gray-700">근거 논문 ({subcategory.papers.length}개)</h4>
            {subcategory.papers.map((paper, index) => (
              <div key={index} className="border-l-4 border-primary-200 pl-4 py-2">
                <p className="font-medium text-sm">{paper.title}</p>
                <p className="text-xs text-gray-600 mt-1">
                  {paper.authors} • {paper.journal} ({paper.publication_year})
                </p>
                <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                  <span>IF: {paper.impact_factor}</span>
                  <span>인용: {paper.citations}회</span>
                  <span>{paper.paper_type}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-900 mb-1">기대 효과</h4>
            <p className="text-sm text-green-800">{subcategory.expected_effect}</p>
          </div>
        </div>
      )}

      {/* Step 3: Content Format Selection */}
      {subcategory && (
        <div className="bg-white rounded-lg shadow p-6 mb-6 animate-slide-up">
          <h2 className="text-xl font-semibold mb-4">3단계: 콘텐츠 형식 선택</h2>
          <div className="space-y-3">
            {[
              { id: 'shorts', name: '숏츠 스크립트', desc: '45-60초 분량의 짧은 영상 대본' },
              { id: 'article', name: '상세 아티클', desc: '2000-3000자 분량의 블로그 글' },
              { id: 'report', name: '종합 리포트', desc: '전문적인 분석 보고서' }
            ].map(format => (
              <label key={format.id} className="flex items-start p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={selectedFormats.includes(format.id)}
                  onChange={() => toggleFormat(format.id)}
                  className="mt-1 mr-3"
                />
                <div>
                  <p className="font-medium">{format.name}</p>
                  <p className="text-sm text-gray-600">{format.desc}</p>
                </div>
              </label>
            ))}
          </div>

          <button
            onClick={handleGenerateContent}
            disabled={loading || selectedFormats.length === 0}
            className="btn-primary mt-6 w-full"
          >
            {loading ? '콘텐츠 생성 중...' : `선택한 ${selectedFormats.length}개 형식으로 콘텐츠 생성`}
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      {/* Workflow Summary Modal */}
      {showWorkflowSummary && workflowSummary && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              📊 워크플로우 완료 - 토큰 사용량 및 비용 요약
            </h2>
            
            <div className="space-y-4">
              {/* Total Summary */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">전체 요약</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">총 작업 수:</span>
                    <span className="ml-2 font-medium">{workflowSummary.total_operations}개</span>
                  </div>
                  <div>
                    <span className="text-gray-600">총 토큰:</span>
                    <span className="ml-2 font-medium">{workflowSummary.total_tokens.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">입력 토큰:</span>
                    <span className="ml-2 font-medium">{workflowSummary.prompt_tokens.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">출력 토큰:</span>
                    <span className="ml-2 font-medium">{workflowSummary.response_tokens.toLocaleString()}</span>
                  </div>
                </div>
              </div>
              
              {/* Cost */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2">예상 비용</h3>
                <div className="text-2xl font-bold text-green-600">
                  ${workflowSummary.estimated_cost_usd.toFixed(4)} USD
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  ≈ ₩{workflowSummary.estimated_cost_krw.toFixed(2)} KRW
                </div>
              </div>
              
              {/* Operations Breakdown */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">작업별 세부 내역</h3>
                <div className="space-y-2 text-sm">
                  {Object.entries(workflowSummary.operations_breakdown).map(([op, stats]: [string, any]) => (
                    <div key={op} className="flex justify-between items-center py-1 border-b border-gray-200">
                      <span className="text-gray-700">{op}</span>
                      <div className="text-right">
                        <span className="text-gray-600">{stats.count}회</span>
                        <span className="ml-3 font-medium">{stats.total_tokens.toLocaleString()} 토큰</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Session Duration */}
              <div className="text-sm text-gray-600">
                작업 소요 시간: {workflowSummary.session_duration}
              </div>
            </div>
            
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => {
                  setShowWorkflowSummary(false)
                  navigate('/library')
                }}
                className="btn-primary"
              >
                라이브러리로 이동
              </button>
              <button
                onClick={() => setShowWorkflowSummary(false)}
                className="btn-secondary"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}