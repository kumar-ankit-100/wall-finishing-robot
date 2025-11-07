# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Local Development (Recommended for Development)

**Backend**:
```bash
cd /home/ankit/Videos/10x/wall-finishing-robot/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ../scripts/create_db.py
python ../scripts/seed_sample.py  # Optional: adds sample data
uvicorn app.main:app --reload --port 8000
```

**Frontend** (new terminal):
```bash
cd /home/ankit/Videos/10x/wall-finishing-robot/frontend
npm install
npm run dev
```

**Access**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Docker (Recommended for Deployment)

```bash
cd /home/ankit/Videos/10x/wall-finishing-robot
docker-compose -f infra/docker-compose.yml up --build
```

**Access**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## 📁 Project Structure

```
wall-finishing-robot/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── core/     # Config, logging, metrics
│   │   ├── db/       # Database models
│   │   ├── models/   # Pydantic schemas
│   │   ├── services/ # Business logic (planner, storage)
│   │   └── tests/    # Test suite
│   └── requirements.txt
├── frontend/         # React application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── lib/         # API client, types
│   │   └── App.tsx
│   └── package.json
├── scripts/          # Utility scripts
│   ├── create_db.py
│   └── seed_sample.py
├── docs/            # Documentation
│   ├── design.md
│   ├── api_spec.md
│   └── how_to_record_walkthrough.md
├── infra/           # Docker & deployment
└── README.md
```

## 🧪 Running Tests

```bash
cd backend
pytest                              # Run all tests
pytest --cov=app --cov-report=html  # With coverage
pytest -v app/tests/test_planner.py # Specific test file
```

## 🎨 Code Formatting

**Backend**:
```bash
cd backend
black app/
isort app/
ruff check app/
```

**Frontend**:
```bash
cd frontend
npm run lint
npm run format
```

## 📝 Sample API Usage

### Create a Wall
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

### Generate Trajectory
```bash
curl -X POST http://localhost:8000/v1/trajectories/walls/1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "pattern": "zigzag",
      "spacing": 0.05,
      "speed": 0.1
    }
  }'
```

### Get Trajectory
```bash
curl http://localhost:8000/v1/trajectories/1?include_wall=true
```

## 🔍 Key Features to Demonstrate

1. **Wall Creation**: 5m × 5m with 0.25m × 0.25m obstacle
2. **Pattern Selection**: Toggle between zigzag and spiral
3. **Visualization**: Animated playback with speed controls
4. **Metrics**: View at http://localhost:8000/metrics
5. **Export**: Download trajectory snapshot as PNG

## 📹 Recording Video

See `docs/how_to_record_walkthrough.md` for detailed guide.

**Quick Timeline**:
- 0:00-0:30: Introduction & architecture
- 0:30-1:30: Create wall demonstration
- 1:30-2:30: Visualization & playback
- 2:30-3:00: API & testing
- 3:00-3:30: Conclusion

## ✅ Pre-Submission Checklist

- [ ] All tests passing (`pytest`)
- [ ] Code formatted (Black, Prettier)
- [ ] No secrets in code
- [ ] README complete
- [ ] Video recorded and uploaded
- [ ] GitHub collaborators added:
  - tanay@10xconstruction.ai
  - tushar@10xconstruction.ai
- [ ] SUBMISSION.md updated with video link

## 🐛 Troubleshooting

**Backend won't start**:
- Check Python version: `python --version` (need 3.11+)
- Activate venv: `source .venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**Frontend won't start**:
- Check Node version: `node --version` (need 18+)
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

**Database issues**:
- Delete and recreate: `rm wall_robot.db && python scripts/create_db.py`

**CORS errors**:
- Check backend is running on port 8000
- Check CORS_ORIGINS in backend/.env

## 📚 Documentation

- **README.md**: Complete project overview
- **docs/design.md**: Algorithm design & complexity
- **docs/api_spec.md**: API documentation
- **docs/how_to_record_walkthrough.md**: Video guide
- **SUBMISSION.md**: Submission details

## 🎯 Assignment Requirements Met

✅ Coverage planning (zigzag & spiral)  
✅ FastAPI + SQLite with indexing  
✅ Obstacle support with validation  
✅ CRUD APIs  
✅ Structured logging  
✅ 2D visualization (no Matplotlib)  
✅ Playback controls  
✅ Tests with 80%+ coverage  
✅ Complete documentation  
✅ Docker deployment  
✅ CI/CD pipeline  

## 🚀 Next Steps

1. Install dependencies
2. Run backend and frontend
3. Test the sample case (5m × 5m wall)
4. Review documentation
5. Record walkthrough video
6. Add GitHub collaborators
7. Submit!

Good luck! 🎉
