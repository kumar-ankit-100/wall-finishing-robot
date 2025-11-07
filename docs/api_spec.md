# API Specification

Complete REST API documentation for the Wall Finishing Robot system.

**Base URL**: `http://localhost:8000`  
**API Version**: v1  
**Content-Type**: `application/json`

## Authentication

Currently no authentication required (add JWT/API keys for production).

## Common Headers

**Request**:
```
Content-Type: application/json
X-Request-ID: <optional-uuid>
```

**Response**:
```
Content-Type: application/json
X-Request-ID: <uuid>
```

## Error Responses

All errors follow this structure:

```json
{
  "detail": "Error description"
}
```

**Status Codes**:
- `400` Bad Request - Invalid input
- `404` Not Found - Resource not found
- `422` Unprocessable Entity - Validation error
- `500` Internal Server Error - Server error

---

## Endpoints

### Health & Metrics

#### GET /v1/health

Health check endpoint.

**Response** `200 OK`:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-07T10:30:00Z",
  "database": "connected"
}
```

#### GET /metrics

Application metrics.

**Response** `200 OK`:
```json
{
  "requests": {
    "total": 142,
    "errors": 3,
    "error_rate_percent": 2.11,
    "avg_response_time_ms": 45.2
  },
  "planner": {
    "runs": 25,
    "avg_time_ms": 85.3
  },
  "database": {
    "queries": 98,
    "avg_time_ms": 12.1
  },
  "entities": {
    "walls_created": 15,
    "trajectories_created": 25
  },
  "endpoints": {
    "POST /v1/walls": {
      "count": 15,
      "avg_time_ms": 42.5
    }
  }
}
```

---

### Walls

#### POST /v1/walls

Create a new wall with optional obstacles.

**Request Body**:
```json
{
  "width": 5.0,
  "height": 5.0,
  "obstacles": [
    {
      "x": 2.0,
      "y": 2.0,
      "width": 0.25,
      "height": 0.25
    }
  ]
}
```

**Validation Rules**:
- `width` > 0
- `height` > 0
- `obstacles[].x` >= 0
- `obstacles[].y` >= 0
- `obstacles[].width` > 0
- `obstacles[].height` > 0
- Obstacle must fit within wall: `x + width <= wall.width`, `y + height <= wall.height`

**Response** `201 Created`:
```json
{
  "id": 1,
  "width": 5.0,
  "height": 5.0,
  "created_at": "2025-11-07T10:30:00Z",
  "obstacles": [
    {
      "id": 1,
      "wall_id": 1,
      "x": 2.0,
      "y": 2.0,
      "width": 0.25,
      "height": 0.25
    }
  ]
}
```

**Errors**:
- `400` If obstacle extends beyond wall
- `422` If validation fails

#### GET /v1/walls/{wall_id}

Retrieve wall by ID.

**Path Parameters**:
- `wall_id` (integer) - Wall identifier

**Response** `200 OK`:
```json
{
  "id": 1,
  "width": 5.0,
  "height": 5.0,
  "created_at": "2025-11-07T10:30:00Z",
  "obstacles": [...]
}
```

**Errors**:
- `404` If wall not found

---

### Trajectories

#### POST /v1/trajectories/walls/{wall_id}/plan

Generate coverage plan for a wall.

**Path Parameters**:
- `wall_id` (integer) - Wall identifier

**Request Body**:
```json
{
  "settings": {
    "pattern": "zigzag",
    "spacing": 0.05,
    "speed": 0.1,
    "clearance": 0.02,
    "resolution": 0.01
  }
}
```

**Settings Schema**:
- `pattern` (enum): `"zigzag"` or `"spiral"` (default: `"zigzag"`)
- `spacing` (float): Pass spacing in meters, 0 < value <= 1.0 (default: `0.05`)
- `speed` (float): Robot speed in m/s, 0 < value <= 2.0 (default: `0.1`)
- `clearance` (float): Obstacle clearance in meters, 0 <= value <= 0.5 (default: `0.02`)
- `resolution` (float): Path point resolution, 0 < value <= 0.1 (default: `0.01`)

**Response** `201 Created`:
```json
{
  "id": 1,
  "wall_id": 1,
  "planner_settings": {
    "pattern": "zigzag",
    "spacing": 0.05,
    "speed": 0.1,
    "clearance": 0.02,
    "resolution": 0.01
  },
  "length_m": 530.42,
  "duration_s": 5304.2,
  "point_count": 50000,
  "created_at": "2025-11-07T10:31:00Z"
}
```

**Errors**:
- `404` If wall not found
- `400` If planning fails (e.g., no valid path)
- `400` If trajectory exceeds max points (10,000 default)

#### GET /v1/trajectories/{trajectory_id}

Retrieve full trajectory with all waypoints.

**Path Parameters**:
- `trajectory_id` (integer) - Trajectory identifier

**Query Parameters**:
- `include_wall` (boolean) - Include wall data (default: `false`)

**Response** `200 OK`:
```json
{
  "id": 1,
  "wall_id": 1,
  "planner_settings": {...},
  "length_m": 530.42,
  "duration_s": 5304.2,
  "point_count": 50000,
  "created_at": "2025-11-07T10:31:00Z",
  "points": [
    {"x": 0.025, "y": 0.025},
    {"x": 0.035, "y": 0.025},
    ...
  ],
  "wall": {  // If include_wall=true
    "id": 1,
    "width": 5.0,
    "height": 5.0,
    "obstacles": [...]
  }
}
```

**Errors**:
- `404` If trajectory not found

#### GET /v1/trajectories

List trajectories with pagination and filters.

**Query Parameters**:
- `wall_id` (integer, optional) - Filter by wall ID
- `pattern` (string, optional) - Filter by pattern ("zigzag"/"spiral")
- `page` (integer) - Page number, >= 1 (default: `1`)
- `page_size` (integer) - Items per page, 1-100 (default: `20`)

**Response** `200 OK`:
```json
{
  "items": [
    {
      "id": 3,
      "wall_id": 1,
      "planner_settings": {...},
      "length_m": 530.42,
      "duration_s": 5304.2,
      "point_count": 50000,
      "created_at": "2025-11-07T10:31:00Z"
    },
    ...
  ],
  "total": 25,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

#### DELETE /v1/trajectories/{trajectory_id}

Delete a trajectory.

**Path Parameters**:
- `trajectory_id` (integer) - Trajectory identifier

**Response** `204 No Content`

**Errors**:
- `404` If trajectory not found

---

## Sample Workflows

### Basic Workflow

1. **Create Wall**:
   ```bash
   curl -X POST http://localhost:8000/v1/walls \
     -H "Content-Type: application/json" \
     -d '{
       "width": 5.0,
       "height": 5.0,
       "obstacles": [
         {"x": 2.0, "y": 2.0, "width": 0.25, "height": 0.25}
       ]
     }'
   ```

2. **Generate Plan**:
   ```bash
   curl -X POST http://localhost:8000/v1/trajectories/walls/1/plan \
     -H "Content-Type: application/json" \
     -d '{
       "settings": {
         "pattern": "zigzag",
         "spacing": 0.05
       }
     }'
   ```

3. **Retrieve Trajectory**:
   ```bash
   curl http://localhost:8000/v1/trajectories/1?include_wall=true
   ```

4. **Download as JSON**:
   ```bash
   curl http://localhost:8000/v1/trajectories/1 > trajectory.json
   ```

### Advanced Workflow

1. **Create Multiple Walls**
2. **Generate Plans with Different Patterns**
3. **List and Compare Trajectories**:
   ```bash
   curl "http://localhost:8000/v1/trajectories?wall_id=1"
   ```

4. **Delete Old Trajectories**:
   ```bash
   curl -X DELETE http://localhost:8000/v1/trajectories/1
   ```

---

## Rate Limiting

**Default Limits**:
- 100 requests per 60 seconds per IP

**Headers**:
- `X-RateLimit-Limit`: Max requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

**Response** `429 Too Many Requests`:
```json
{
  "detail": "Rate limit exceeded. Try again in 42 seconds."
}
```

---

## Versioning

API version is included in the path: `/v1/...`

Future versions will be `/v2/...` with backwards compatibility where possible.

---

## WebSocket Support (Future)

Planned for real-time trajectory updates:

```
ws://localhost:8000/v1/trajectories/{id}/stream
```

---

## OpenAPI/Swagger

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
