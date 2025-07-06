import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import axios from 'axios'

interface Content {
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

interface ContentState {
  contents: Content[]
  currentContent: Content | null
  loading: boolean
  error: string | null
}

const initialState: ContentState = {
  contents: [],
  currentContent: null,
  loading: false,
  error: null,
}

export const fetchContents = createAsyncThunk(
  'content/fetch',
  async (params?: { content_type?: string; category_id?: string }) => {
    const response = await axios.get('/api/v1/contents/list', { params })
    return response.data
  }
)

export const generateContent = createAsyncThunk(
  'content/generate',
  async (data: any) => {
    const response = await axios.post('/api/v1/contents/generate', data)
    return response.data
  }
)

export const deleteContentAsync = createAsyncThunk(
  'content/delete',
  async (contentId: string) => {
    await axios.delete(`/api/v1/contents/${contentId}`)
    return contentId
  }
)

const contentSlice = createSlice({
  name: 'content',
  initialState,
  reducers: {
    setCurrentContent: (state, action) => {
      state.currentContent = action.payload
    },
    deleteContent: (state, action) => {
      state.contents = state.contents.filter(content => content.id !== action.payload)
      if (state.currentContent?.id === action.payload) {
        state.currentContent = null
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch contents
      .addCase(fetchContents.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchContents.fulfilled, (state, action) => {
        state.loading = false
        // ContentListResponse 구조에서 contents 배열 추출
        state.contents = action.payload.contents || []
      })
      .addCase(fetchContents.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch contents'
      })
      // Generate content
      .addCase(generateContent.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(generateContent.fulfilled, (state, action) => {
        state.loading = false
        // API 응답 구조에 맞게 처리
        console.log('Content generation response:', action.payload)
        if (action.payload && action.payload.content) {
          // ContentResponse에서 GeneratedContent 추출
          const generatedContent = action.payload.content
          state.contents = [...state.contents, generatedContent]
          state.currentContent = generatedContent
        } else {
          console.error('Invalid content response:', action.payload)
          state.error = 'Invalid response format'
        }
      })
      .addCase(generateContent.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to generate content'
      })
      // Delete content
      .addCase(deleteContentAsync.fulfilled, (state, action) => {
        state.contents = state.contents.filter(content => content.id !== action.payload)
        if (state.currentContent?.id === action.payload) {
          state.currentContent = null
        }
      })
      .addCase(deleteContentAsync.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to delete content'
      })
  },
})

export const { setCurrentContent, deleteContent } = contentSlice.actions
export default contentSlice.reducer