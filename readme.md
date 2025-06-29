# TrueShorts Backend API

## What is TrueShorts?

TrueShorts is an intelligent news aggregation and verification platform that combines AI-powered fact-checking with personalized news delivery. It helps users discover relevant news while automatically verifying the authenticity of claims using multiple sources and AI analysis.

### Key Features:
- **AI-Powered News Verification**: Automatically fact-checks news articles using web search, Wikipedia, and AI analysis
- **Personalized News Feed**: Delivers news tailored to user preferences using machine learning
- **Interactive AI News Agent**: Allows users to ask questions about news articles and get detailed analysis
- **Multi-Source Aggregation**: Collects news from multiple reliable sources (BBC, Reuters, Al Jazeera, etc.)
- **Real-time Fact Checking**: Continuously verifies news claims in the background

## 🚀 How to Use the API

### Option 1: Use the Deployed API (Production)

The backend is deployed and available at:

```
http://trueshorts-api.duejcqajdff7c5h2.centralindia.azurecontainer.io:8000
```

- **API Docs:** http://trueshorts-api.duejcqajdff7c5h2.centralindia.azurecontainer.io:8000/docs
- Use this URL in your frontend or API testing tools (e.g., Postman, Swagger UI).
- All endpoints described below are available at this base URL.

### Option 2: Run Locally with Docker Compose

You can run the backend locally for development or testing using Docker Compose:

```bash
# 1. Clone the repository
# 2. Create a .env file with your secrets (see below)
# 3. Start all services

docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Example docker-compose.yml
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

  backend:
    image: shubhthecoder/trueshorts_backend:latest
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped

volumes:
  mongodb_data:
```

## 📚 API Documentation

- **Production Docs:** http://trueshorts-api.duejcqajdff7c5h2.centralindia.azurecontainer.io:8000/docs
- **Local Docs:** http://localhost:8000/docs (if running locally)

## 🔗 API Endpoints & Usage Guide

All endpoints are available at the base URL (production or local). For example:
- Production: `http://trueshorts-api.duejcqajdff7c5h2.centralindia.azurecontainer.io:8000/news`
- Local: `http://localhost:8000/news`

### Authentication
- `POST /auth/signup` — Register a new user
- `POST /auth/login` — Login and get JWT token

### News
- `GET /news` — Get personalized news (requires JWT)
- `POST /read/{article_id}` — Track reading
- `POST /fetch-latest-news` — Fetch latest news
- `POST /news/save/{article_id}` — Save article
- `GET /news/saved` — Get saved articles
- `GET /news/search?query=...` — Search news

### AI News Agent
- `POST /get_more_about_news` — Start AI chat about an article
- `POST /get_more_follow_up` — Ask follow-up questions

### Fake News Detection
- `POST /fake_news/claim-verdict` — Verify a claim

## 📝 Environment Variables

For local development, create a `.env` file:

```env
GNEWS_API_KEY=f30e4c031aa2ea070ba8b4fca5109aa3
SECRET_KEY=1a2b3c4d5e6f7g8h9i0jkLMNOPQrstuvWXyz9876543210
MONGO_URI=mongodb+srv://shubham07kumargupta:Shubham@2006@trueshorts-cluster.vzk8awq.mongodb.net/?retryWrites=true&w=majority&appName=trueshorts-cluster
SERPER_API_KEY=0f8f7d962eeb0953e4190e2311e140c5a6c02d50
GOOGLE_FACT_CHECK_API_KEY=AIzaSyDLMGxKA8LhHeejl52owJ6kLEYYWEnnnbw
GROQ_API_KEY=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
```

## 🧑‍💻 Example: Using the API from Frontend

```javascript
const API_BASE = 'http://trueshorts-api.duejcqajdff7c5h2.centralindia.azurecontainer.io:8000'; // or 'http://localhost:8000' for local

// Register
fetch(`${API_BASE}/auth/signup`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
  .then(res => res.json())
  .then(console.log);

// Login
fetch(`${API_BASE}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
  .then(res => res.json())
  .then(data => localStorage.setItem('token', data.access_token));

// Get news (after login)
fetch(`${API_BASE}/news`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
  .then(res => res.json())
  .then(console.log);
```

## 🗄️ Accessing the Database (MongoDB)

- **Production:**
  - MongoDB is not exposed publicly for security. Use Azure Portal or a secure admin tunnel if needed.
- **Local:**
  - Use MongoDB Compass or mongosh:
    - Connection string: `mongodb://admin:password@localhost:27017`
    - Default DB: `news`

## 🛡️ Auto-Shutdown Feature (Production)
- Every API request updates a `last_active` timestamp in MongoDB.
- A scheduled GitHub Action checks this timestamp every 15 minutes.
- If the backend is idle for >1.5 hours, the Azure container is automatically stopped to save costs.

## 🛠️ CI/CD Pipeline (GitHub Actions)

Deployment is automated using GitHub Actions:
- On every push to `main`, the workflow `.github/workflows/docker-render-deploy.yml` will:
  1. Build and push the Docker image to Docker Hub (`shubhthecoder/trueshorts_backend:latest`).
  2. Log in to Azure using the service principal credentials in `AZURE_CREDENTIALS`.
  3. Restart the Azure Container Instance (`trueshorts-backend` in resource group `trueshorts-backend`).
- This ensures your latest code is always deployed to the public API URL above.

## 📞 Support
If you encounter issues:
- Check the [API docs](http://trueshorts-api.duejcqajdff7c5h2.centralindia.azurecontainer.io:8000/docs)
- Check logs in Azure Portal
- For local: `docker-compose logs`
- For deployment: see GitHub Actions logs

##  Quick Start (DockerHub Image)

### Prerequisites
- Docker Desktop installed
- Docker Hub account access (credentials provided below)

### Step 1: Login to Docker Hub

Since the Docker image is in a private repository, you need to login first:

```bash
# Login to Docker Hub with provided credentials
docker login

# Username: shubhthecoder
# Password: dckr_pat_upjYN6pxGqfoFjZxb7PbQESW-FM
```

### Step 2: Setup Project

```bash
# Create a new directory for your project
mkdir trueshorts-test
cd trueshorts-test

# Create docker-compose.yml file (copy the content below)
# Then run:
docker-compose up -d
```

## Required Files

### 1. Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

  trueshorts:
    image: shubhthecoder/trueshorts_backend:latest
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
      - GNEWS_API_KEY=f30e4c031aa2ea070ba8b4fca5109aa3
      - SECRET_KEY=1a2b3c4d5e6f7g8h9i0jkLMNOPQrstuvWXyz9876543210
      - MONGO_URI=mongodb://admin:password@mongodb:27017
      - SERPER_API_KEY=0f8f7d962eeb0953e4190e2311e140c5a6c02d50
      - GOOGLE_FACT_CHECK_API_KEY=AIzaSyDLMGxKA8LhHeejl52owJ6kLEYYWEnnnbw
      - GROQ_API_KEY=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

volumes:
  mongodb_data:
```

### 2. Create `.env` file (optional, for custom configuration)

```env
# Optional: Override default API keys
GNEWS_API_KEY=your_gnews_api_key
SECRET_KEY=your_secret_key
MONGO_URI=mongodb://admin:password@mongodb:27017
SERPER_API_KEY=your_serper_api_key
GOOGLE_FACT_CHECK_API_KEY=your_google_fact_check_key
GROQ_API_KEY=your_groq_api_key
```

## Start the API

```bash
# First, login to Docker Hub (if not already logged in)
docker login
# Username: shubhthecoder
# Password: dckr_pat_upjYN6pxGqfoFjZxb7PbQESW-FM

# Pull the private image
docker pull shubhthecoder/trueshorts_backend:latest

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

##  API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints & Usage Guide

### Authentication Endpoints

#### `POST /auth/signup`
**Purpose**: Register a new user account to access personalized news features.

**When to use**: 
- First-time user registration
- Creating user profiles for personalized news delivery
- Enabling user-specific features like saved articles and reading history

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response**:
```json
{
  "msg": "Account created"
}
```

**Frontend Integration Example**:
```javascript
const registerUser = async (email, password) => {
  const response = await fetch('http://localhost:8000/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return response.json();
};
```

#### `POST /auth/login`
**Purpose**: Authenticate existing users and get access token for API calls.

**When to use**:
- User login after registration
- Session management
- Getting authentication token for protected endpoints

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Frontend Integration Example**:
```javascript
const loginUser = async (email, password) => {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data;
};
```

### News Management Endpoints

#### `GET /news`
**Purpose**: Get personalized news articles for the authenticated user.

**When to use**:
- Display news feed on homepage
- Show personalized news recommendations
- Get verified news articles with fact-checking results

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "article_id": "507f1f77bcf86cd799439011",
  "title": "Breaking News Headline",
  "content": "Full article content...",
  "category": "politics",
  "published": "2024-01-15T10:30:00Z",
  "source": "BBC",
  "url": "https://example.com/article",
  "user_id": "user123",
  "seen": false,
  "verified": true,
  "verdict": "REAL",
  "explanation": "This claim has been verified by multiple reliable sources."
}
```

**Frontend Integration Example**:
```javascript
const getNews = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:8000/news', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

#### `POST /read/{article_id}`
**Purpose**: Track user reading behavior for better personalization.

**When to use**:
- When user opens an article
- To improve news recommendations
- Track user engagement metrics

**Request Body**:
```json
{
  "duration": 120
}
```

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "msg": "Reading tracked"
}
```

#### `POST /fetch-latest-news`
**Purpose**: Manually trigger news aggregation and fetch latest articles.

**When to use**:
- Refresh news feed
- Get latest breaking news
- Force update of news recommendations

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "status": "success",
  "new_articles": 15
}
```

### Article Management Endpoints

#### `POST /news/save/{article_id}`
**Purpose**: Save articles for later reading.

**When to use**:
- Bookmark interesting articles
- Create reading list
- Save articles for offline reading

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "msg": "Article saved"
}
```

#### `GET /news/saved`
**Purpose**: Get all saved articles for the user.

**When to use**:
- Display saved articles page
- Show user's reading list
- Access bookmarked content

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
[
  {
    "article_id": "507f1f77bcf86cd799439011",
    "title": "Saved Article Title",
    "content": "Article content...",
    "category": "technology",
    "published": "2024-01-15T10:30:00Z",
    "source": "TechCrunch",
    "url": "https://example.com/article",
    "saved_at": "2024-01-15T11:00:00Z"
  }
]
```

###  Search Endpoints

#### `GET /news/search?query={search_term}`
**Purpose**: Search through all available news articles.

**When to use**:
- Implement search functionality
- Find specific topics or keywords
- Filter news by content

**Parameters**:
- `query` (required): Search keywords or description

**Response**:
```json
[
  {
    "headline": "Search Result Title",
    "content": "Article content matching search...",
    "timestamp": "2024-01-15T10:30:00Z",
    "source": "Reuters",
    "category": "business",
    "url": "https://example.com/article"
  }
]
```

**Frontend Integration Example**:
```javascript
const searchNews = async (query) => {
  const response = await fetch(`http://localhost:8000/news/search?query=${encodeURIComponent(query)}`);
  return response.json();
};
```

### 🤖 AI News Agent Endpoints

#### `POST /get_more_about_news`
**Purpose**: Start an AI-powered conversation about a specific news article.

**When to use**:
- Provide detailed analysis of news articles
- Answer user questions about news context
- Generate timelines and impact analysis

**Request Body**:
```json
{
  "article_id": "507f1f77bcf86cd799439011"
}
```

**Response**:
```json
{
  "session_id": "session_12345",
  "timeline": "Detailed timeline of events...",
  "analysis": "Comprehensive analysis of the news impact..."
}
```

**Frontend Integration Example**:
```javascript
const startAIChat = async (articleId) => {
  const response = await fetch('http://localhost:8000/get_more_about_news', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ article_id: articleId })
  });
  return response.json();
};
```

#### `POST /get_more_follow_up`
**Purpose**: Ask follow-up questions in an existing AI conversation session.

**When to use**:
- Continue AI conversations about news
- Ask specific questions about articles
- Get detailed explanations and context

**Request Body**:
```json
{
  "session_id": "session_12345",
  "question": "How does this affect the economy?"
}
```

**Response**:
```json
{
  "session_id": "session_12345",
  "answer": "Detailed answer about economic impact..."
}
```

**Frontend Integration Example**:
```javascript
const askFollowUp = async (sessionId, question) => {
  const response = await fetch('http://localhost:8000/get_more_follow_up', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question })
  });
  return response.json();
};
```

### 🔍 Fake News Detection Endpoints

#### `POST /fake_news/claim-verdict`
**Purpose**: Verify if a specific claim or statement is fake news using AI and multiple sources.

**When to use**:
- Fact-check user-submitted claims
- Verify news headlines
- Provide credibility scores for information

**Request Body**:
```json
{
  "claim": "The Earth is flat"
}
```

**Response**:
```json
{
  "verdict": "FAKE",
  "explanation": "This claim has been debunked by scientific evidence. Multiple reliable sources confirm the Earth is spherical."
}
```

**Frontend Integration Example**:
```javascript
const verifyClaim = async (claim) => {
  const response = await fetch('http://localhost:8000/fake_news/claim-verdict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ claim })
  });
  return response.json();
};
```

## Testing the API

### 1. Using Interactive Docs (Easiest)
1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in the required parameters
4. Click "Execute"

### 2. Using curl
```bash
# Test if API is running
curl http://localhost:8000/news/

# Test fake news verification
curl -X POST http://localhost:8000/fake_news/claim-verdict \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Earth is flat"}'

# Test news agent
curl -X POST http://localhost:8000/get_more_about_news \
  -H "Content-Type: application/json" \
  -d '{"article_id": "your_article_id"}'
```

### 3. Complete Frontend Integration Example
```javascript
class TrueShortsAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('token');
  }

  // Authentication
  async signup(email, password) {
    const response = await fetch(`${this.baseURL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return response.json();
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    this.token = data.access_token;
    localStorage.setItem('token', data.access_token);
    return data;
  }

  // News
  async getNews() {
    const response = await fetch(`${this.baseURL}/news`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  async saveArticle(articleId) {
    const response = await fetch(`${this.baseURL}/news/save/${articleId}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  async getSavedArticles() {
    const response = await fetch(`${this.baseURL}/news/saved`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  // Search
  async searchNews(query) {
    const response = await fetch(`${this.baseURL}/news/search?query=${encodeURIComponent(query)}`);
    return response.json();
  }

  // AI Agent
  async startAIChat(articleId) {
    const response = await fetch(`${this.baseURL}/get_more_about_news`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ article_id: articleId })
    });
    return response.json();
  }

  async askFollowUp(sessionId, question) {
    const response = await fetch(`${this.baseURL}/get_more_follow_up`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, question })
    });
    return response.json();
  }

  // Fake News Detection
  async verifyClaim(claim) {
    const response = await fetch(`${this.baseURL}/fake_news/claim-verdict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ claim })
    });
    return response.json();
  }
}

// Usage
const api = new TrueShortsAPI();

// Example workflow
async function exampleWorkflow() {
  // 1. Register/Login
  await api.signup('user@example.com', 'password123');
  await api.login('user@example.com', 'password123');

  // 2. Get personalized news
  const news = await api.getNews();
  console.log('Latest news:', news);

  // 3. Verify a claim
  const verification = await api.verifyClaim('Some claim here');
  console.log('Verification result:', verification);

  // 4. Start AI chat about an article
  const aiSession = await api.startAIChat(news.article_id);
  console.log('AI analysis:', aiSession);

  // 5. Ask follow-up question
  const followUp = await api.askFollowUp(aiSession.session_id, 'How does this affect the economy?');
  console.log('Follow-up answer:', followUp);
}
```

##️ Database Access

### MongoDB Connection Details
- **Host**: localhost
- **Port**: 27017
- **Username**: admin
- **Password**: password
- **Database**: news (default)

### View Database Data
```bash
# Connect to MongoDB container
docker exec -it trueshorts-test-mongodb-1 mongosh -u admin -p password

# List databases
show dbs

# Use news database
use news

# List collections
show collections

# View articles
db.articles.find().pretty()

# View users
db.users.find().pretty()

# View news sessions
db.news_sessions.find().pretty()
```

### MongoDB Management Tools
- **MongoDB Compass**: Connect to `mongodb://admin:password@localhost:27017`
- **Studio 3T**: Same connection string
- **MongoDB Atlas**: Export data if needed

##  Development Commands

```bash
# Start services
docker-compose up -d

# Start with logs
docker-compose up

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f trueshorts
docker-compose logs -f mongodb

# Stop services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up --build -d

# Check service status
docker-compose ps
```

## 🔧 Troubleshooting

### Port 8000 already in use
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Use a different port
docker-compose up -d -p 8001:8000
# Then access at http://localhost:8001
```

### MongoDB connection issues
```bash
# Check if MongoDB is running
docker-compose ps

# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb

# Reset MongoDB (clears all data)
docker-compose down -v
docker-compose up -d
```

### API not responding
```bash
# Check if containers are running
docker-compose ps

# View app logs
docker-compose logs trueshorts

# Restart the app
docker-compose restart trueshorts

# Check container health
docker ps
```

### Docker image pull issues
```bash
# Login to Docker Hub (if needed)
docker login

# Pull image manually
docker pull shubhthecoder/trueshorts_backend:latest

# Check available images
docker images
```

## Monitoring and Logs

### View Real-time Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f trueshorts
docker-compose logs -f mongodb
```

### Check Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Health Checks
```bash
# Check if API is responding
curl http://localhost:8000/docs

# Check MongoDB connection
docker exec -it trueshorts-test-mongodb-1 mongosh -u admin -p password --eval "db.runCommand('ping')"
```

## Environment Variables Reference

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `GNEWS_API_KEY` | f30e4c031aa2ea070ba8b4fca5109aa3 | GNews API key for news aggregation |
| `SECRET_KEY` | 1a2b3c4d5e6f7g8h9i0jkLMNOPQrstuvWXyz9876543210 | JWT secret key for authentication |
| `MONGO_URI` | mongodb://admin:password@mongodb:27017 | MongoDB connection string |
| `SERPER_API_KEY` | 0f8f7d962eeb0953e4190e2311e140c5a6c02d50 | Serper API key for web search |
| `GOOGLE_FACT_CHECK_API_KEY` | AIzaSyDLMGxKA8LhHeejl52owJ6kLEYYWEnnnbw | Google Fact Check API key |
| `GROQ_API_KEY` | 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 | Groq LLM API key for AI features |

## Ready to Test!

1. **Create the files** above
2. **Run**: `docker-compose up -d`
3. **Visit**: http://localhost:8000/docs
4. **Start testing** the API endpoints

**No backend knowledge required!** Everything is pre-configured and ready to use.

##  Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Restart: `docker-compose restart`
3. Rebuild: `docker-compose up --build -d`
4. Reset: `docker-compose down -v && docker-compose up -d`

---

**Docker Image**: `shubhthecoder/trueshorts_backend:latest`  
**Docker Hub**: https://hub.docker.com/r/shubhthecoder/trueshorts_backend