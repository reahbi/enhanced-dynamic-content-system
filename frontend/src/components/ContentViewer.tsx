import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

interface ContentViewerProps {
  content: {
    id: string
    topic: string
    category_id: string
    content_type: string
    content: string
    metadata: {
      [key: string]: any
    }
    quality_score: number
    thinking_process: string | null
    created_at: string
  }
  onDelete?: (contentId: string) => void
}

type CopyType = 'text' | 'html' | 'naver'

export default function ContentViewer({ content, onDelete }: ContentViewerProps) {
  const [showThinking, setShowThinking] = useState(false)
  const [copied, setCopied] = useState(false)
  const [showCopyMenu, setShowCopyMenu] = useState(false)
  const [showDownloadMenu, setShowDownloadMenu] = useState(false)
  const [previewMode, setPreviewMode] = useState(false)
  const [htmlPreviewMode, setHtmlPreviewMode] = useState(false)
  const [transforming, setTransforming] = useState(false)
  const [transformedContent, setTransformedContent] = useState<any>(null)
  const [showTransformMenu, setShowTransformMenu] = useState(false)
  const copyMenuRef = useRef<HTMLDivElement>(null)
  const downloadMenuRef = useRef<HTMLDivElement>(null)
  const transformMenuRef = useRef<HTMLDivElement>(null)

  // Click outside handler
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (copyMenuRef.current && !copyMenuRef.current.contains(event.target as Node)) {
        setShowCopyMenu(false)
      }
      if (downloadMenuRef.current && !downloadMenuRef.current.contains(event.target as Node)) {
        setShowDownloadMenu(false)
      }
      if (transformMenuRef.current && !transformMenuRef.current.contains(event.target as Node)) {
        setShowTransformMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const getContentTypeLabel = (type: string) => {
    switch (type) {
      case 'shorts':
        return '🎬 숏츠 스크립트'
      case 'article':
        return '📄 상세 아티클'
      case 'report':
        return '📊 종합 리포트'
      default:
        return '📝 콘텐츠'
    }
  }

  const isHtmlContent = (text: string) => {
    // Check if content contains HTML tags
    return /<[^>]+>/.test(text)
  }

  const formatContent = (text: string) => {
    // 빈 줄로 단락 구분
    const paragraphs = text.split('\n\n')
    
    return paragraphs.map((paragraph, index) => {
      // 제목 처리 (### 형식)
      if (paragraph.match(/^#{1,6}\s/)) {
        const level = paragraph.match(/^#+/)?.[0].length || 1
        const cleanText = paragraph.replace(/^#+\s/, '')
        const className = level === 1 ? 'text-2xl font-bold mt-6 mb-3' : 
                         level === 2 ? 'text-xl font-bold mt-4 mb-2' : 
                         'text-lg font-semibold mt-3 mb-2'
        return <h3 key={index} className={className}>{cleanText}</h3>
      }
      
      // 번호 목록 처리
      if (paragraph.match(/^\d+\.\s/)) {
        const items = paragraph.split('\n').filter(line => line.trim())
        return (
          <ol key={index} className="list-decimal list-inside space-y-2 mb-4 ml-4">
            {items.map((item, i) => {
              const cleanItem = item.replace(/^\d+\.\s*/, '')
              return <li key={i} className="text-gray-700 leading-relaxed">{cleanItem}</li>
            })}
          </ol>
        )
      }
      
      // 불릿 목록 처리
      if (paragraph.match(/^[-*•]\s/)) {
        const items = paragraph.split('\n').filter(line => line.trim())
        return (
          <ul key={index} className="list-disc list-inside space-y-2 mb-4 ml-4">
            {items.map((item, i) => {
              const cleanItem = item.replace(/^[-*•]\s*/, '')
              return <li key={i} className="text-gray-700 leading-relaxed">{cleanItem}</li>
            })}
          </ul>
        )
      }
      
      // 타임스탬프가 있는 경우 (숏츠 스크립트)
      if (paragraph.match(/\[\d+:\d+-\d+:\d+\]/)) {
        const [timestamp, ...textParts] = paragraph.split(']')
        const cleanTimestamp = timestamp + ']'
        const text = textParts.join(']')
        return (
          <div key={index} className="mb-3">
            <span className="text-sm font-mono text-primary-600">{cleanTimestamp}</span>
            <p className="text-gray-700 leading-relaxed ml-4">{text.trim()}</p>
          </div>
        )
      }
      
      // 섹션 구분선
      if (paragraph.match(/^[-=]{3,}$/)) {
        return <hr key={index} className="my-6 border-gray-200" />
      }
      
      // 일반 단락
      if (paragraph.trim()) {
        return <p key={index} className="text-gray-700 mb-4 leading-relaxed">{paragraph}</p>
      }
      
      return null
    }).filter(Boolean)
  }

  // 네이버 블로그 호환 HTML 생성
  const generateNaverHTML = (text: string) => {
    const paragraphs = text.split('\n\n')
    let html = ''
    
    paragraphs.forEach((paragraph, index) => {
      // 제목 처리
      if (paragraph.match(/^#{1,6}\s/)) {
        const level = paragraph.match(/^#+/)?.[0].length || 1
        const cleanText = paragraph.replace(/^#+\s/, '')
        
        // 네이버 스타일 제목
        if (level === 1) {
          html += `<h2 style="font-size: 28px; color: #333; margin: 30px 0 20px 0; font-weight: bold;">${cleanText}</h2>\n`
        } else if (level === 2) {
          html += `<h3 style="font-size: 22px; color: #555; margin: 25px 0 15px 0; font-weight: bold;">${cleanText}</h3>\n`
        } else {
          html += `<h4 style="font-size: 18px; color: #666; margin: 20px 0 10px 0; font-weight: bold;">${cleanText}</h4>\n`
        }
      }
      // 번호 목록
      else if (paragraph.match(/^\d+\.\s/)) {
        const items = paragraph.split('\n').filter(line => line.trim())
        html += '<ol style="margin: 15px 0; padding-left: 30px;">\n'
        items.forEach(item => {
          const cleanItem = item.replace(/^\d+\.\s*/, '')
          html += `  <li style="margin-bottom: 10px; line-height: 1.8;">${cleanItem}</li>\n`
        })
        html += '</ol>\n'
      }
      // 불릿 목록
      else if (paragraph.match(/^[-*•]\s/)) {
        const items = paragraph.split('\n').filter(line => line.trim())
        html += '<ul style="margin: 15px 0; padding-left: 30px;">\n'
        items.forEach(item => {
          const cleanItem = item.replace(/^[-*•]\s*/, '')
          html += `  <li style="margin-bottom: 10px; line-height: 1.8;">${cleanItem}</li>\n`
        })
        html += '</ul>\n'
      }
      // 타임스탬프
      else if (paragraph.match(/\[\d+:\d+-\d+:\d+\]/)) {
        const [timestamp, ...textParts] = paragraph.split(']')
        const cleanTimestamp = timestamp + ']'
        const text = textParts.join(']').trim()
        html += `<p style="margin: 15px 0; line-height: 1.8;"><strong style="color: #e74c3c;">${cleanTimestamp}</strong> ${text}</p>\n`
      }
      // 구분선
      else if (paragraph.match(/^[-=]{3,}$/)) {
        html += '<hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">\n'
      }
      // 💡 팁 박스
      else if (paragraph.startsWith('💡')) {
        html += `<div style="background-color: #fff5b4; padding: 15px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #f1c40f;">
          <p style="margin: 0; line-height: 1.8; font-size: 16px;">${paragraph}</p>
        </div>\n`
      }
      // ⚠️ 주의사항 박스
      else if (paragraph.startsWith('⚠️')) {
        html += `<div style="background-color: #fee; padding: 15px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #e74c3c;">
          <p style="margin: 0; line-height: 1.8; font-size: 16px;">${paragraph}</p>
        </div>\n`
      }
      // ✅ 체크 박스
      else if (paragraph.startsWith('✅')) {
        html += `<div style="background-color: #e8f8f5; padding: 15px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #27ae60;">
          <p style="margin: 0; line-height: 1.8; font-size: 16px;">${paragraph}</p>
        </div>\n`
      }
      // 일반 단락
      else if (paragraph.trim()) {
        // 굵은 글씨 처리
        let processedText = paragraph.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #333; font-weight: bold;">$1</strong>')
        // 이탤릭 처리
        processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>')
        // 형광펜 효과 (~~텍스트~~)
        processedText = processedText.replace(/~~(.*?)~~/g, '<span style="background-color: #fff5b4; padding: 2px 4px;">$1</span>')
        
        html += `<p style="margin: 15px 0; line-height: 1.8; font-size: 16px; color: #333;">${processedText}</p>\n`
      }
      
      // 첫 문단 후 여백 추가
      if (index === 0 && !paragraph.match(/^#{1,6}\s/)) {
        html += '<br>\n'
      }
    })
    
    return html
  }

  const transformContent = async (transformationType: 'humanize' | 'simplify' | 'practical') => {
    setTransforming(true)
    try {
      const response = await axios.post('/api/v1/contents/transform', {
        content_id: content.id,
        transformation_type: transformationType
      })
      
      // 변환된 콘텐츠를 새로운 콘텐츠로 표시
      setTransformedContent(response.data.content)
      
      // 성공 메시지
      const messages = {
        humanize: '사람이 쓴 것처럼 자연스럽게 변환되었습니다',
        simplify: '쉽고 이해하기 쉽게 변환되었습니다',
        practical: '실용적이고 행동 중심으로 변환되었습니다'
      }
      alert(messages[transformationType])
      
    } catch (error) {
      console.error('콘텐츠 변환 실패:', error)
      alert('콘텐츠 변환에 실패했습니다.')
    } finally {
      setTransforming(false)
    }
  }

  const copyToClipboard = async (type: CopyType = 'text') => {
    try {
      if (type === 'text') {
        await navigator.clipboard.writeText(displayContent.content)
      } else if (type === 'html') {
        const html = generateNaverHTML(displayContent.content)
        await navigator.clipboard.writeText(html)
      } else if (type === 'naver') {
        const html = generateNaverHTML(displayContent.content)
        const blob = new Blob([html], { type: 'text/html' })
        const data = [new ClipboardItem({ 'text/html': blob, 'text/plain': new Blob([content.content], { type: 'text/plain' }) })]
        await navigator.clipboard.write(data)
      }
      setCopied(true)
      setShowCopyMenu(false)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      // 폴백: HTML 복사가 실패하면 텍스트로 복사
      if (type !== 'text') {
        try {
          const html = generateNaverHTML(displayContent.content)
          await navigator.clipboard.writeText(html)
          setCopied(true)
          setShowCopyMenu(false)
          setTimeout(() => setCopied(false), 2000)
        } catch {
          alert('복사에 실패했습니다.')
        }
      } else {
        alert('복사에 실패했습니다.')
      }
    }
  }

  const downloadContent = (format: 'txt' | 'html' = 'txt') => {
    const date = new Date().toISOString().split('T')[0]
    let filename: string
    let blob: Blob
    
    if (format === 'html') {
      filename = `${content.topic}_${content.content_type}_${date}.html`
      const html = `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${content.topic}</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; line-height: 1.8; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { margin-top: 1.5em; margin-bottom: 0.5em; }
        p { margin-bottom: 1em; }
        ul, ol { margin-bottom: 1em; }
        li { margin-bottom: 0.5em; }
        hr { margin: 2em 0; border: none; border-top: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>${content.topic}</h1>
    <p><small>${getContentTypeLabel(content.content_type)} | 품질: ${Math.round(content.quality_score)}점 | ${new Date(content.created_at).toLocaleString('ko-KR')}</small></p>
    <hr>
    ${generateNaverHTML(content.content)}
</body>
</html>`
      blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    } else {
      filename = `${content.topic}_${content.content_type}_${date}.txt`
      blob = new Blob([content.content], { type: 'text/plain;charset=utf-8' })
    }
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename.replace(/[^a-zA-Z0-9가-힣_-]/g, '_')
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // 표시할 콘텐츠 결정 (변환된 콘텐츠가 있으면 그것을, 없으면 원본을)
  const displayContent = transformedContent || content
  
  return (
    <div className="max-h-[80vh] overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b p-6 z-10">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {displayContent.topic}
              {transformedContent && (
                <span className="ml-2 text-sm text-purple-600 bg-purple-100 px-2 py-1 rounded">
                  ✨ AI 변환됨
                </span>
              )}
            </h2>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span className="font-medium">{getContentTypeLabel(displayContent.content_type)}</span>
              <span>품질: {Math.round(displayContent.quality_score)}점</span>
              {content.metadata?.papers_used && (
                <span>논문 {content.metadata.papers_used}개 참조</span>
              )}
              <span>{new Date(content.created_at).toLocaleString('ko-KR')}</span>
            </div>
          </div>
          
          <div className="flex gap-2">
            <div className="relative" ref={copyMenuRef}>
              <button
                onClick={() => setShowCopyMenu(!showCopyMenu)}
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                title="복사 옵션"
              >
                {copied ? '✓ 복사됨!' : '📋 복사'}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {showCopyMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-20">
                  <button
                    onClick={() => copyToClipboard('text')}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    📄 일반 텍스트 복사
                  </button>
                  <button
                    onClick={() => copyToClipboard('naver')}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🎨 서식 포함 복사 (네이버)
                  </button>
                  <button
                    onClick={() => copyToClipboard('html')}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🔧 HTML 소스 복사
                  </button>
                </div>
              )}
            </div>
            
            <div className="relative" ref={downloadMenuRef}>
              <button
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors"
                title="다운로드 옵션"
              >
                💾 다운로드
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {showDownloadMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-20">
                  <button
                    onClick={() => {
                      downloadContent('txt')
                      setShowDownloadMenu(false)
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    📄 텍스트 파일 (.txt)
                  </button>
                  <button
                    onClick={() => {
                      downloadContent('html')
                      setShowDownloadMenu(false)
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🌐 HTML 파일 (.html)
                  </button>
                </div>
              )}
            </div>
            
            <div className="relative" ref={transformMenuRef}>
              <button
                onClick={() => setShowTransformMenu(!showTransformMenu)}
                disabled={transforming}
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-purple-600 bg-white border border-purple-300 rounded-md hover:bg-purple-50 transition-colors disabled:opacity-50"
                title="AI 변환 옵션"
              >
                {transforming ? '변환 중...' : '✨ AI 변환'}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {showTransformMenu && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200 z-20">
                  <button
                    onClick={() => {
                      transformContent('humanize')
                      setShowTransformMenu(false)
                    }}
                    disabled={transforming}
                    className="block w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 border-b border-gray-100"
                  >
                    <div className="font-medium">🤗 사람처럼 변환</div>
                    <div className="text-xs text-gray-500 mt-1">AI 느낌을 없애고 자연스럽게</div>
                  </button>
                  <button
                    onClick={() => {
                      transformContent('simplify')
                      setShowTransformMenu(false)
                    }}
                    disabled={transforming}
                    className="block w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 border-b border-gray-100"
                  >
                    <div className="font-medium">📚 쉽게 설명</div>
                    <div className="text-xs text-gray-500 mt-1">전문 용어를 쉬운 말로 풀어서</div>
                  </button>
                  <button
                    onClick={() => {
                      transformContent('practical')
                      setShowTransformMenu(false)
                    }}
                    disabled={transforming}
                    className="block w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <div className="font-medium">💪 실용적으로</div>
                    <div className="text-xs text-gray-500 mt-1">이론보다 실천 방법 중심으로</div>
                  </button>
                </div>
              )}
            </div>
            
            {onDelete && (
              <button
                onClick={() => {
                  if (window.confirm('이 콘텐츠를 삭제하시겠습니까?')) {
                    onDelete(content.id)
                  }
                }}
                className="px-3 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-md hover:bg-red-50 transition-colors"
                title="콘텐츠 삭제"
              >
                🗑️ 삭제
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Reset to Original if Transformed */}
          {transformedContent && (
            <button
              onClick={() => setTransformedContent(null)}
              className="flex items-center gap-2 text-sm text-purple-600 hover:text-purple-700 transition-colors font-medium"
            >
              ↩️ 원본으로 돌아가기
            </button>
          )}
          
          {/* Preview Mode Toggle */}
          <button
            onClick={() => setPreviewMode(!previewMode)}
            className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 transition-colors"
          >
            {previewMode ? '📝 원본 보기' : '👁️ 네이버 미리보기'}
          </button>
          
          {/* HTML Copy Mode Toggle */}
          <button
            onClick={() => setHtmlPreviewMode(!htmlPreviewMode)}
            className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 transition-colors"
          >
            {htmlPreviewMode ? '📝 일반 보기' : '📋 HTML 복사 모드'}
          </button>
          
          {/* Thinking Process Toggle */}
          {content.thinking_process && (
            <button
              onClick={() => setShowThinking(!showThinking)}
              className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 transition-colors"
            >
              {showThinking ? '▲' : '▼'} AI 사고 과정 {showThinking ? '숨기기' : '보기'}
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Thinking Process */}
        {showThinking && content.thinking_process && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">🤔 AI 사고 과정</h3>
            <div className="text-sm text-blue-800 whitespace-pre-wrap">{content.thinking_process}</div>
          </div>
        )}

        {/* Main Content */}
        <div className="prose prose-lg max-w-none">
          {content.content_type === 'shorts' && !previewMode && (
            <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                💡 이 스크립트는 45-60초 분량의 YouTube Shorts용으로 작성되었습니다.
              </p>
            </div>
          )}
          
          {htmlPreviewMode ? (
            <div className="bg-gray-50 border border-gray-300 rounded-lg p-6">
              <div className="text-sm text-gray-600 mb-4 text-center">
                📋 아래 내용을 전체 선택(Ctrl+A) → 복사(Ctrl+C) → 네이버 블로그에 붙여넣기 해주세요
              </div>
              <div 
                className="bg-white p-8 border border-gray-200 rounded shadow-sm" 
                style={{
                  fontFamily: '"Malgun Gothic", "맑은 고딕", sans-serif',
                  lineHeight: '1.8',
                  color: '#333',
                  userSelect: 'text',
                  cursor: 'text'
                }}
                dangerouslySetInnerHTML={{ __html: isHtmlContent(displayContent.content) ? displayContent.content : generateNaverHTML(displayContent.content) }}
              />
            </div>
          ) : previewMode ? (
            <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
              <div className="text-sm text-gray-500 mb-4 text-center">
                ⬇️ 네이버 블로그 미리보기 ⬇️
              </div>
              <div 
                className="naver-preview" 
                dangerouslySetInnerHTML={{ __html: generateNaverHTML(displayContent.content) }}
                style={{
                  fontFamily: '"Malgun Gothic", "맑은 고딕", sans-serif',
                  lineHeight: '1.8',
                  color: '#333'
                }}
              />
            </div>
          ) : (
            formatContent(displayContent.content)
          )}
        </div>

        {/* Papers Reference */}
        {content.metadata?.papers && content.metadata.papers.length > 0 && (
          <div className="mt-8 pt-6 border-t">
            <h3 className="font-semibold text-gray-700 mb-3">📚 참조 논문</h3>
            <div className="space-y-4">
              {content.metadata.papers.map((paper: any, index: number) => (
                <div key={paper.id || index} className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">{paper.title}</h4>
                  {paper.authors && (
                    <p className="text-sm text-gray-600 mb-1">저자: {paper.authors}</p>
                  )}
                  {paper.journal && (
                    <p className="text-sm text-gray-600 mb-1">저널: {paper.journal}</p>
                  )}
                  {paper.abstract && (
                    <p className="text-sm text-gray-700 mt-2 line-clamp-3">{paper.abstract}</p>
                  )}
                  {paper.key_findings && paper.key_findings.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm font-medium text-gray-700">주요 발견:</p>
                      <ul className="list-disc list-inside text-sm text-gray-600 mt-1">
                        {paper.key_findings.map((finding: string, idx: number) => (
                          <li key={idx}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {paper.doi && (
                    <p className="text-xs text-gray-500 mt-2">DOI: {paper.doi}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        {content.metadata && Object.keys(content.metadata).length > 0 && (
          <div className="mt-8 pt-6 border-t">
            <h3 className="font-semibold text-gray-700 mb-3">📋 추가 정보</h3>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              {Object.entries(content.metadata).map(([key, value]) => {
                if (key === 'generation_time' || key === 'papers_used' || key === 'papers' || typeof value === 'object') return null
                return (
                  <div key={key}>
                    <dt className="font-medium text-gray-600">{key}:</dt>
                    <dd className="text-gray-900">{String(value)}</dd>
                  </div>
                )
              })}
            </dl>
          </div>
        )}
      </div>
    </div>
  )
}