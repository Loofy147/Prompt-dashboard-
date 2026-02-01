# Prompt Dashboard Manager

A production-grade web application for systematically creating, analyzing, and optimizing AI prompts using quantitative quality metrics (PES Framework).

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Overview

Transform ad-hoc prompt engineering into a systematic, measurable process. Track quality across six dimensions (Persona, Tone, Format, Specificity, Constraints, Context) and compute composite Q scores for data-driven optimization.

### Key Features

- **📝 Prompt Library** - Organize prompts with full-text search, tagging, and filtering
- **🧮 Quality Calculator** - Real-time Q score computation with dimensional breakdown
- **🔬 A/B/C Testing** - Generate and compare prompt variants (Concise/Neutral/Commanding)
- **📊 Analytics Dashboard** - Visualize quality trends, distributions, and performance
- **💾 Version Control** - Track prompt history with diff visualization
- **📤 Export/Import** - Share prompts in JSON, Markdown, or CSV formats

### Quality Framework (PES)

```
Q = 0.18×P + 0.22×T + 0.20×F + 0.18×S + 0.12×C + 0.10×R

Where:
  P = Persona clarity (explicit role specification)
  T = Tone appropriateness (domain-appropriate voice)
  F = Format precision (structured output specification)
  S = Specificity (quantified constraints and details)
  C = Constraint enforcement (validation mechanisms)
  R = Context richness (background information)
```

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/prompt-dashboard.git
cd prompt-dashboard

# 2. Start services
docker-compose up -d

# 3. Seed database with example prompts
docker-compose exec backend python seed_data.py

# 4. Open application
# Visit http://localhost:3000
# Login: demo / demo123
```

That's it! The dashboard is now running with 5 example prompts spanning different quality levels.

## 📁 Project Structure

```
prompt-dashboard/
├── api/                    # Flask/FastAPI backend
│   ├── app.py                 # Main application entry point
│   ├── quality_calculator.py  # Core Q score computation
│   ├── feature_analyzer.py    # NLP-based feature extraction
│   ├── seed_data.py          # Database seeding script
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── PromptEditor.tsx
│   │   │   ├── QualityCalculator.tsx
│   │   │   ├── PromptCard.tsx
│   │   │   ├── VariantComparison.tsx
│   │   │   └── ...
│   │   ├── views/             # Main views
│   │   │   ├── LibraryView.tsx
│   │   │   ├── EditorView.tsx
│   │   │   ├── AnalyzerView.tsx
│   │   │   └── ReportsView.tsx
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docs/                       # Documentation
│   ├── architecture.mmd       # System architecture diagram
│   ├── openapi.yaml          # API specification
│   ├── database_schema.dbml   # Database ERD
│   └── wireframes.txt         # UI wireframes
├── tests/                      # Test suite
│   ├── test_quality.py        # Unit tests for quality calculator
│   └── test_api.py            # API integration tests
├── docker-compose.yml          # Container orchestration
└── README.md
```

## 🏗️ Architecture

### System Components

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
┌──────▼─────────────────────────┐
│  React Frontend (Port 3000)    │
│  - Library/Editor/Analyzer/    │
│    Reports views               │
│  - Real-time Q calculation     │
│  - State management (Redux)    │
└──────┬─────────────────────────┘
       │ REST API
┌──────▼─────────────────────────┐
│  Flask Backend (Port 5000)     │
│  - JWT Authentication          │
│  - CRUD Controllers            │
│  - Quality Analysis Engine     │
└──────┬─────────────────────────┘
       │
┌──────▼─────────────────────────┐
│  SQLite Database               │
│  - Prompts, Variants, Tags     │
│  - Version History, Analytics  │
└────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.11
- Flask/FastAPI
- SQLite (production: PostgreSQL)
- spaCy (NLP analysis)
- JWT authentication

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS
- React Query (API caching)
- Recharts (visualization)
- Redux Toolkit (state management)

## 📚 API Reference

### Base URL
```
http://localhost:5000/api
```

### Authentication
All endpoints require JWT bearer token:
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

### Core Endpoints

#### Create Prompt
```bash
POST /api/prompts
Content-Type: application/json

{
  "text": "Your prompt text here",
  "tags": ["technical", "spec"]
}

# Response: 201 Created
{
  "id": 42,
  "text": "...",
  "Q_score": 0.88,
  "features": {
    "P": 0.92, "T": 0.88, "F": 0.95,
    "S": 0.90, "C": 0.85, "R": 0.70
  },
  "created_at": "2025-02-01T12:00:00Z"
}
```

#### List Prompts
```bash
GET /api/prompts?Q_min=0.80&tags=technical&page=1&per_page=20

# Response: 200 OK
{
  "prompts": [...],
  "total": 156,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

#### Analyze Quality
```bash
POST /api/prompts/42/analyze

# Response: 200 OK
{
  "features": {"P": 0.92, "T": 0.88, ...},
  "Q_score": 0.8766,
  "breakdown": {
    "wP_P": 0.1656,
    "wT_T": 0.1936,
    ...
  }
}
```

#### Generate Variants
```bash
POST /api/prompts/42/variants
Content-Type: application/json

{
  "variant_types": ["concise", "neutral", "commanding"]
}

# Response: 201 Created
{
  "variants": [
    {"type": "concise", "text": "...", "Q_score": 0.76},
    {"type": "neutral", "text": "...", "Q_score": 0.84},
    {"type": "commanding", "text": "...", "Q_score": 0.92}
  ],
  "comparison": {...}
}
```

#### Get Analytics
```bash
GET /api/analytics?metric=distribution&days=30

# Response: 200 OK
{
  "distribution": {...},
  "avg_scores": {"P": 0.85, "T": 0.82, ...},
  "top_performers": [...],
  "tag_cloud": [...]
}
```

See `docs/openapi.yaml` for complete API specification with all 9 endpoints.

## 🧪 Testing

### Run Unit Tests
```bash
# Backend tests
docker-compose exec backend pytest tests/ -v

# With coverage
docker-compose exec backend pytest tests/ --cov=. --cov-report=html

# Frontend tests
docker-compose exec frontend npm test
```

### Test Coverage Goals
- Backend: >90% coverage
- API endpoints: All 9 endpoints tested
- Quality calculator: Edge cases, precision, performance

### Performance Benchmarks
```bash
# Run quality calculator benchmark
docker-compose exec backend python -c "
from quality_calculator import benchmark_performance
avg_time = benchmark_performance(1000)
print(f'Average: {avg_time:.4f}ms')
print('Target: <1ms - PASS' if avg_time < 1 else 'FAIL')
"
```

Expected: <1ms per Q calculation

## 🔧 Development

### Local Development Setup

```bash
# Backend (without Docker)
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Frontend (without Docker)
cd frontend
npm install
npm start
```

### Database Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback
docker-compose exec backend alembic downgrade -1
```

### Environment Variables

Create `.env` file:
```env
# Backend
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-change-in-production
DATABASE_URL=sqlite:///data/prompts.db
FLASK_ENV=development

# Frontend
REACT_APP_API_URL=http://localhost:5000/api
```

## 📊 Sample Data

The seed script creates 5 diverse prompts:

1. **Technical Spec** (Q=0.93) - High F/S, comprehensive requirements
2. **Casual Marketing** (Q=0.42) - Low across all dimensions (demonstration)
3. **Research Synthesis** (Q=0.87) - High R/C, academic rigor
4. **Marketing Copy** (Q=0.89) - High T/P, audience-focused
5. **Product Brief** (Q=0.70) - Moderate quality, improvement opportunities

Each demonstrates different strengths and weaknesses in the PES framework.

## 🚢 Deployment

### Vercel Deployment (Recommended)

This project is configured for seamless deployment on [Vercel](https://vercel.com).

1.  **Connect your Repository** to Vercel.
2.  **Configure Environment Variables**:
    *   `DATABASE_URL`: Your Neon Postgres connection string.
3.  **Deploy**: Vercel will automatically detect the `vercel.json` and build both the Python API and the React frontend.

### Docker Hub (Establishment)

The project is established on Docker Hub under the `django213` namespace.

```bash
docker login -u django213
docker build -t django213/prompt-dashboard-backend ./api
docker build -t django213/prompt-dashboard-frontend ./frontend
docker push django213/prompt-dashboard-backend
docker push django213/prompt-dashboard-frontend
```

### Production Deployment (Docker Compose)

# Enable HTTPS with Let's Encrypt
docker-compose exec nginx certbot --nginx -d yourdomain.com
```

### Production Checklist

- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS (nginx + Let's Encrypt)
- [ ] Set up backup strategy for database
- [ ] Configure rate limiting (100 req/min per IP)
- [ ] Enable monitoring (Prometheus + Grafana)
- [ ] Set up error tracking (Sentry)
- [ ] Configure CORS for production domain
- [ ] Run security audit (`npm audit`, `safety check`)

## 🐛 Troubleshooting

### Common Issues

**Database locked error:**
```bash
# SQLite doesn't support high concurrency well
# Solution: Migrate to PostgreSQL for production
docker-compose down
docker-compose up -d
```

**Port already in use:**
```bash
# Change ports in docker-compose.yml
# Backend: ports: ["5001:5000"]
# Frontend: ports: ["3001:3000"]
```

**Tests failing:**
```bash
# Ensure test database is clean
docker-compose exec backend python -c "
import os;
os.remove('data/test.db') if os.path.exists('data/test.db') else None
"
docker-compose exec backend pytest tests/
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📖 Documentation

- **Architecture Diagram**: `docs/architecture.mmd` (Mermaid format)
- **API Specification**: `docs/openapi.yaml` (OpenAPI 3.0)
- **Database Schema**: `docs/database_schema.dbml` (ERD)
- **UI Wireframes**: `docs/wireframes.txt` (ASCII art)
- **Quality Calculator**: See `api/quality_calculator.py` docstrings

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style

- Python: Follow PEP 8, use type hints
- TypeScript/React: ESLint + Prettier
- Commit messages: Conventional Commits format

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- PES Quality Framework based on prompt engineering best practices
- UI components inspired by modern SaaS dashboards
- Testing methodology from pytest and React Testing Library

## 📞 Support

- **Issues**: GitHub Issues
- **Email**: support@promptdashboard.dev
- **Docs**: https://docs.promptdashboard.dev

---

Built with ❤️ for prompt engineers everywhere. Happy optimizing! 🚀
