# LevelUP Backend

API for LevelUP - service for effective education

## API Callbacks

```
# Register new user
curl -X POST "http://localhost:8000/register?login=test&password=123456"

# Login
curl -X POST "http://localhost:8000/login?login=test&password=123456"

# Verify session
curl -H "Authorization: Bearer SESSION_KEY" http://localhost:8000/verify

# Leaderboard
curl -H "Authorization: Bearer SESSION_KEY" "http://localhost:8000/leaderboard?filter=rank"
curl -H "Authorization: Bearer SESSION_KEY" "http://localhost:8000/leaderboard?filter=days"

# Logout
curl -X POST -H "Authorization: Bearer SESSION_KEY" http://localhost:8000/logout

# Update statistics
curl -X POST "http://localhost:8000/account/statistics" \
-H "Authorization: Bearer <session_key>" \
-H "api-key: $(echo -n 'your_api_secret_key' | base64)" \
-H "Content-Type: application/json" \
-d '{"achievements": ["new_achievement"], "courses": ["new_course"]}'

# Update account info
curl -X POST "http://localhost:8000/account/info" \
-H "Authorization: Bearer <session_key>" \
-H "api-key: $(echo -n 'your_api_secret_key' | base64)" \
-H "Content-Type: application/json" \
-d '{"points": 100, "level": 2}'

# Get account info
curl -X GET "http://localhost:8000/account/info" \
-H "Authorization: Bearer <session_key>" \
-H "api-key: $(echo -n 'your_api_secret_key' | base64)"

# Get flashcards database
curl -X GET "http://localhost:8000/flashcards/database" \
-H "Authorization: Bearer <session_key>"

# Get specific flashcard
curl -X GET "http://localhost:8000/flashcards/FLASHCARD_ID" \
-H "Authorization: Bearer <session_key>"
```
