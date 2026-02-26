#!/bin/bash
# deploy.sh — Push code and restart the VPS bot in one command
# Usage: bash deploy.sh
#
# Run from your local VS Code terminal after making changes.
# Requires: SSH key added to GitHub (done) and VPS SSH key set up (run deploy-setup.sh first)

set -e

echo "Pushing to GitHub..."
git add -A
git commit -m "Deploy $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || echo "(nothing new to commit)"
git push

echo "Pulling to VPS and restarting bot..."
ssh root@5.161.215.26 'cd /opt/bellissimo && git pull && screen -S bellissimo -X stuff "^C" && sleep 2 && screen -S bellissimo -X stuff "/opt/venv/bin/python3 discord_bot.py\n"'

echo "Done. Bot is restarting on VPS."
