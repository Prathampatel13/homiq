# HomiQ - Smart House Maintenance Ecosystem

**HomiQ** is an enterprise-grade smart home maintenance and on-demand technical service platform featuring architectural 3D interfaces, state-machine booking lifecycles, real-time WebSocket dispatch, cryptographic SmartVerify™ check-ins, and secure Razorpay payment processing.

---

## 🏛️ Project Directory Structure

```
homiq/
├── backend/                  # FastAPI Enterprise Backend
│   ├── alembic/              # Database migration definitions
│   ├── app/                  # Application core, api, models, services
│   │   ├── api/              # Versioned REST & WebSocket routers
│   │   ├── core/             # Configuration, caching, Redis & Celery setup
│   │   ├── crud/             # Database repository operations
│   │   ├── database/         # SQLAlchemy session & base models
│   │   ├── middleware/       # Security headers, CORS, request logging
│   │   ├── models/           # Declarative database entities
│   │   ├── schemas/          # Pydantic request/response validation schemas
│   │   ├── security/         # JWT tokens, rate limiting & session protection
│   │   ├── services/         # Encapsulated business logic & orchestrators
│   │   ├── tasks/            # Celery async background workers
│   │   └── utils/            # Shared helper utilities
│   ├── docs/                 # Architecture, Cloudinary & Disaster Recovery docs
│   ├── nginx/                # Reverse proxy & SSL production configurations
│   ├── scripts/              # Database backup, restore, deploy & diagnostics
│   └── tests/                # Smoke tests, integration test suites & reports
│
├── frontend/                 # React 18 + TypeScript + Vite Frontend
│   ├── public/               # Static assets & icons
│   └── src/
│       ├── api/              # Axios HTTP client endpoints & contracts
│       ├── components/       # Reusable UI component library
│       │   ├── 3d/           # Three.js 3D architectural house visualizer
│       │   ├── brand/        # HomiQ SVG logos & brand marks
│       │   ├── common/       # Navbar, Footer, Mobile Bottom Navigation
│       │   ├── modals/       # SmartVerify, Payment, Address & Review modals
│       │   └── ui/           # Status badges, empty states, loading indicators
│       ├── pages/            # Role-based dashboards & interactive service views
│       ├── services/         # Frontend business logic & helpers
│       ├── store/            # Zustand global state (Auth, Cart, UI)
│       └── types/            # TypeScript domain interfaces & enum definitions
│
├── scripts/                  # Project-wide maintenance & generator tools
│   └── generators/           # UI component & layout generators
│
└── .gitignore                # Multi-language Git ignore configuration
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup (FastAPI + PostgreSQL)

```bash
# Navigate to backend
cd homiq/backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Apply database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (React + Vite)

```bash
# Navigate to frontend
cd homiq/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

---

## 🔒 Key Enterprise Features

- **3-Tier Architecture**: Modular separation of API routing, Service business rules, and CRUD database repositories.
- **SmartVerify™**: Cryptographic QR and 6-digit OTP two-factor verification between technician and homeowner upon arrival.
- **Interactive 3D Home Viewer**: WebGL/Three.js interactive architectural model enabling intuitive room-by-room service selection.
- **Real-Time WebSockets**: Live tracking, dispatch updates, and multi-user room routing backed by Redis Pub/Sub.
- **Multi-Role Portals**: Tailored interfaces for Customers, Service Providers/Technicians, Fleet Companies, and Administrators.
