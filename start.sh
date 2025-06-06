#!/bin/bash

# Start virtual display
Xvfb :1 -screen 0 1024x768x16 &
export DISPLAY=:1

# Wait for Xvfb to initialize
sleep 2

# Start window manager and panel
openbox-session & tint2 &

# Start VNC server
x11vnc -display :1 -forever -nopw -shared -rfbport 5900 &

# Start Python app
python3 /app/production/control.py &

# Start noVNC and keep it in foreground 
/opt/novnc/utils/launch.sh --vnc localhost:5900 --listen 8080
