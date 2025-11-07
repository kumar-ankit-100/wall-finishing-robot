import { useState } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { WallForm } from './components/WallForm';
import { CanvasViz } from './components/CanvasViz';
import { api } from './lib/api';
import type { Wall, TrajectoryDetail, WallCreateRequest, PlannerSettings } from './lib/types';
import './styles/tailwind.css';
import { Loader2, AlertCircle } from 'lucide-react';

function App() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeWall, setActiveWall] = useState<Wall | null>(null);
  const [activePath, setActivePath] = useState<TrajectoryDetail | null>(null);
  const [selectedPattern, setSelectedPattern] = useState<'zigzag' | 'spiral'>('zigzag');

  const createWallAndPath = async (wallData: WallCreateRequest) => {
    setErrorMessage(null);
    setIsGenerating(true);

    try {
      const newWall = await api.createWall(wallData);
      setActiveWall(newWall);

      // Spiral needs tighter spacing for complete coverage
      const toolSpacing = selectedPattern === 'spiral' ? 0.05 : 0.2;
      
      const plannerConfig: PlannerSettings = {
        pattern: selectedPattern,
        spacing: toolSpacing,
        speed: 0.1,
        clearance: 0.02,
        resolution: 0.01,
      };

      const pathResult = await api.createPlan(newWall.id, { settings: plannerConfig });
      const fullPath = await api.getTrajectory(pathResult.id, true);
      setActivePath(fullPath);
    } catch (err) {
      console.error('Failed to generate path:', err);
      setErrorMessage(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-900">
        
        <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-lg border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                    Wall Finishing Robot
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Autonomous Path Planning System
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Pattern:</label>
                <select
                  value={selectedPattern}
                  onChange={(e) => setSelectedPattern(e.target.value as 'zigzag' | 'spiral')}
                  className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  disabled={isGenerating}
                >
                  <option value="zigzag">Zigzag Coverage</option>
                  <option value="spiral">Spiral Coverage</option>
                </select>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-8">
          {errorMessage && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-r-lg shadow-sm animate-slide-up">
              <div className="flex items-start gap-3">
                <AlertCircle className="text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <h3 className="font-semibold text-red-900 dark:text-red-200">Error</h3>
                  <p className="text-sm text-red-800 dark:text-red-300 mt-1">{errorMessage}</p>
                </div>
              </div>
            </div>
          )}

          {isGenerating && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <Loader2 className="animate-spin text-blue-600 mx-auto mb-4" size={56} />
                <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
                  Generating coverage path...
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  This may take a few moments
                </p>
              </div>
            </div>
          )}

          {!isGenerating && !activePath && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <WallForm onSubmit={createWallAndPath} loading={isGenerating} />
              
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700">
                <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">
                  Getting Started
                </h2>
                <div className="space-y-5">
                  {[
                    { num: '1', title: 'Define Wall Dimensions', desc: 'Set the width and height in meters' },
                    { num: '2', title: 'Place Obstacles', desc: 'Add windows, vents, or other blocked areas' },
                    { num: '3', title: 'Choose Pattern', desc: 'Select zigzag for efficiency or spiral for aesthetics' },
                    { num: '4', title: 'Generate & Visualize', desc: 'Watch the robot path with playback controls' }
                  ].map((step) => (
                    <div key={step.num} className="flex items-start gap-4 group">
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-xl flex items-center justify-center font-bold shadow-md group-hover:scale-110 transition-transform">
                        {step.num}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">{step.title}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{step.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {!isGenerating && activePath && activeWall && (
            <div className="space-y-6 animate-fade-in">
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-100 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Active Pattern: <span className="font-bold text-gray-900 dark:text-gray-100 capitalize">{activePath.planner_settings.pattern}</span>
                    </span>
                  </div>
                  <button
                    onClick={async () => {
                      setErrorMessage(null);
                      setIsGenerating(true);
                      try {
                        const toolSpacing = selectedPattern === 'spiral' ? 0.05 : 0.2;
                        const plannerConfig: PlannerSettings = {
                          pattern: selectedPattern,
                          spacing: toolSpacing,
                          speed: 0.1,
                          clearance: 0.02,
                          resolution: 0.01,
                        };
                        const pathResult = await api.createPlan(activeWall.id, { settings: plannerConfig });
                        const fullPath = await api.getTrajectory(pathResult.id, true);
                        setActivePath(fullPath);
                      } catch (err) {
                        console.error('Regeneration failed:', err);
                        setErrorMessage(err instanceof Error ? err.message : 'Something went wrong');
                      } finally {
                        setIsGenerating(false);
                      }
                    }}
                    className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 font-medium"
                    disabled={isGenerating}
                  >
                    Regenerate with {selectedPattern === activePath.planner_settings.pattern ? 'Same' : selectedPattern.charAt(0).toUpperCase() + selectedPattern.slice(1)} Pattern
                  </button>
                </div>
              </div>
              
              <CanvasViz wall={activeWall} trajectory={activePath} />
              
              <button
                onClick={() => {
                  setActivePath(null);
                  setActiveWall(null);
                }}
                className="w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-all font-medium"
              >
                Create New Plan
              </button>
            </div>
          )}
        </main>

        <footer className="mt-16 border-t border-gray-200/50 dark:border-gray-700/50 bg-white/60 dark:bg-gray-900/60 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <p className="text-center text-sm text-gray-600 dark:text-gray-400">
              Wall Finishing Robot Control System · Version 1.0.0
            </p>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;
