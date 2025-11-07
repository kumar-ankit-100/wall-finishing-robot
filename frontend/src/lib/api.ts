/**
 * API client for backend communication with retry logic.
 */

import type {
  Wall,
  WallCreateRequest,
  Trajectory,
  TrajectoryDetail,
  TrajectoryListResponse,
  PlanRequest,
  HealthResponse,
  MetricsResponse,
} from './types';

// Use environment variable or default to proxied path
const API_BASE = import.meta.env.VITE_API_URL || '';  // Empty string uses Vite proxy in dev

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = 3
): Promise<Response> {
  let lastError: Error | null = null;

  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.detail || `HTTP ${response.status}`,
          response.status,
          errorData
        );
      }

      return response;
    } catch (error) {
      lastError = error as Error;
      if (i < retries - 1) {
        // Exponential backoff
        await new Promise((resolve) => setTimeout(resolve, Math.pow(2, i) * 1000));
      }
    }
  }

  throw lastError || new Error('Request failed');
}

export const api = {
  // Health & Metrics
  async getHealth(): Promise<HealthResponse> {
    const response = await fetchWithRetry(`${API_BASE}/v1/health`);
    return response.json();
  },

  async getMetrics(): Promise<MetricsResponse> {
    const response = await fetchWithRetry(`${API_BASE}/metrics`);
    return response.json();
  },

  // Walls
  async createWall(data: WallCreateRequest): Promise<Wall> {
    const response = await fetchWithRetry(`${API_BASE}/v1/walls`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async getWall(wallId: number): Promise<Wall> {
    const response = await fetchWithRetry(`${API_BASE}/v1/walls/${wallId}`);
    return response.json();
  },

  // Trajectories
  async createPlan(wallId: number, planRequest: PlanRequest): Promise<Trajectory> {
    const response = await fetchWithRetry(
      `${API_BASE}/v1/trajectories/walls/${wallId}/plan`,
      {
        method: 'POST',
        body: JSON.stringify(planRequest),
      }
    );
    return response.json();
  },

  async getTrajectory(
    trajectoryId: number,
    includeWall = false
  ): Promise<TrajectoryDetail> {
    const url = `${API_BASE}/v1/trajectories/${trajectoryId}?include_wall=${includeWall}`;
    const response = await fetchWithRetry(url);
    return response.json();
  },

  async listTrajectories(params?: {
    wallId?: number;
    pattern?: string;
    page?: number;
    pageSize?: number;
  }): Promise<TrajectoryListResponse> {
    const queryParams = new URLSearchParams();
    if (params?.wallId) queryParams.set('wall_id', params.wallId.toString());
    if (params?.pattern) queryParams.set('pattern', params.pattern);
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.pageSize) queryParams.set('page_size', params.pageSize.toString());

    const url = `${API_BASE}/v1/trajectories?${queryParams}`;
    const response = await fetchWithRetry(url);
    return response.json();
  },

  async deleteTrajectory(trajectoryId: number): Promise<void> {
    await fetchWithRetry(`${API_BASE}/v1/trajectories/${trajectoryId}`, {
      method: 'DELETE',
    });
  },
};

export { ApiError };
