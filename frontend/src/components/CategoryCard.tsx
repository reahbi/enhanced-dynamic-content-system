interface CategoryCardProps {
  category: {
    id: string
    name: string
    description: string
    emoji: string
    practicality_score: number
    interest_score: number
    content_count?: number
  }
  onSelect: (category: any) => void
  onDelete?: (categoryId: string) => void
}

export default function CategoryCard({ category, onSelect, onDelete }: CategoryCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow relative">
      {onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete(category.id)
          }}
          className="absolute top-2 right-2 text-gray-400 hover:text-red-500 transition-colors"
          title="카테고리 삭제"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
      <div className="flex items-center mb-4">
        <span className="text-3xl mr-3">{category.emoji}</span>
        <h3 className="text-lg font-semibold text-gray-800">{category.name}</h3>
      </div>
      <p className="text-gray-600 text-sm mb-4">{category.description}</p>
      {category.content_count !== undefined && category.content_count > 0 && (
        <div className="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded inline-block mb-3">
          📄 콘텐츠 {category.content_count}개 연결됨
        </div>
      )}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">실용성</span>
          <div className="flex items-center">
            <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
              <div
                className="bg-primary-500 h-2 rounded-full"
                style={{ width: `${(category.practicality_score / 10) * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium">{category.practicality_score}/10</span>
          </div>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">관심도</span>
          <div className="flex items-center">
            <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
              <div
                className="bg-green-500 h-2 rounded-full"
                style={{ width: `${(category.interest_score / 10) * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium">{category.interest_score}/10</span>
          </div>
        </div>
      </div>
      <button
        onClick={() => onSelect(category)}
        className="w-full bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
      >
        선택하기
      </button>
    </div>
  )
}