import { configureStore } from '@reduxjs/toolkit'
import categoriesReducer from './categoriesSlice'
import contentReducer from './contentSlice'

export const store = configureStore({
  reducer: {
    categories: categoriesReducer,
    content: contentReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch