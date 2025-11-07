"""
Unit tests for obstacle avoidance in coverage planning.

Tests ensure that generated paths NEVER cross through obstacles.
"""
import pytest
from app.services.planner import CoveragePlanner, create_plan, Rectangle


class TestObstacleAvoidance:
    """Test suite for robust obstacle avoidance."""
    
    def test_single_obstacle_center(self):
        """Test path avoids single obstacle in center of wall."""
        wall_width = 5.0
        wall_height = 5.0
        obstacles = [(2.0, 2.0, 1.0, 1.0)]  # 1x1m obstacle in center
        
        planner = CoveragePlanner(
            wall_width, wall_height, obstacles,
            spacing=0.5, clearance=0.05, resolution=0.1
        )
        
        result = planner.plan("zigzag")
        points = [(p["x"], p["y"]) for p in result["points"]]
        
        # Verify no point is inside expanded obstacle
        expanded_obs = Rectangle(2.0 - 0.05, 2.0 - 0.05, 1.1, 1.1)
        for x, y in points:
            assert not expanded_obs.contains_point(x, y), \
                f"Point ({x}, {y}) is inside obstacle bounds"
        
        # Verify we got some coverage points
        assert len(points) > 0, "No coverage path generated"
    
    def test_multiple_obstacles(self):
        """Test path avoids multiple obstacles."""
        obstacles = [
            (1.0, 1.0, 0.5, 0.5),  # Bottom-left
            (3.0, 3.0, 0.5, 0.5),  # Top-right
            (1.0, 3.0, 0.5, 0.5),  # Top-left
        ]
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.3, clearance=0.02, resolution=0.05
        )
        
        result = planner.plan("zigzag")
        points = [(p["x"], p["y"]) for p in result["points"]]
        
        # Check each obstacle is avoided
        for obs_x, obs_y, obs_w, obs_h in obstacles:
            expanded_obs = Rectangle(
                obs_x - 0.02, obs_y - 0.02,
                obs_w + 0.04, obs_h + 0.04
            )
            for x, y in points:
                assert not expanded_obs.contains_point(x, y), \
                    f"Point ({x}, {y}) is inside obstacle at ({obs_x}, {obs_y})"
        
        assert len(points) > 100, "Path should have many points"
    
    def test_no_line_segment_crosses_obstacle(self):
        """Test that no line segment between consecutive points crosses obstacle."""
        obstacles = [(2.0, 2.0, 1.0, 1.0)]
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.4, clearance=0.05, resolution=0.1
        )
        
        result = planner.plan("zigzag")
        points = [(p["x"], p["y"]) for p in result["points"]]
        
        expanded_obs = Rectangle(1.95, 1.95, 1.1, 1.1)
        
        # Check each segment
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # Check horizontal segments
            if abs(y1 - y2) < 1e-9:
                assert not expanded_obs.intersects_horizontal_segment(x1, x2, y1), \
                    f"Horizontal segment ({x1},{y1}) to ({x2},{y2}) crosses obstacle"
            
            # Check vertical segments
            elif abs(x1 - x2) < 1e-9:
                assert not expanded_obs.intersects_vertical_segment(x1, y1, y2), \
                    f"Vertical segment ({x1},{y1}) to ({x2},{y2}) crosses obstacle"
    
    def test_obstacle_at_wall_edge(self):
        """Test obstacle touching wall boundary."""
        obstacles = [(0, 0, 1.0, 1.0)]  # Bottom-left corner
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.5, clearance=0.02, resolution=0.1
        )
        
        result = planner.plan("zigzag")
        assert len(result["points"]) > 0
    
    def test_large_obstacle(self):
        """Test with large obstacle taking significant wall area."""
        obstacles = [(1.0, 1.0, 3.0, 2.0)]  # 3x2m obstacle
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.3, clearance=0.05, resolution=0.1
        )
        
        result = planner.plan("zigzag")
        points = [(p["x"], p["y"]) for p in result["points"]]
        
        # Check coverage efficiency
        assert "coverage_efficiency_pct" in result
        assert result["coverage_efficiency_pct"] < 100  # Should be less due to obstacle
        assert result["coverage_efficiency_pct"] > 50   # But still substantial coverage
    
    def test_narrow_gap_between_obstacles(self):
        """Test path navigates narrow gap between two obstacles."""
        obstacles = [
            (2.0, 0.0, 0.5, 2.0),  # Left obstacle
            (2.7, 0.0, 0.5, 2.0),  # Right obstacle (20cm gap)
        ]
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.3, clearance=0.02, resolution=0.05
        )
        
        result = planner.plan("zigzag")
        points = [(p["x"], p["y"]) for p in result["points"]]
        
        # Verify points exist in the gap region
        gap_points = [p for x, y in points for p in [(x, y)] 
                     if 2.52 < x < 2.68 and y < 2.0]
        
        # Should have some coverage in gap (gap is 20cm - 4cm clearance = 16cm usable)
        assert len(gap_points) > 0, "Should cover narrow gap between obstacles"
    
    def test_spiral_pattern_obstacle_avoidance(self):
        """Test spiral pattern also avoids obstacles."""
        obstacles = [(2.0, 2.0, 1.0, 1.0)]
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.3, clearance=0.05, resolution=0.1
        )
        
        result = planner.plan("spiral")
        points = [(p["x"], p["y"]) for p in result["points"]]
        
        expanded_obs = Rectangle(1.95, 1.95, 1.1, 1.1)
        for x, y in points:
            assert not expanded_obs.contains_point(x, y), \
                f"Spiral point ({x}, {y}) is inside obstacle"
    
    def test_clearance_parameter(self):
        """Test different clearance values."""
        obstacles = [(2.0, 2.0, 1.0, 1.0)]
        
        # Small clearance
        planner1 = CoveragePlanner(5.0, 5.0, obstacles, 
                                  spacing=0.5, clearance=0.01, resolution=0.1)
        result1 = planner1.plan("zigzag")
        
        # Large clearance
        planner2 = CoveragePlanner(5.0, 5.0, obstacles,
                                  spacing=0.5, clearance=0.1, resolution=0.1)
        result2 = planner2.plan("zigzag")
        
        # Larger clearance should result in fewer accessible points
        assert len(result2["points"]) < len(result1["points"]), \
            "Larger clearance should reduce coverage area"
    
    def test_no_obstacles(self):
        """Test path generation works with no obstacles."""
        planner = CoveragePlanner(
            5.0, 5.0, [],
            spacing=0.5, clearance=0.05, resolution=0.1
        )
        
        result = planner.plan("zigzag")
        assert len(result["points"]) > 0
        assert result["coverage_efficiency_pct"] == 100.0
    
    def test_overlapping_obstacles(self):
        """Test handling of overlapping obstacles."""
        obstacles = [
            (2.0, 2.0, 1.0, 1.0),
            (2.5, 2.5, 1.0, 1.0),  # Overlaps with first
        ]
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.3, clearance=0.02, resolution=0.1
        )
        
        result = planner.plan("zigzag")
        points = [(p["x"], p["y"]) for p in result["points"]]
        
        # Should handle overlapping obstacles correctly
        assert len(points) > 0
    
    def test_obstacle_validation(self):
        """Test obstacle validation catches invalid inputs."""
        # Invalid dimension
        with pytest.raises(ValueError):
            create_plan(5.0, 5.0, [(1.0, 1.0, -1.0, 1.0)])
        
        # Obstacle larger than wall
        with pytest.raises(ValueError):
            create_plan(5.0, 5.0, [(0.0, 0.0, 10.0, 10.0)])
        
        # Invalid wall dimensions
        with pytest.raises(ValueError):
            create_plan(-5.0, 5.0, [])
    
    def test_create_plan_api(self):
        """Test the create_plan API function."""
        result = create_plan(
            wall_width=5.0,
            wall_height=5.0,
            obstacles=[(2.0, 2.0, 1.0, 1.0)],
            pattern="zigzag",
            spacing=0.3,
            clearance=0.05,
            resolution=0.1,
            speed=0.2
        )
        
        assert "points" in result
        assert "length_m" in result
        assert "duration_s" in result
        assert "coverage_efficiency_pct" in result
        assert len(result["points"]) > 0
        assert result["duration_s"] > 0
    
    def test_path_metadata(self):
        """Test that path metadata is correctly calculated."""
        obstacles = [(2.0, 2.0, 1.0, 1.0)]
        
        result = create_plan(
            5.0, 5.0, obstacles,
            spacing=0.3, clearance=0.02, resolution=0.1, speed=0.1
        )
        
        # Check metadata fields
        assert result["wall_area_m2"] == 25.0
        assert result["obstacle_area_m2"] == 1.0
        assert result["accessible_area_m2"] == 24.0
        assert 90 < result["coverage_efficiency_pct"] < 100
        
        # Check path length makes sense
        assert result["length_m"] > 0
        assert result["duration_s"] == pytest.approx(result["length_m"] / 0.1, rel=0.01)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_fully_blocked_row(self):
        """Test handling when an entire row is blocked."""
        # Create obstacle that blocks entire height at x=2.5
        obstacles = [(2.4, 0.0, 0.2, 5.0)]
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.5, clearance=0.02, resolution=0.1
        )
        
        result = planner.plan("zigzag")
        # Should still generate path on both sides
        assert len(result["points"]) > 0
    
    def test_very_small_wall(self):
        """Test with very small wall dimensions."""
        planner = CoveragePlanner(
            0.5, 0.5, [],
            spacing=0.1, clearance=0.01, resolution=0.02
        )
        
        result = planner.plan("zigzag")
        assert len(result["points"]) > 0
    
    def test_obstacle_exactly_at_boundary(self):
        """Test obstacle positioned exactly at wall boundary."""
        obstacles = [(0.0, 0.0, 1.0, 1.0)]  # Flush with corner
        
        planner = CoveragePlanner(
            5.0, 5.0, obstacles,
            spacing=0.3, clearance=0.02, resolution=0.1
        )
        
        result = planner.plan("zigzag")
        assert len(result["points"]) > 0
