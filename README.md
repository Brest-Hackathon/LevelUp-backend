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

# Generate mood test
curl -H "Authorization: Bearer <session_key>" http://localhost:8000/mood/test

# Send mood test results
curl -X POST -H "Authorization: Bearer <session_key>" -H "Content-Type: application/json" \
-d '[{"question":"How often do you feel happy?","chosen_option":"Often"},{"question":"Do you feel energetic throughout the day?","chosen_option":"Yes"},{"question":"How easily do you get irritated?","chosen_option":"Rarely"},{"question":"Do you feel motivated to complete tasks?","chosen_option":"Very motivated"},{"question":"How often do you feel anxious?","chosen_option":"Almost never"},{"question":"Do you enjoy socializing with others?","chosen_option":"Yes"},{"question":"How well do you sleep at night?","chosen_option":"Very well"},{"question":"Do you feel overwhelmed by daily responsibilities?","chosen_option":"Never"},{"question":"How often do you laugh or smile?","chosen_option":"Frequently"},{"question":"Do you feel satisfied with your life?","chosen_option":"Very satisfied"}]' \
http://localhost:8000/mood/test
```

