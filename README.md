<p align="center">
  <img src="https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Firebase-Auth%20%7C%20Firestore-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase" />
  <img src="https://img.shields.io/badge/Tailwind-3.x-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind" />
</p>

# 👔 Best-Fit

**Smart Wardrobe Manager with ML-Powered Color Analysis**

Best-Fit is a modern wardrobe management application that uses machine learning to extract dominant colors from your clothing items and suggest perfectly coordinated outfits based on color harmony theory.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Authentication** | Firebase Auth with email/password and Google OAuth |
| 📸 **Smart Uploads** | Drag-and-drop image uploads with automatic processing |
| 🎨 **ML Color Extraction** | K-means clustering identifies dominant colors in each garment |
| 👗 **Outfit Builder** | Create and save outfit combinations from your closet |
| ✨ **AI Suggestions** | Get outfit recommendations based on color harmony & style |
| 🌈 **Color Theory** | Complementary, analogous, triadic, and monochromatic schemes |
| ☁️ **Cloud Sync** | Data persists across devices with Firestore |

---

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for lightning-fast builds
- **Tailwind CSS** for modern, responsive UI
- **Firebase SDK** for auth & data
- **React Router v6** for navigation
- **Lucide React** for icons

### Backend
- **FastAPI** - High-performance Python API
- **ColorThief** - K-means color extraction
- **Pillow** - Image processing
- **Firebase Admin SDK** - Server-side auth verification

### Infrastructure
- **Firebase** - Authentication, Firestore, Storage
- **Vercel** - Frontend deployment (optional)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Firebase project ([Create one here](https://console.firebase.google.com))

### 1. Clone the Repository

```bash
git clone https://github.com/abdurislam/Best-Fit.git
cd Best-Fit
```

### 2. Firebase Configuration

1. Create a Firebase project and enable:
   - **Authentication** (Email/Password + Google)
   - **Firestore Database**
   - **Storage**

2. Get your web app config from Project Settings → General → Your apps

### 3. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cat > .env << EOF
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_API_URL=http://localhost:8000
EOF

# Start development server
npm run dev
```

### 5. Open the App

Navigate to `http://localhost:5173` in your browser.

---

## 📁 Project Structure

```
Best-Fit/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── auth.py                 # Firebase auth utilities
│   │   ├── models/                 # Pydantic models
│   │   ├── routers/                # API route handlers
│   │   └── services/               # Business logic
│   │       ├── color_service.py    # ML color extraction
│   │       └── outfit_service.py   # Outfit generation
│   ├── uploads/                    # User uploaded images
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable UI components
│   │   ├── contexts/               # React contexts (Auth)
│   │   ├── lib/                    # Firebase configuration
│   │   ├── pages/                  # Page components
│   │   ├── services/               # API client services
│   │   └── types/                  # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

## 🔌 API Reference

### Closet Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/closet/` | List all clothing items |
| `POST` | `/api/closet/` | Upload new item with image |
| `GET` | `/api/closet/{id}` | Get item details |
| `PUT` | `/api/closet/{id}` | Update item metadata |
| `DELETE` | `/api/closet/{id}` | Remove item |
| `POST` | `/api/closet/{id}/reanalyze` | Re-extract colors |

### Outfit Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/outfits/` | List saved outfits |
| `POST` | `/api/outfits/` | Create new outfit |
| `DELETE` | `/api/outfits/{id}` | Delete outfit |
| `POST` | `/api/outfits/suggest` | Get AI suggestions |

### Color Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/colors/extract` | Extract colors from image |
| `POST` | `/api/colors/harmony/score` | Calculate harmony score |

---

## 🎨 Color Harmony Theory

Best-Fit uses established color theory to suggest outfits:

| Scheme | Description | Best For |
|--------|-------------|----------|
| **Complementary** | Opposite colors on the wheel | Bold, high-contrast looks |
| **Analogous** | Adjacent colors | Harmonious, cohesive outfits |
| **Triadic** | Three evenly-spaced colors | Balanced, vibrant combinations |
| **Monochromatic** | Shades of one color | Elegant, sophisticated style |

---

## 🤖 Why K-Means Over LLMs?

We chose dedicated ML for color extraction over general-purpose LLMs:

| Factor | K-Means Clustering | Local LLM (Ollama) |
|--------|-------------------|-------------------|
| **Speed** | ~100ms/image | 2-5 seconds/image |
| **Precision** | Exact RGB values | Subjective descriptions |
| **Memory** | ~50MB | 4-16GB |
| **Reliability** | Deterministic | Variable outputs |

---

## 🚢 Deployment

### Frontend (Vercel)

```bash
cd frontend
npm run build
npx vercel --prod
```

Set these environment variables in Vercel dashboard:
- `VITE_FIREBASE_*` - All Firebase config values
- `VITE_API_URL` - Your backend URL

### Backend

Deploy to any Python hosting (Railway, Render, AWS, etc.):

```bash
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 🔒 Security

- All API endpoints require Firebase authentication
- User data is isolated by UID in Firestore
- Environment variables for sensitive configuration
- CORS configured for allowed origins only

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [ColorThief](https://github.com/fengsp/color-thief-py) for color extraction
- [Firebase](https://firebase.google.com) for backend services
- [Tailwind CSS](https://tailwindcss.com) for styling
- [Lucide](https://lucide.dev) for beautiful icons

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/abdurislam">Abdur Islam</a>
</p>
