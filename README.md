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
```
