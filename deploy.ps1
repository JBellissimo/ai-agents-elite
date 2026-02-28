# deploy.ps1 — Push code and restart VPS bot in one command
# Usage: .\deploy.ps1
# Run from VS Code terminal (PowerShell) after making changes.

Write-Host "Pushing to GitHub..."
git add -A
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "Deploy $timestamp" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "(nothing new to commit)" }
git push

Write-Host "Updating VPS and restarting bot..."
ssh root@5.161.215.26 "cd /opt/bellissimo && git pull && /opt/venv/bin/pip install -r requirements.txt -q && pkill -f orchestrator.py 2>/dev/null; pkill -f discord_bot.py 2>/dev/null; screen -wipe 2>/dev/null; sleep 2; screen -dm -S bellissimo /opt/venv/bin/python3 /opt/bellissimo/orchestrator.py && echo 'Orchestrator restarted'"

Write-Host "Done. Bot is live on VPS."
