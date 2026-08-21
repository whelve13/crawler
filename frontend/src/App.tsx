import { HashRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CrawlReportPage from './pages/CrawlReport';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <HashRouter>
        <div className="p-4 sm:p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/report/:taskId" element={<CrawlReportPage />} />
          </Routes>
        </div>
      </HashRouter>
    </div>
  );
}

export default App;
