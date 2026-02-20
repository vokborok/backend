#!/bin/bash

# ===========================================
# Setup script for mergehero.fun domain
# ===========================================
# This script configures Apache2 for the MergeHero game
# Run with: sudo ./setup-mergehero-fun.sh

set -e

echo "🎮 Setting up Apache for mergehero.fun..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root or with sudo"
    echo "   Usage: sudo ./setup-mergehero-fun.sh"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN="mergehero.fun"
CONFIG_FILE="mergehero.fun.conf"
WEBROOT="/var/www/html/mergehero"

echo ""
echo "📋 Configuration:"
echo "   Domain: $DOMAIN"
echo "   Config: $CONFIG_FILE"
echo "   WebRoot: $WEBROOT"
echo ""

# Check if SSL certificates exist
echo "🔐 Checking SSL certificates..."
SSL_CERT="/etc/letsencrypt/live/mergehero.fun/mergehero.crt"
SSL_KEY="/etc/letsencrypt/live/mergehero.fun/mergehero.key"
SSL_CHAIN="/etc/letsencrypt/live/mergehero.fun/ca.crt"

if [ ! -f "$SSL_CERT" ]; then
    echo "❌ SSL certificate not found: $SSL_CERT"
    exit 1
fi
if [ ! -f "$SSL_KEY" ]; then
    echo "❌ SSL key not found: $SSL_KEY"
    exit 1
fi
if [ ! -f "$SSL_CHAIN" ]; then
    echo "❌ SSL chain not found: $SSL_CHAIN"
    exit 1
fi
echo "✅ SSL certificates found"

# Enable required Apache modules
echo ""
echo "📦 Enabling required Apache modules..."
a2enmod proxy 2>/dev/null || echo "   proxy already enabled"
a2enmod proxy_http 2>/dev/null || echo "   proxy_http already enabled"
a2enmod ssl 2>/dev/null || echo "   ssl already enabled"
a2enmod rewrite 2>/dev/null || echo "   rewrite already enabled"
a2enmod headers 2>/dev/null || echo "   headers already enabled"
a2enmod deflate 2>/dev/null || echo "   deflate already enabled"
a2enmod mime 2>/dev/null || echo "   mime already enabled"
echo "✅ Apache modules enabled"

# Create document root directory if it doesn't exist
echo ""
echo "📁 Creating document root directory..."
if [ ! -d "$WEBROOT" ]; then
    mkdir -p "$WEBROOT"
    chown -R www-data:www-data "$WEBROOT"
    chmod -R 755 "$WEBROOT"
    echo "✅ Created $WEBROOT"
else
    echo "ℹ️  Directory already exists: $WEBROOT"
fi

# Create a placeholder index.html if it doesn't exist
if [ ! -f "$WEBROOT/index.html" ]; then
    cat > "$WEBROOT/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MergeHero</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }
        .container { padding: 20px; }
        h1 { font-size: 3em; margin-bottom: 0.5em; }
        p { font-size: 1.2em; opacity: 0.9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 MergeHero</h1>
        <p>Coming soon...</p>
    </div>
</body>
</html>
EOF
    chown www-data:www-data "$WEBROOT/index.html"
    echo "✅ Created placeholder index.html"
fi

# Copy configuration file to Apache sites-available
echo ""
echo "📋 Copying configuration file..."
if [ -f "$SCRIPT_DIR/$CONFIG_FILE" ]; then
    cp "$SCRIPT_DIR/$CONFIG_FILE" /etc/apache2/sites-available/
    echo "✅ Copied $CONFIG_FILE to /etc/apache2/sites-available/"
else
    echo "❌ Configuration file not found: $SCRIPT_DIR/$CONFIG_FILE"
    exit 1
fi

# Enable the site
echo ""
echo "🌐 Enabling site..."
a2ensite "$CONFIG_FILE" 2>/dev/null || echo "   Site already enabled"
echo "✅ Site enabled"

# Test Apache configuration
echo ""
echo "🧪 Testing Apache configuration..."
if apache2ctl configtest 2>&1 | grep -q "Syntax OK"; then
    echo "✅ Apache configuration is valid"
else
    echo "❌ Apache configuration test failed:"
    apache2ctl configtest
    exit 1
fi

# Restart Apache
echo ""
echo "🔄 Restarting Apache..."

# Stop Apache completely
systemctl stop apache2 2>/dev/null || true
sleep 1

# Kill any remaining apache processes
pkill -9 apache2 2>/dev/null || true
sleep 1

# Start Apache
systemctl start apache2

# Check if Apache started successfully
sleep 2
if systemctl is-active --quiet apache2; then
    echo "✅ Apache restarted successfully"
else
    echo "❌ Failed to start Apache. Checking logs..."
    journalctl -u apache2 --no-pager -n 20
    exit 1
fi

# Verify the site is accessible
echo ""
echo "🔍 Verifying site accessibility..."

# Test HTTPS
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "https://$DOMAIN" 2>/dev/null || echo "000")
if [ "$HTTPS_STATUS" = "200" ] || [ "$HTTPS_STATUS" = "301" ] || [ "$HTTPS_STATUS" = "302" ]; then
    echo "✅ HTTPS is accessible (HTTP $HTTPS_STATUS)"
else
    echo "⚠️  HTTPS returned HTTP $HTTPS_STATUS (this might be normal if DNS is not configured yet)"
fi

# Test backend health endpoint
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://localhost:8002/health" 2>/dev/null || echo "000")
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ Backend health endpoint is accessible"
else
    echo "⚠️  Backend not responding (HTTP $BACKEND_STATUS) - make sure Docker is running"
fi

# Summary
echo ""
echo "=========================================="
echo "🎉 Setup complete!"
echo "=========================================="
echo ""
echo "📱 Your site should be available at:"
echo "   - https://mergehero.fun"
echo "   - https://www.mergehero.fun"
echo ""
echo "🔌 API endpoints:"
echo "   - https://mergehero.fun/MH/ (API)"
echo "   - https://mergehero.fun/telegram/ (Telegram webhook)"
echo "   - https://mergehero.fun/docs (Swagger UI)"
echo "   - https://mergehero.fun/health (Health check)"
echo ""
echo "📁 Static files location:"
echo "   - $WEBROOT"
echo ""
echo "📝 Log files:"
echo "   - Error: /var/log/apache2/mergehero_fun_error.log"
echo "   - Access: /var/log/apache2/mergehero_fun_access.log"
echo ""
echo "🐳 Don't forget to start the backend:"
echo "   cd /path/to/MergeHeroServer && docker-compose up -d"
echo ""
