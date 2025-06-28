uvicorn app:app --reload --workers 4 

## News Agent Endpoints

### POST /news/get_more_about_news
- **Description:** Get a timeline and impact analysis for a news article using an agentic AI pipeline (Groq LLM + web/Wikipedia search). Returns a session_id for follow-ups.
- **Request Body:**
  ```json
  { "article_id": "string" }
  ```
- **Response:**
  ```json
  { "session_id": "string", "timeline": "string", "analysis": "string" }
  ```

### POST /news/get_more_follow_up
- **Description:** Ask follow-up questions about the same article/session. Uses session_id from previous call. Maintains context/memory for 10 minutes.
- **Request Body:**
  ```json
  { "session_id": "string", "question": "string" }
  ```
- **Response:**
  ```json
  { "session_id": "string", "answer": "string" }
  ```

### Session Management
- Sessions are stored in MongoDB with a 10-minute TTL (auto-expiry).
- Each session maintains context/history for contextual Q&A.

## Environment Variables
- Add to your `.env` or environment:
  - `GROQ_API_KEY` (required for agentic endpoints)
  - `MONGO_DB_NAME` (default: `news`) 