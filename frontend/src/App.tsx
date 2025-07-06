import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import CategoriesPage from './pages/CategoriesPage'
import ContentGeneratorPage from './pages/ContentGeneratorPage'
import LibraryPage from './pages/LibraryPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="categories" element={<CategoriesPage />} />
        <Route path="generate" element={<ContentGeneratorPage />} />
        <Route path="library" element={<LibraryPage />} />
      </Route>
    </Routes>
  )
}

export default App