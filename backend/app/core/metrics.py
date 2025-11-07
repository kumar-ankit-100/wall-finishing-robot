"""
Application metrics tracking for observability.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict
from collections import defaultdict
import threading


@dataclass
class Metrics:
    """In-memory metrics storage."""
    
    request_count: int = 0
    error_count: int = 0
    total_response_time_ms: float = 0.0
    endpoint_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    endpoint_times: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    planner_runs: int = 0
    planner_total_time_ms: float = 0.0
    db_queries: int = 0
    db_total_time_ms: float = 0.0
    trajectories_created: int = 0
    walls_created: int = 0
    
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def record_request(self, endpoint: str, duration_ms: float, status_code: int) -> None:
        """Record an API request."""
        with self._lock:
            self.request_count += 1
            self.total_response_time_ms += duration_ms
            self.endpoint_counts[endpoint] += 1
            self.endpoint_times[endpoint] += duration_ms
            
            if status_code >= 400:
                self.error_count += 1
    
    def record_planner_run(self, duration_ms: float) -> None:
        """Record a planner execution."""
        with self._lock:
            self.planner_runs += 1
            self.planner_total_time_ms += duration_ms
    
    def record_db_query(self, duration_ms: float) -> None:
        """Record a database query."""
        with self._lock:
            self.db_queries += 1
            self.db_total_time_ms += duration_ms
    
    def record_trajectory_created(self) -> None:
        """Record trajectory creation."""
        with self._lock:
            self.trajectories_created += 1
    
    def record_wall_created(self) -> None:
        """Record wall creation."""
        with self._lock:
            self.walls_created += 1
    
    def get_avg_response_time(self) -> float:
        """Get average response time in ms."""
        with self._lock:
            if self.request_count == 0:
                return 0.0
            return self.total_response_time_ms / self.request_count
    
    def get_avg_planner_time(self) -> float:
        """Get average planner execution time in ms."""
        with self._lock:
            if self.planner_runs == 0:
                return 0.0
            return self.planner_total_time_ms / self.planner_runs
    
    def get_avg_db_time(self) -> float:
        """Get average DB query time in ms."""
        with self._lock:
            if self.db_queries == 0:
                return 0.0
            return self.db_total_time_ms / self.db_queries
    
    def get_error_rate(self) -> float:
        """Get error rate as percentage."""
        with self._lock:
            if self.request_count == 0:
                return 0.0
            return (self.error_count / self.request_count) * 100
    
    def to_dict(self) -> dict:
        """Export metrics as dictionary."""
        with self._lock:
            return {
                "requests": {
                    "total": self.request_count,
                    "errors": self.error_count,
                    "error_rate_percent": round(self.get_error_rate(), 2),
                    "avg_response_time_ms": round(self.get_avg_response_time(), 2),
                },
                "planner": {
                    "runs": self.planner_runs,
                    "avg_time_ms": round(self.get_avg_planner_time(), 2),
                },
                "database": {
                    "queries": self.db_queries,
                    "avg_time_ms": round(self.get_avg_db_time(), 2),
                },
                "entities": {
                    "walls_created": self.walls_created,
                    "trajectories_created": self.trajectories_created,
                },
                "endpoints": {
                    endpoint: {
                        "count": count,
                        "avg_time_ms": round(self.endpoint_times[endpoint] / count, 2)
                    }
                    for endpoint, count in self.endpoint_counts.items()
                }
            }


# Global metrics instance
_metrics = Metrics()


def get_metrics() -> Metrics:
    """Get global metrics instance."""
    return _metrics
