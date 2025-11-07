"""
Tests for coverage planner algorithms.
"""
import pytest
from app.services.planner import CoveragePlanner, create_plan, Rectangle, Point


class TestRectangle:
    """Test Rectangle helper class."""
    
    def test_contains_point(self):
        """Test point containment check."""
        rect = Rectangle(0, 0, 10, 10)
        assert rect.contains_point(5, 5)
        assert rect.contains_point(0, 0)
        assert rect.contains_point(10, 10)
        assert not rect.contains_point(11, 5)
        assert not rect.contains_point(5, 11)
    
    def test_intersects(self):
        """Test rectangle intersection."""
        rect1 = Rectangle(0, 0, 10, 10)
        rect2 = Rectangle(5, 5, 10, 10)
        rect3 = Rectangle(20, 20, 5, 5)
        
        assert rect1.intersects(rect2)
        assert rect2.intersects(rect1)
        assert not rect1.intersects(rect3)


class TestPoint:
    """Test Point helper class."""
    
    def test_distance(self):
        """Test distance calculation."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert p1.distance_to(p2) == 5.0
        
        p3 = Point(1, 1)
        p4 = Point(1, 1)
        assert p3.distance_to(p4) == 0.0


class TestCoveragePlanner:
    """Test coverage planning algorithms."""
    
    def test_planner_initialization(self):
        """Test planner initializes correctly."""
        planner = CoveragePlanner(
            wall_width=5.0,
            wall_height=5.0,
            obstacles=[],
            spacing=0.05
        )
        assert planner.wall.width == 5.0
        assert planner.wall.height == 5.0
        assert len(planner.obstacles) == 0
    
    def test_planner_with_obstacles(self):
        """Test planner with obstacles."""
        obstacles = [(2.0, 2.0, 0.5, 0.5)]
        planner = CoveragePlanner(
            wall_width=5.0,
            wall_height=5.0,
            obstacles=obstacles,
            spacing=0.05,
            clearance=0.02
        )
        assert len(planner.obstacles) == 1
        assert len(planner.expanded_obstacles) == 1
        
        # Expanded obstacle should be larger
        exp_obs = planner.expanded_obstacles[0]
        assert exp_obs.x < 2.0
        assert exp_obs.width > 0.5
    
    def test_is_point_valid(self):
        """Test point validation."""
        obstacles = [(2.0, 2.0, 1.0, 1.0)]
        planner = CoveragePlanner(
            wall_width=5.0,
            wall_height=5.0,
            obstacles=obstacles,
            clearance=0.0
        )
        
        # Point outside wall
        assert not planner._is_point_valid(6.0, 3.0)
        
        # Point inside obstacle
        assert not planner._is_point_valid(2.5, 2.5)
        
        # Valid point
        assert planner._is_point_valid(0.5, 0.5)
    
    def test_zigzag_pattern_no_obstacles(self):
        """Test zigzag pattern on empty wall."""
        planner = CoveragePlanner(
            wall_width=1.0,
            wall_height=1.0,
            obstacles=[],
            spacing=0.2,
            resolution=0.1
        )
        
        points = planner.plan_zigzag()
        assert len(points) > 0
        
        # All points should be within wall
        for x, y in points:
            assert 0 <= x <= 1.0
            assert 0 <= y <= 1.0
    
    def test_zigzag_pattern_with_obstacle(self):
        """Test zigzag pattern avoids obstacles."""
        obstacles = [(0.4, 0.4, 0.2, 0.2)]
        planner = CoveragePlanner(
            wall_width=1.0,
            wall_height=1.0,
            obstacles=obstacles,
            spacing=0.1,
            clearance=0.0,
            resolution=0.05
        )
        
        points = planner.plan_zigzag()
        assert len(points) > 0
        
        # No points should be inside obstacle
        for x, y in points:
            assert not (0.4 <= x <= 0.6 and 0.4 <= y <= 0.6)
    
    def test_spiral_pattern_no_obstacles(self):
        """Test spiral pattern on empty wall."""
        planner = CoveragePlanner(
            wall_width=1.0,
            wall_height=1.0,
            obstacles=[],
            spacing=0.2,
            resolution=0.1
        )
        
        points = planner.plan_spiral()
        assert len(points) > 0
        
        # All points should be within wall
        for x, y in points:
            assert 0 <= x <= 1.0
            assert 0 <= y <= 1.0
    
    def test_sample_case_5x5_with_window(self):
        """Test the assignment sample case: 5m x 5m with 0.25m x 0.25m window."""
        obstacles = [(2.0, 2.0, 0.25, 0.25)]  # Window somewhere in middle
        
        result = create_plan(
            wall_width=5.0,
            wall_height=5.0,
            obstacles=obstacles,
            pattern="zigzag",
            spacing=0.05,
            clearance=0.02,
            resolution=0.01,
            speed=0.1
        )
        
        assert "points" in result
        assert "length_m" in result
        assert "duration_s" in result
        assert "point_count" in result
        
        assert len(result["points"]) > 0
        assert result["length_m"] > 0
        assert result["duration_s"] > 0
        assert result["point_count"] == len(result["points"])
    
    def test_invalid_pattern(self):
        """Test invalid pattern raises error."""
        planner = CoveragePlanner(1.0, 1.0, [])
        
        with pytest.raises(ValueError, match="Unknown pattern"):
            planner.plan("invalid_pattern")
    
    def test_obstacle_larger_than_wall(self):
        """Test handling of obstacle larger than wall."""
        # This should still work but may produce minimal or no points
        obstacles = [(0, 0, 10, 10)]
        planner = CoveragePlanner(
            wall_width=5.0,
            wall_height=5.0,
            obstacles=obstacles,
            spacing=0.1
        )
        
        # May raise or return empty - both acceptable
        try:
            points = planner.plan_zigzag()
            # If it returns, should be empty or minimal
            assert len(points) <= 10
        except ValueError:
            # Acceptable to raise error
            pass
    
    def test_path_length_calculation(self):
        """Test path length is calculated correctly."""
        result = create_plan(
            wall_width=1.0,
            wall_height=1.0,
            obstacles=[],
            pattern="zigzag",
            spacing=0.5,
            resolution=0.1,
            speed=0.1
        )
        
        # Manually calculate approximate length
        points = result["points"]
        manual_length = 0.0
        for i in range(len(points) - 1):
            p1 = Point(points[i]["x"], points[i]["y"])
            p2 = Point(points[i + 1]["x"], points[i + 1]["y"])
            manual_length += p1.distance_to(p2)
        
        # Should be close (within 1% due to rounding)
        assert abs(result["length_m"] - manual_length) < manual_length * 0.01
    
    def test_duration_calculation(self):
        """Test duration is calculated from length and speed."""
        speed = 0.5  # m/s
        result = create_plan(
            wall_width=2.0,
            wall_height=2.0,
            obstacles=[],
            pattern="zigzag",
            spacing=0.2,
            speed=speed
        )
        
        expected_duration = result["length_m"] / speed
        assert abs(result["duration_s"] - expected_duration) < 0.01
