import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import axios from 'axios'

interface Category {
  id: string
  name: string
  description: string
  emoji: string
  practicality_score: number
  interest_score: number
  seed_keyword: string
  created_at: string
  content_count?: number
}

interface CategoriesState {
  categories: Category[]
  loading: boolean
  generateLoading: boolean
  error: string | null
}

const initialState: CategoriesState = {
  categories: [],
  loading: false,
  generateLoading: false,
  error: null,
}

export const fetchCategories = createAsyncThunk(
  'categories/fetch',
  async () => {
    const response = await axios.get('/api/v1/categories')
    return response.data
  }
)

export const generateCategories = createAsyncThunk(
  'categories/generate',
  async ({ keyword, count }: { keyword: string; count: number }) => {
    const response = await axios.post('/api/v1/categories/generate', {
      keyword: keyword,
      count: count
    }, {
      timeout: 60000  // 60초 타임아웃 설정
    })
    return response.data
  }
)

export const deleteCategoryAsync = createAsyncThunk(
  'categories/delete',
  async (categoryId: string) => {
    await axios.delete(`/api/v1/categories/${categoryId}`)
    return categoryId
  }
)

const categoriesSlice = createSlice({
  name: 'categories',
  initialState,
  reducers: {
    resetGenerateState: (state) => {
      state.generateLoading = false
      state.error = null
    },
    clearCategories: (state) => {
      state.categories = []
    },
    deleteCategory: (state, action) => {
      state.categories = state.categories.filter(cat => cat.id !== action.payload)
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch categories
      .addCase(fetchCategories.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.loading = false
        console.log('Fetch categories response:', action.payload)
        // API 응답이 { categories: [...] } 형식일 수도 있음
        state.categories = action.payload.categories || action.payload || []
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch categories'
      })
      // Generate categories
      .addCase(generateCategories.pending, (state) => {
        state.generateLoading = true
        state.error = null
      })
      .addCase(generateCategories.fulfilled, (state, action) => {
        state.generateLoading = false
        console.log('Generated categories response:', action.payload)
        // API 응답이 { categories: [...], total: X, ... } 형식인 경우
        const newCategories = action.payload.categories || action.payload
        // Replace all categories with the newly generated ones
        state.categories = newCategories
        console.log('Updated categories:', state.categories)
      })
      .addCase(generateCategories.rejected, (state, action) => {
        state.generateLoading = false
        console.error('Generate categories failed:', action.error)
        state.error = action.error.message || 'Failed to generate categories'
      })
      // Delete category
      .addCase(deleteCategoryAsync.fulfilled, (state, action) => {
        state.categories = state.categories.filter(cat => cat.id !== action.payload)
      })
      .addCase(deleteCategoryAsync.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to delete category'
      })
  },
})

export const { resetGenerateState, clearCategories, deleteCategory } = categoriesSlice.actions
export default categoriesSlice.reducer