/**
 * TypeScript type definitions for the API.
 */

export interface Point {
  x: number;
  y: number;
}

export interface Obstacle {
  id?: number;
  wall_id?: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Wall {
  id: number;
  width: number;
  height: number;
  created_at: string;
  obstacles: Obstacle[];
}

export interface WallCreateRequest {
  width: number;
  height: number;
  obstacles: Omit<Obstacle, 'id' | 'wall_id'>[];
}

export interface PlannerSettings {
  pattern: 'zigzag' | 'spiral';
  spacing?: number;
  speed?: number;
  clearance?: number;
  resolution?: number;
}

export interface PlanRequest {
  settings: PlannerSettings;
}

export interface Trajectory {
  id: number;
  wall_id: number;
  planner_settings: PlannerSettings;
  length_m: number;
  duration_s: number;
  point_count: number;
  created_at: string;
}

export interface TrajectoryDetail extends Trajectory {
  points: Point[];
  wall?: Wall;
}

export interface TrajectoryListResponse {
  items: Trajectory[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  database: string;
}

export interface MetricsResponse {
  requests: {
    total: number;
    errors: number;
    error_rate_percent: number;
    avg_response_time_ms: number;
  };
  planner: {
    runs: number;
    avg_time_ms: number;
  };
  database: {
    queries: number;
    avg_time_ms: number;
  };
  entities: {
    walls_created: number;
    trajectories_created: number;
  };
  endpoints: Record<string, { count: number; avg_time_ms: number }>;
}

export interface PresetWall {
  name: string;
  description: string;
  width: number;
  height: number;
  obstacles: Omit<Obstacle, 'id' | 'wall_id'>[];
}
