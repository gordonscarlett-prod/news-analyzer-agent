import { Routes, Route, NavLink } from 'react-router-dom'
import { LineChart, Newspaper, LayoutGrid } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Trends from './pages/Trends'
import NewsFeed from './pages/NewsFeed'

function App() {
  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold text-sm">NA</div>
            <span className="font-semibold text-lg">News Analyzer Agent</span>
          </div>
          <nav className="flex items-center gap-1">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link-active' : 'nav-link'}>
              <span className="inline-flex items-center gap-1.5"><LayoutGrid size={16} /> Dashboard</span>
            </NavLink>
            <NavLink to="/trends" className={({ isActive }) => isActive ? 'nav-link-active' : 'nav-link'}>
              <span className="inline-flex items-center gap-1.5"><LineChart size={16} /> Trends</span>
            </NavLink>
            <NavLink to="/news" className={({ isActive }) => isActive ? 'nav-link-active' : 'nav-link'}>
              <span className="inline-flex items-center gap-1.5"><Newspaper size={16} /> News Feed</span>
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trends" element={<Trends />} />
          <Route path="/news" element={<NewsFeed />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
