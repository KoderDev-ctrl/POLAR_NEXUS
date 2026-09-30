import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import MissionDashboardCryoxRoutex16 from './pages/MissionDashboardCryoxRoutex16';
import IcebergExplorerCryox from './pages/IcebergExplorerCryox';
import VoyagePlannerRoutex16 from './pages/VoyagePlannerRoutex16';
import DynamicNavigationReplanning from './pages/DynamicNavigationReplanning';
import CryoxRoutex16AntarcticMaritimeNavigation from './pages/CryoxRoutex16AntarcticMaritimeNavigation';

function App() {
  return (
    <BrowserRouter>
      <div className="fixed bottom-0 left-0 right-0 bg-white p-2 z-[9999] flex justify-around text-xs border-t opacity-50 hover:opacity-100">
        <Link to="/">Dashboard</Link>
        <Link to="/iceberg">Iceberg</Link>
        <Link to="/voyage">Voyage</Link>
        <Link to="/dynamic">Dynamic Nav</Link>
        <Link to="/maritime">Maritime Nav</Link>
      </div>
      <Routes>
        <Route path="/" element={<MissionDashboardCryoxRoutex16 />} />
        <Route path="/iceberg" element={<IcebergExplorerCryox />} />
        <Route path="/voyage" element={<VoyagePlannerRoutex16 />} />
        <Route path="/dynamic" element={<DynamicNavigationReplanning />} />
        <Route path="/maritime" element={<CryoxRoutex16AntarcticMaritimeNavigation />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
