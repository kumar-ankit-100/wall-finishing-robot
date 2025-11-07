import { useEffect, useRef, useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, Download } from 'lucide-react';
import type { Point, Wall, TrajectoryDetail } from '../lib/types';

interface CanvasVizProps {
  wall: Wall;
  trajectory: TrajectoryDetail;
}

export function CanvasViz({ wall, trajectory }: CanvasVizProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [speed, setSpeed] = useState(1);
  const animationRef = useRef<number>();
  const lastTimeRef = useRef<number>(0);

  const padding = 40;
  const canvasWidth = 800;
  const canvasHeight = 600;

  const scale = Math.min(
    (canvasWidth - 2 * padding) / wall.width,
    (canvasHeight - 2 * padding) / wall.height
  );

  const toCanvas = (x: number, y: number): [number, number] => {
    return [padding + x * scale, canvasHeight - padding - y * scale];
  };

  const drawScene = (ctx: CanvasRenderingContext2D, robotIndex: number) => {
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // Background
    ctx.fillStyle = '#f9fafb';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    // Wall
    const [wallX, wallY] = toCanvas(0, 0);
    const [wallX2, wallY2] = toCanvas(wall.width, wall.height);
    ctx.strokeStyle = '#1f2937';
    ctx.lineWidth = 2;
    ctx.strokeRect(wallX, wallY2, wallX2 - wallX, wallY - wallY2);

    // Grid
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 0.5;
    const gridSpacing = 0.5 * scale;
    for (let x = wallX; x <= wallX2; x += gridSpacing) {
      ctx.beginPath();
      ctx.moveTo(x, wallY2);
      ctx.lineTo(x, wallY);
      ctx.stroke();
    }
    for (let y = wallY2; y <= wallY; y += gridSpacing) {
      ctx.beginPath();
      ctx.moveTo(wallX, y);
      ctx.lineTo(wallX2, y);
      ctx.stroke();
    }

    // Obstacles with clearance zones
    const clearance = 0.02; // 2cm clearance (matching backend default)
    wall.obstacles.forEach((obs) => {
      // Draw clearance zone (expanded area)
      const [cx, cy] = toCanvas(obs.x - clearance, obs.y - clearance);
      const [cx2, cy2] = toCanvas(obs.x + obs.width + clearance, obs.y + obs.height + clearance);
      ctx.fillStyle = '#fee2e2';
      ctx.fillRect(cx, cy2, cx2 - cx, cy - cy2);
      ctx.strokeStyle = '#fca5a5';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.strokeRect(cx, cy2, cx2 - cx, cy - cy2);
      ctx.setLineDash([]);
      
      // Draw actual obstacle
      const [ox, oy] = toCanvas(obs.x, obs.y);
      const [ox2, oy2] = toCanvas(obs.x + obs.width, obs.y + obs.height);
      ctx.fillStyle = '#fecaca';
      ctx.fillRect(ox, oy2, ox2 - ox, oy - oy2);
      ctx.strokeStyle = '#dc2626';
      ctx.lineWidth = 2;
      ctx.strokeRect(ox, oy2, ox2 - ox, oy - oy2);
    });

    // Path - draw only continuous segments, skip jumps over obstacles
    if (trajectory.points.length > 0) {
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 1.5;
      ctx.globalAlpha = 0.4;
      
      // Helper to check if segment is a "jump" (crosses obstacle or is too long)
      const isJump = (p1: Point, p2: Point): boolean => {
        const dx = Math.abs(p2.x - p1.x);
        const dy = Math.abs(p2.y - p1.y);
        
        // Detect jumps:
        // 1. Any vertical movement (different y values) = row change = jump
        // 2. Large horizontal movement (> spacing * 1.5) = segment jump
        // 3. Any diagonal movement = jump
        const rowSpacing = 0.2; // Match backend spacing
        return dy > 0.01 || dx > (rowSpacing * 1.5) || (dx > 0.05 && dy > 0.001);
      };
      
      ctx.beginPath();
      let [px, py] = toCanvas(trajectory.points[0].x, trajectory.points[0].y);
      ctx.moveTo(px, py);
      
      for (let i = 1; i < trajectory.points.length; i++) {
        const [nextX, nextY] = toCanvas(trajectory.points[i].x, trajectory.points[i].y);
        
        if (isJump(trajectory.points[i - 1], trajectory.points[i])) {
          // Jump detected - start new path segment
          ctx.stroke();
          ctx.beginPath();
          ctx.moveTo(nextX, nextY);
        } else {
          // Continue current segment
          ctx.lineTo(nextX, nextY);
        }
        
        px = nextX;
        py = nextY;
      }
      ctx.stroke();
      ctx.globalAlpha = 1;

      // Visited path (up to current index) - also skip jumps
      if (robotIndex > 0) {
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 2;
        ctx.beginPath();
        let [sx, sy] = toCanvas(trajectory.points[0].x, trajectory.points[0].y);
        ctx.moveTo(sx, sy);
        
        for (let i = 1; i <= robotIndex; i++) {
          const [nextX, nextY] = toCanvas(trajectory.points[i].x, trajectory.points[i].y);
          
          if (isJump(trajectory.points[i - 1], trajectory.points[i])) {
            // Jump detected - draw dotted line and start new segment
            ctx.stroke();
            
            // Draw dotted jump line
            ctx.save();
            ctx.strokeStyle = '#9ca3af';
            ctx.lineWidth = 1;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(sx, sy);
            ctx.lineTo(nextX, nextY);
            ctx.stroke();
            ctx.restore();
            
            // Start new solid segment
            ctx.strokeStyle = '#10b981';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(nextX, nextY);
          } else {
            ctx.lineTo(nextX, nextY);
          }
          
          sx = nextX;
          sy = nextY;
        }
        ctx.stroke();
      }

      // Robot
      if (robotIndex < trajectory.points.length) {
        const point = trajectory.points[robotIndex];
        const [rx, ry] = toCanvas(point.x, point.y);

        // Robot body
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(rx, ry, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#991b1b';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Direction indicator
        if (robotIndex < trajectory.points.length - 1) {
          const nextPoint = trajectory.points[robotIndex + 1];
          const dx = nextPoint.x - point.x;
          const dy = nextPoint.y - point.y;
          const angle = Math.atan2(-dy, dx);
          ctx.strokeStyle = '#991b1b';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(rx, ry);
          ctx.lineTo(rx + Math.cos(angle) * 12, ry + Math.sin(angle) * 12);
          ctx.stroke();
        }
      }

      // Start point
      const [s0x, s0y] = toCanvas(trajectory.points[0].x, trajectory.points[0].y);
      ctx.fillStyle = '#10b981';
      ctx.beginPath();
      ctx.arc(s0x, s0y, 4, 0, Math.PI * 2);
      ctx.fill();

      // End point
      const lastPoint = trajectory.points[trajectory.points.length - 1];
      const [enx, eny] = toCanvas(lastPoint.x, lastPoint.y);
      ctx.fillStyle = '#8b5cf6';
      ctx.beginPath();
      ctx.arc(enx, eny, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    // Labels
    ctx.fillStyle = '#374151';
    ctx.font = '12px sans-serif';
    ctx.fillText(`${wall.width}m`, wallX + (wallX2 - wallX) / 2 - 15, wallY + 25);
    ctx.save();
    ctx.translate(wallX - 25, wallY2 + (wallY - wallY2) / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText(`${wall.height}m`, -15, 0);
    ctx.restore();
  };

  const animate = (timestamp: number) => {
    if (!lastTimeRef.current) lastTimeRef.current = timestamp;
    const delta = timestamp - lastTimeRef.current;

    if (delta > (1000 / (speed * 10))) {
      setCurrentIndex((prev) => {
        if (prev >= trajectory.points.length - 1) {
          setPlaying(false);
          return prev;
        }
        return prev + 1;
      });
      lastTimeRef.current = timestamp;
    }

    if (playing) {
      animationRef.current = requestAnimationFrame(animate);
    }
  };

  useEffect(() => {
    if (playing) {
      lastTimeRef.current = 0;
      animationRef.current = requestAnimationFrame(animate);
    } else {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [playing, speed]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    drawScene(ctx, currentIndex);
  }, [currentIndex, wall, trajectory]);

  const downloadSnapshot = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const url = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = `trajectory-${trajectory.id}.png`;
    link.href = url;
    link.click();
  };

  const progress = (currentIndex / (trajectory.points.length - 1)) * 100;

  return (
    <div className="card animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          Trajectory Visualization
        </h2>
        <button onClick={downloadSnapshot} className="btn-secondary flex items-center gap-2">
          <Download size={18} />
          Snapshot
        </button>
      </div>

      <canvas
        ref={canvasRef}
        width={canvasWidth}
        height={canvasHeight}
        className="border border-gray-300 dark:border-gray-600 rounded-lg mx-auto"
      />

      <div className="mt-4 space-y-4">
        <div>
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
            <span>Progress</span>
            <span>
              {currentIndex} / {trajectory.points.length - 1} points
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-200"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => setCurrentIndex(0)}
            className="btn-secondary"
            title="Reset to start"
          >
            <SkipBack size={20} />
          </button>
          <button
            onClick={() => setPlaying(!playing)}
            className="btn-primary px-6"
          >
            {playing ? <Pause size={20} /> : <Play size={20} />}
          </button>
          <button
            onClick={() => setCurrentIndex(trajectory.points.length - 1)}
            className="btn-secondary"
            title="Jump to end"
          >
            <SkipForward size={20} />
          </button>
        </div>

        {/* Quick jump buttons */}
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Quick Jump
          </label>
          <div className="grid grid-cols-4 gap-2">
            <button
              onClick={() => setCurrentIndex(Math.floor((trajectory.points.length - 1) * 0.25))}
              className="btn-secondary text-sm py-2"
            >
              25%
            </button>
            <button
              onClick={() => setCurrentIndex(Math.floor((trajectory.points.length - 1) * 0.5))}
              className="btn-secondary text-sm py-2"
            >
              50%
            </button>
            <button
              onClick={() => setCurrentIndex(Math.floor((trajectory.points.length - 1) * 0.75))}
              className="btn-secondary text-sm py-2"
            >
              75%
            </button>
            <button
              onClick={() => setCurrentIndex(trajectory.points.length - 1)}
              className="btn-secondary text-sm py-2"
            >
              100%
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Playback Speed: {speed}x
          </label>
          <div className="flex items-center gap-2">
            <input
              type="range"
              min="0.25"
              max="20"
              step="0.25"
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="flex-1"
            />
            <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[60px] text-right">
              {speed.toFixed(2)}x
            </span>
          </div>
          <div className="flex gap-2 mt-2">
            <button onClick={() => setSpeed(1)} className="btn-secondary text-xs px-3 py-1">1x</button>
            <button onClick={() => setSpeed(2)} className="btn-secondary text-xs px-3 py-1">2x</button>
            <button onClick={() => setSpeed(5)} className="btn-secondary text-xs px-3 py-1">5x</button>
            <button onClick={() => setSpeed(10)} className="btn-secondary text-xs px-3 py-1">10x</button>
            <button onClick={() => setSpeed(20)} className="btn-secondary text-xs px-3 py-1">20x</button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="card bg-gray-50 dark:bg-gray-700 p-3">
            <div className="text-gray-600 dark:text-gray-400">Length</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {trajectory.length_m.toFixed(2)}m
            </div>
          </div>
          <div className="card bg-gray-50 dark:bg-gray-700 p-3">
            <div className="text-gray-600 dark:text-gray-400">Duration</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {trajectory.duration_s.toFixed(1)}s
            </div>
          </div>
          <div className="card bg-gray-50 dark:bg-gray-700 p-3">
            <div className="text-gray-600 dark:text-gray-400">Pattern</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {trajectory.planner_settings.pattern}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
