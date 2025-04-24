# LevelUP Backend

API for LevelUP - service for effective education

## API Callbacks

```
# Register new user
curl -X POST "http://localhost:8000/register?login=test&password=123456"

# Login
curl -X POST "http://localhost:8000/login?login=test&password=123456"

# Verify session (replace SESSION_KEY)
curl -H "Authorization: Bearer SESSION_KEY" http://localhost:8000/verify

# Logout
curl -X POST -H "Authorization: Bearer SESSION_KEY" http://localhost:8000/logout

# Update statistics

curl -X POST "http://localhost:8000/account/statistics" \
-H "Authorization: Bearer <session_key>" \
-H "X-API-Key: $(echo -n 'your_api_secret_key' | base64)" \
-H "Content-Type: application/json" \
-d '{"achievements": ["new_achievement"], "courses": ["new_course"]}'

# Update account info

curl -X POST "http://localhost:8000/account/info" \
-H "Authorization: Bearer <session_key>" \
-H "X-API-Key: $(echo -n 'your_api_secret_key' | base64)" \
-H "Content-Type: application/json" \
-d '{"points": 100, "level": 2}'

# Get account info

curl -X GET "http://localhost:8000/account/info" \
-H "Authorization: Bearer <session_key>" \
-H "X-API-Key: $(echo -n 'your_api_secret_key' | base64)"
```
