import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState, AppDispatch } from '../store'
import { fetchContents, setCurrentContent, deleteContentAsync } from '../store/contentSlice'
import ContentViewer from '../components/ContentViewer'
import { Dialog } from '@headlessui/react'

export default function LibraryPage() {
  const dispatch = useDispatch<AppDispatch>()
  const { contents, loading, currentContent } = useSelector((state: RootState) => state.content)
  const [filter, setFilter] = useState<string>('')
  const [isViewerOpen, setIsViewerOpen] = useState(false)

  useEffect(() => {
    dispatch(fetchContents())
      .unwrap()
      .then((data) => {
        console.log('Fetched contents:', data)
      })
      .catch((error) => {
        console.error('Error fetching contents:', error)
      })
  }, [dispatch])

  const handleViewContent = (content: any) => {
    dispatch(setCurrentContent(content))
    setIsViewerOpen(true)
  }

  const handleDeleteContent = async (contentId: string) => {
    try {
      await dispatch(deleteContentAsync(contentId)).unwrap()
      setIsViewerOpen(false)
      // 리스트 새로고침
      dispatch(fetchContents())
    } catch (error) {
      console.error('콘텐츠 삭제 실패:', error)
      alert('콘텐츠 삭제에 실패했습니다.')
    }
  }

  const filteredContents = contents.filter(
    content => !filter || content.content_type === filter
  )

  const getContentTypeLabel = (type: string) => {
    switch (type) {
      case 'shorts':
        return '숏츠 스크립트'
      case 'article':
        return '아티클'
      case 'report':
        return '리포트'
      default:
        return type
    }
  }

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case 'shorts':
        return '🎬'
      case 'article':
        return '📄'
      case 'report':
        return '📊'
      default:
        return '📝'
    }
  }
  
  // HTML 태그 제거 함수
  const stripHtmlTags = (html: string) => {
    // HTML 태그 제거
    let text = html.replace(/<[^>]*>/g, '')
    // HTML 엔티티 디코드
    text = text.replace(/&nbsp;/g, ' ')
    text = text.replace(/&lt;/g, '<')
    text = text.replace(/&gt;/g, '>')
    text = text.replace(/&amp;/g, '&')
    text = text.replace(/&quot;/g, '"')
    text = text.replace(/&#39;/g, "'")
    // 연속된 공백 제거
    text = text.replace(/\s+/g, ' ')
    return text.trim()
  }
  
  // HTML 콘텐츠 검사
  const isHtmlContent = (text: string) => {
    return /<[^>]+>/.test(text)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">콘텐츠 라이브러리</h1>
        <p className="text-gray-600">생성된 모든 콘텐츠를 확인하고 관리할 수 있습니다.</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">필터:</span>
          <button
            onClick={() => setFilter('')}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              filter === ''
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            전체 ({contents.length})
          </button>
          {['shorts', 'article', 'report'].map(type => {
            const count = contents.filter(c => c.content_type === type).length
            return (
              <button
                key={type}
                onClick={() => setFilter(type)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  filter === type
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {getContentTypeLabel(type)} ({count})
              </button>
            )
          })}
        </div>
      </div>

      {/* Content Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-gray-600">콘텐츠 로딩 중...</p>
        </div>
      ) : filteredContents.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">아직 생성된 콘텐츠가 없습니다.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredContents.map(content => (
            <div key={content.id} className="card hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">{getContentTypeIcon(content.content_type)}</span>
                <span className="text-xs text-gray-500">
                  {new Date(content.created_at).toLocaleDateString('ko-KR')}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                {content.topic}
              </h3>
              <div className="text-sm text-gray-600 mb-2 line-clamp-3">
                {/* 콘텐츠 내용 미리보기 - HTML 및 포맷 제거하고 텍스트만 추출 */}
                {(() => {
                  let text = content.content
                  // HTML 콘텐츠인 경우 태그 제거
                  if (isHtmlContent(text)) {
                    text = stripHtmlTags(text)
                  }
                  // 마크다운 포맷 제거
                  text = text
                    .replace(/^#{1,6}\s/gm, '') // 제목 마크다운 제거
                    .replace(/\*\*(.*?)\*\*/g, '$1') // 굵은 글씨 제거
                    .replace(/\*(.*?)\*/g, '$1') // 이탤릭 제거
                    .replace(/\[\d+:\d+-\d+:\d+\]/g, '') // 타임스탬프 제거
                    .replace(/^[-*•]\s/gm, '') // 불릿 포인트 제거
                    .replace(/^\d+\.\s/gm, '') // 번호 목록 제거
                    .replace(/\n\n+/g, ' ') // 줄바꿈을 공백으로
                    .replace(/^[-=]{3,}$/gm, '') // 구분선 제거
                    .trim()
                  return text.substring(0, 150) + '...'
                })()}
              </div>
              {content.metadata?.papers && content.metadata.papers.length > 0 && (
                <div className="text-xs text-gray-500 mb-2">
                  📚 논문 {content.metadata.papers.length}개 참조
                </div>
              )}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  <span>품질: {Math.round(content.quality_score)}/100</span>
                  {content.metadata?.generation_time && (
                    <>
                      <span>•</span>
                      <span>생성 시간: {typeof content.metadata.generation_time === 'number' ? content.metadata.generation_time.toFixed(1) : content.metadata.generation_time}초</span>
                    </>
                  )}
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => handleViewContent(content)}
                  className="flex-1 text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  전체 보기 →
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    if (window.confirm('이 콘텐츠를 삭제하시겠습니까?')) {
                      handleDeleteContent(content.id)
                    }
                  }}
                  className="px-3 py-1 text-red-600 hover:text-red-700 text-sm font-medium border border-red-200 rounded hover:bg-red-50 transition-colors"
                  title="콘텐츠 삭제"
                >
                  삭제
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Content Viewer Dialog */}
      <Dialog
        open={isViewerOpen}
        onClose={() => setIsViewerOpen(false)}
        className="relative z-50"
      >
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="mx-auto max-w-4xl w-full max-h-[90vh] overflow-y-auto bg-white rounded-lg shadow-xl">
            {currentContent && <ContentViewer content={currentContent} onDelete={handleDeleteContent} />}
            <div className="sticky bottom-0 bg-white border-t p-4">
              <button
                onClick={() => setIsViewerOpen(false)}
                className="btn-secondary w-full"
              >
                닫기
              </button>
            </div>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  )
}