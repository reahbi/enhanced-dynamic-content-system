import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { RootState, AppDispatch } from '../store'
import { generateCategories, fetchCategories, resetGenerateState, deleteCategoryAsync } from '../store/categoriesSlice'
import CategoryCard from '../components/CategoryCard'

export default function CategoriesPage() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { categories, generateLoading, error } = useSelector((state: RootState) => state.categories)
  const [keyword, setKeyword] = useState('운동')
  const [count, setCount] = useState(5)

  useEffect(() => {
    // 페이지 로드 시 생성 상태 초기화
    dispatch(resetGenerateState())
    // fetchCategories() 제거 - 새로 생성한 카테고리만 보여줌
  }, [dispatch])

  const handleGenerate = async () => {
    try {
      const result = await dispatch(generateCategories({ keyword, count }))
      console.log('Generate result:', result)
    } catch (error) {
      console.error('Generate error:', error)
    }
  }

  const handleSelectCategory = (category: any) => {
    navigate('/generate', { state: { category } })
  }

  const handleDeleteCategory = async (categoryId: string) => {
    if (window.confirm('이 카테고리를 삭제하시겠습니까?')) {
      try {
        await dispatch(deleteCategoryAsync(categoryId)).unwrap()
      } catch (error: any) {
        console.error('카테고리 삭제 실패:', error)
        // 에러 메시지 추출
        const errorMessage = error?.response?.data?.detail || error?.message || '카테고리 삭제에 실패했습니다.'
        alert(errorMessage)
      }
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">카테고리 생성</h1>
        <p className="text-gray-600">
          관심 키워드를 입력하면 AI가 실용적이고 매력적인 카테고리를 자동으로 생성합니다.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-2">
              키워드
            </label>
            <input
              type="text"
              id="keyword"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="input"
              placeholder="예: 운동, 다이어트, 건강"
            />
          </div>
          <div>
            <label htmlFor="count" className="block text-sm font-medium text-gray-700 mb-2">
              생성 개수
            </label>
            <select
              id="count"
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="input"
            >
              {[3, 5, 7, 10].map((n) => (
                <option key={n} value={n}>
                  {n}개
                </option>
              ))}
            </select>
          </div>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generateLoading || !keyword.trim()}
          className="btn-primary mt-4"
        >
          {generateLoading ? '생성 중...' : '카테고리 생성'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {categories.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">생성된 카테고리</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((category) => (
              <CategoryCard
                key={category.id}
                category={category}
                onSelect={handleSelectCategory}
                onDelete={handleDeleteCategory}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}