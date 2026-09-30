import React from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <main className="w-full min-h-[calc(100vh-64px)] flex items-center justify-center p-8 bg-surface">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left Side: Text */}
        <div className="flex flex-col space-y-6">
          <h1 className="text-5xl font-headline-xl text-primary leading-tight">
            POLAR NEXUS
          </h1>
          <p className="text-lg font-body-lg text-on-surface-variant max-w-lg leading-relaxed">
            Advanced maritime decision support for the Antarctic. 
            Polar Nexus provides real-time iceberg trajectory prediction, 
            intelligent voyage planning, and sea-ice prediction to ensure safe and efficient navigation in extreme polar environments.
          </p>
          <div className="flex flex-wrap gap-4 pt-4">
            <Link to="/dashboard" className="px-6 py-3 bg-primary text-on-primary rounded-lg font-label-caps uppercase tracking-wider hover:bg-[#17324D] transition-colors shadow-sm">
              Dashboard
            </Link>
            <Link to="/iceberg-tracking" className="px-6 py-3 bg-surface-container-low text-primary rounded-lg font-label-caps uppercase tracking-wider hover:bg-surface-container transition-colors shadow-sm border border-surface-variant">
              Iceberg Tracking
            </Link>
            <Link to="/vessel-navigation" className="px-6 py-3 bg-surface-container-low text-primary rounded-lg font-label-caps uppercase tracking-wider hover:bg-surface-container transition-colors shadow-sm border border-surface-variant">
              Vessel Navigation
            </Link>
            <Link to="/sea-ice" className="px-6 py-3 bg-surface-container-low text-primary rounded-lg font-label-caps uppercase tracking-wider hover:bg-surface-container transition-colors shadow-sm border border-surface-variant">
              Sea Ice
            </Link>
          </div>
        </div>

        {/* Right Side: Image */}
        <div className="relative rounded-2xl overflow-hidden shadow-2xl aspect-[4/3] bg-surface-container">
          <img 
            src="/hero.jpg" 
            alt="Majestic 3D Polar Iceberg" 
            className="w-full h-full object-cover"
          />
          {/* Subtle gradient overlay for elegance */}
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 to-transparent pointer-events-none"></div>
        </div>
      </div>
    </main>
  );
}
