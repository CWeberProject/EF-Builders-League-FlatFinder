# Scraper Improvement Plan

## Mouse Movement Enhancement

### Current Issues
- Mouse movements can go out of bounds
- Absolute coordinate system leading to positioning errors
- Lack of viewport boundary awareness
- Too large/rapid movements

### Improvements

1. **Viewport-Aware Movement System**
```python
def get_viewport_boundaries(self):
    return {
        'width': self.driver.execute_script('return window.innerWidth;'),
        'height': self.driver.execute_script('return window.innerHeight;'),
        'scroll_x': self.driver.execute_script('return window.pageXOffset;'),
        'scroll_y': self.driver.execute_script('return window.pageYOffset;')
    }
```

2. **Bezier Curve Movement Path**
```python
def calculate_bezier_points(p0, p1, p2, steps=20):
    """
    Generate points along a quadratic Bezier curve for smooth mouse movement
    p0: start point
    p1: control point
    p2: end point
    """
    points = []
    for t in range(steps + 1):
        t = t / steps
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        points.append((x, y))
    return points
```

3. **Safe Movement Implementation**
```python
def safe_mouse_movement(self, element):
    viewport = self.get_viewport_boundaries()
    element_loc = element.location
    
    # Ensure target is within viewport
    target_x = min(max(element_loc['x'], 0), viewport['width'])
    target_y = min(max(element_loc['y'], 0), viewport['height'])
    
    # Generate smooth path
    start = self.get_current_mouse_position()
    control = self.calculate_control_point(start, (target_x, target_y))
    path = self.calculate_bezier_points(start, control, (target_x, target_y))
    
    # Execute movement
    for point in path:
        if self.is_point_safe(point, viewport):
            self.move_to_relative(point)
            time.sleep(random.uniform(0.01, 0.03))
```

### Implementation Steps

1. Add viewport boundary detection and safe zone calculation
2. Implement Bezier curve generation for smooth paths
3. Create relative movement system using small increments
4. Add safety checks and fallback mechanisms
5. Implement gradual acceleration/deceleration
6. Add error recovery for failed movements

### Safety Mechanisms

- Keep 10% margin from viewport edges
- Maximum step size of 20 pixels per movement
- Acceleration capped at 2 pixels per frame
- Automatic path recalculation if target moves
- Fallback to direct movement if smooth path fails

### Testing Strategy

1. Test with various viewport sizes
2. Verify boundary detection
3. Measure movement smoothness
4. Validate error recovery
5. Performance impact assessment

## Next Steps

1. Implement viewport boundary detection
2. Add Bezier curve movement system
3. Integrate safety checks
4. Add error recovery mechanisms
5. Test and validate improvements