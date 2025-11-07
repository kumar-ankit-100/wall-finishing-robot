import { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import type { WallCreateRequest, Obstacle } from '../lib/types';

interface WallFormProps {
  onSubmit: (wall: WallCreateRequest) => Promise<void>;
  loading: boolean;
}

export function WallForm({ onSubmit, loading }: WallFormProps) {
  const [wallWidth, setWallWidth] = useState('5.0');
  const [wallHeight, setWallHeight] = useState('5.0');
  const [obstacleList, setObstacleList] = useState<Omit<Obstacle, 'id' | 'wall_id'>[]>([
    { x: 1.5, y: 3.5, width: 1.2, height: 0.8 },
    { x: 3.5, y: 1.0, width: 0.4, height: 0.4 },
    { x: 0.5, y: 0.5, width: 0.6, height: 0.6 },
  ]);

  const addNewObstacle = () => {
    setObstacleList([...obstacleList, { x: 0, y: 0, width: 0.5, height: 0.5 }]);
  };

  const deleteObstacle = (idx: number) => {
    setObstacleList(obstacleList.filter((_, i) => i !== idx));
  };

  const modifyObstacle = (idx: number, property: keyof Obstacle, val: number) => {
    const updated = [...obstacleList];
    updated[idx] = { ...updated[idx], [property]: val };
    setObstacleList(updated);
  };

  const submitForm = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      width: parseFloat(wallWidth),
      height: parseFloat(wallHeight),
      obstacles: obstacleList,
    });
  };

  return (
    <form onSubmit={submitForm} className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700 animate-fade-in">
      <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">
        Wall Configuration
      </h2>

      <div className="grid grid-cols-2 gap-5 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Width (meters)
          </label>
          <input
            type="number"
            step="0.1"
            min="0.1"
            value={wallWidth}
            onChange={(e) => setWallWidth(e.target.value)}
            className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Height (meters)
          </label>
          <input
            type="number"
            step="0.1"
            min="0.1"
            value={wallHeight}
            onChange={(e) => setWallHeight(e.target.value)}
            className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            required
          />
        </div>
      </div>

      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Obstacles
          </h3>
          <button
            type="button"
            onClick={addNewObstacle}
            className="flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-all font-medium"
          >
            <Plus size={18} />
            Add
          </button>
        </div>

        {obstacleList.length === 0 && (
          <p className="text-gray-500 dark:text-gray-400 text-sm italic py-4 text-center bg-gray-50 dark:bg-gray-900/50 rounded-lg">
            No obstacles defined
          </p>
        )}

        {obstacleList.map((obs, idx) => (
          <div
            key={idx}
            className="mb-4 p-4 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-xl"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Obstacle {idx + 1}
              </span>
              <button
                type="button"
                onClick={() => deleteObstacle(idx)}
                className="p-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                aria-label="Remove obstacle"
              >
                <Trash2 size={18} />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">
                  X Position
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={obs.x}
                  onChange={(e) => modifyObstacle(idx, 'x', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">
                  Y Position
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={obs.y}
                  onChange={(e) => modifyObstacle(idx, 'y', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">
                  Width
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={obs.width}
                  onChange={(e) => modifyObstacle(idx, 'width', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">
                  Height
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={obs.height}
                  onChange={(e) => modifyObstacle(idx, 'height', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full px-6 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg"
      >
        {loading ? 'Generating...' : 'Generate Coverage Plan'}
      </button>
    </form>
  );
}
