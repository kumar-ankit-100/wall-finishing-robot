"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns correct data."""
        response = client.get("/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "database" in data
        assert data["status"] == "healthy"


class TestWallEndpoints:
    """Test wall management endpoints."""
    
    def test_create_wall_no_obstacles(self, client):
        """Test creating a wall without obstacles."""
        payload = {
            "width": 5.0,
            "height": 5.0,
            "obstacles": []
        }
        
        response = client.post("/v1/walls", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["width"] == 5.0
        assert data["height"] == 5.0
        assert "id" in data
        assert "created_at" in data
        assert len(data["obstacles"]) == 0
    
    def test_create_wall_with_obstacles(self, client):
        """Test creating a wall with obstacles."""
        payload = {
            "width": 5.0,
            "height": 5.0,
            "obstacles": [
                {"x": 2.0, "y": 2.0, "width": 0.25, "height": 0.25}
            ]
        }
        
        response = client.post("/v1/walls", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert len(data["obstacles"]) == 1
        assert data["obstacles"][0]["x"] == 2.0
    
    def test_create_wall_invalid_dimensions(self, client):
        """Test creating wall with invalid dimensions fails."""
        payload = {
            "width": -5.0,
            "height": 5.0,
            "obstacles": []
        }
        
        response = client.post("/v1/walls", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_create_wall_obstacle_out_of_bounds(self, client):
        """Test obstacle outside wall bounds fails validation."""
        payload = {
            "width": 5.0,
            "height": 5.0,
            "obstacles": [
                {"x": 4.0, "y": 4.0, "width": 2.0, "height": 2.0}  # Extends beyond wall
            ]
        }
        
        response = client.post("/v1/walls", json=payload)
        assert response.status_code == 422
    
    def test_get_wall(self, client):
        """Test retrieving a wall by ID."""
        # Create wall first
        create_response = client.post("/v1/walls", json={
            "width": 3.0,
            "height": 4.0,
            "obstacles": []
        })
        wall_id = create_response.json()["id"]
        
        # Get wall
        response = client.get(f"/v1/walls/{wall_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == wall_id
        assert data["width"] == 3.0
        assert data["height"] == 4.0
    
    def test_get_nonexistent_wall(self, client):
        """Test getting nonexistent wall returns 404."""
        response = client.get("/v1/walls/999")
        assert response.status_code == 404


class TestTrajectoryEndpoints:
    """Test trajectory planning and management endpoints."""
    
    def test_create_plan(self, client):
        """Test creating a trajectory plan."""
        # Create wall first
        wall_response = client.post("/v1/walls", json={
            "width": 5.0,
            "height": 5.0,
            "obstacles": [
                {"x": 2.0, "y": 2.0, "width": 0.25, "height": 0.25}
            ]
        })
        wall_id = wall_response.json()["id"]
        
        # Create plan
        plan_payload = {
            "settings": {
                "pattern": "zigzag",
                "spacing": 0.1,
                "speed": 0.1,
                "clearance": 0.02,
                "resolution": 0.02
            }
        }
        
        response = client.post(f"/v1/trajectories/walls/{wall_id}/plan", json=plan_payload)
        assert response.status_code == 201
        
        data = response.json()
        assert "id" in data
        assert data["wall_id"] == wall_id
        assert data["length_m"] > 0
        assert data["duration_s"] > 0
        assert data["point_count"] > 0
    
    def test_create_plan_nonexistent_wall(self, client):
        """Test planning for nonexistent wall fails."""
        plan_payload = {"settings": {"pattern": "zigzag"}}
        
        response = client.post("/v1/trajectories/walls/999/plan", json=plan_payload)
        assert response.status_code == 404
    
    def test_create_plan_spiral_pattern(self, client):
        """Test creating plan with spiral pattern."""
        wall_response = client.post("/v1/walls", json={
            "width": 2.0,
            "height": 2.0,
            "obstacles": []
        })
        wall_id = wall_response.json()["id"]
        
        plan_payload = {
            "settings": {
                "pattern": "spiral",
                "spacing": 0.2
            }
        }
        
        response = client.post(f"/v1/trajectories/walls/{wall_id}/plan", json=plan_payload)
        assert response.status_code == 201
    
    def test_get_trajectory(self, client):
        """Test retrieving trajectory with points."""
        # Create wall and plan
        wall_response = client.post("/v1/walls", json={
            "width": 1.0,
            "height": 1.0,
            "obstacles": []
        })
        wall_id = wall_response.json()["id"]
        
        plan_response = client.post(
            f"/v1/trajectories/walls/{wall_id}/plan",
            json={"settings": {"pattern": "zigzag", "spacing": 0.5}}
        )
        trajectory_id = plan_response.json()["id"]
        
        # Get trajectory
        response = client.get(f"/v1/trajectories/{trajectory_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == trajectory_id
        assert "points" in data
        assert len(data["points"]) > 0
        assert "x" in data["points"][0]
        assert "y" in data["points"][0]
    
    def test_list_trajectories(self, client):
        """Test listing trajectories with pagination."""
        # Create wall and multiple plans
        wall_response = client.post("/v1/walls", json={
            "width": 2.0,
            "height": 2.0,
            "obstacles": []
        })
        wall_id = wall_response.json()["id"]
        
        # Create 3 trajectories
        for _ in range(3):
            client.post(
                f"/v1/trajectories/walls/{wall_id}/plan",
                json={"settings": {"pattern": "zigzag"}}
            )
        
        # List trajectories
        response = client.get("/v1/trajectories")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["items"]) == 3
    
    def test_list_trajectories_pagination(self, client):
        """Test trajectory listing pagination."""
        # Create wall and plans
        wall_response = client.post("/v1/walls", json={
            "width": 2.0,
            "height": 2.0,
            "obstacles": []
        })
        wall_id = wall_response.json()["id"]
        
        for _ in range(5):
            client.post(
                f"/v1/trajectories/walls/{wall_id}/plan",
                json={"settings": {"pattern": "zigzag"}}
            )
        
        # Get first page
        response = client.get("/v1/trajectories?page=1&page_size=2")
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["has_more"] is True
        
        # Get second page
        response = client.get("/v1/trajectories?page=2&page_size=2")
        data = response.json()
        assert len(data["items"]) == 2
    
    def test_list_trajectories_filter_by_wall(self, client):
        """Test filtering trajectories by wall ID."""
        # Create two walls
        wall1_response = client.post("/v1/walls", json={
            "width": 1.0,
            "height": 1.0,
            "obstacles": []
        })
        wall1_id = wall1_response.json()["id"]
        
        wall2_response = client.post("/v1/walls", json={
            "width": 2.0,
            "height": 2.0,
            "obstacles": []
        })
        wall2_id = wall2_response.json()["id"]
        
        # Create plans
        client.post(f"/v1/trajectories/walls/{wall1_id}/plan", json={"settings": {}})
        client.post(f"/v1/trajectories/walls/{wall2_id}/plan", json={"settings": {}})
        client.post(f"/v1/trajectories/walls/{wall2_id}/plan", json={"settings": {}})
        
        # Filter by wall2
        response = client.get(f"/v1/trajectories?wall_id={wall2_id}")
        data = response.json()
        assert data["total"] == 2
    
    def test_delete_trajectory(self, client):
        """Test deleting a trajectory."""
        # Create wall and plan
        wall_response = client.post("/v1/walls", json={
            "width": 1.0,
            "height": 1.0,
            "obstacles": []
        })
        wall_id = wall_response.json()["id"]
        
        plan_response = client.post(
            f"/v1/trajectories/walls/{wall_id}/plan",
            json={"settings": {}}
        )
        trajectory_id = plan_response.json()["id"]
        
        # Delete trajectory
        response = client.delete(f"/v1/trajectories/{trajectory_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/v1/trajectories/{trajectory_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_trajectory(self, client):
        """Test deleting nonexistent trajectory returns 404."""
        response = client.delete("/v1/trajectories/999")
        assert response.status_code == 404


class TestMetricsEndpoint:
    """Test metrics endpoint."""
    
    def test_metrics_enabled(self, client):
        """Test metrics endpoint when enabled."""
        # Make some requests to generate metrics
        client.get("/v1/health")
        client.get("/v1/health")
        
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "requests" in data
        assert "planner" in data
        assert "database" in data
        assert "entities" in data


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data
