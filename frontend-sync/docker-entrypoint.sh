#!/bin/sh

# Docker entrypoint script for Kuwait Social AI React Frontend
# Handles environment variable injection at runtime

set -e

# Default values
API_URL=${API_URL:-"http://backend:5000"}
APP_ENV=${APP_ENV:-"production"}
APP_VERSION=${APP_VERSION:-"1.0.0"}

echo "🚀 Starting Kuwait Social AI Frontend..."
echo "📊 Environment: $APP_ENV"
echo "🔗 API URL: $API_URL"
echo "📦 Version: $APP_VERSION"

# Create runtime config file
cat > /usr/share/nginx/html/config.js << EOF
window.APP_CONFIG = {
  API_URL: "$API_URL",
  APP_ENV: "$APP_ENV",
  APP_VERSION: "$APP_VERSION",
  FEATURES: {
    PRAYER_TIMES: true,
    COMPETITOR_ANALYSIS: true,
    AI_CONTENT_GENERATION: true,
    ANALYTICS: true
  }
};
EOF

echo "✅ Runtime configuration created"

# Start nginx
echo "🌐 Starting Nginx server..."
exec "$@"