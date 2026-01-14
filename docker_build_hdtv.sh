#!/usr/bin/env bash
set -e

# Ensure writable HOME
export HOME=/root

# Start Xvfb properly
Xvfb :99 -screen 0 1024x768x16 &
XVFB_PID=$!

# Wait for X
sleep 1

# First-run rebuild if needed
if [ ! -d "$HOME/.cache/hdtv" ]; then
    echo "Running first-time HDTV rebuild..."
    hdtv --rebuild-usr --execute exit || true
fi

# Stop Xvfb after rebuild
kill $XVFB_PID
wait $XVFB_PID 2>/dev/null || true

# Start a fresh Xvfb for interactive use
Xvfb :99 -screen 0 1024x768x16 &
exec "$@"
