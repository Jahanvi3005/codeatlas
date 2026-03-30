import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import RepoWorkspace from './pages/RepoWorkspace';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground font-sans selection:bg-accent/30 selection:text-foreground">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/repo/:id" element={<Dashboard />} />
          <Route path="/repo/:id/workspace" element={<RepoWorkspace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
