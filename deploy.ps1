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
ssh root@5.161.215.26 "cd /opt/bellissimo && git pull && pkill -f discord_bot.py; sleep 2; screen -dm -S bellissimo /opt/venv/bin/python3 discord_bot.py && echo 'Bot restarted'"

Write-Host "Done. Bot is live on VPS."
