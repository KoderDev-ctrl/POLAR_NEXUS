import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import SeaIce from './pages/SeaIce';
import IcebergExplorerCryox from './pages/IcebergExplorerCryox';
import VoyagePlannerRoutex16 from './pages/VoyagePlannerRoutex16';

function Navigation() {
  const location = useLocation();
  return (
    <nav className="fixed top-0 w-full z-50 bg-white/90 backdrop-blur-md border-b border-surface-container-low shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[24px]">ac_unit</span>
              <span className="font-headline-sm text-primary tracking-widest uppercase">Polar Nexus</span>
            </Link>
            <div className="hidden sm:flex sm:space-x-8">
              <Link to="/dashboard" className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/dashboard' ? 'border-primary text-primary' : 'border-transparent text-secondary hover:border-surface-variant hover:text-primary'}`}>
                Dashboard
              </Link>
              <Link to="/iceberg-tracking" className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/iceberg-tracking' ? 'border-primary text-primary' : 'border-transparent text-secondary hover:border-surface-variant hover:text-primary'}`}>
                Iceberg Tracking
              </Link>
              <Link to="/vessel-navigation" className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/vessel-navigation' ? 'border-primary text-primary' : 'border-transparent text-secondary hover:border-surface-variant hover:text-primary'}`}>
                Vessel Navigation
              </Link>
              <Link to="/sea-ice" className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/sea-ice' ? 'border-primary text-primary' : 'border-transparent text-secondary hover:border-surface-variant hover:text-primary'}`}>
                Sea Ice Prediction
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <div className="pt-16 min-h-screen bg-surface">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/iceberg-tracking" element={<IcebergExplorerCryox />} />
          <Route path="/vessel-navigation" element={<VoyagePlannerRoutex16 />} />
          <Route path="/sea-ice" element={<SeaIce />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
