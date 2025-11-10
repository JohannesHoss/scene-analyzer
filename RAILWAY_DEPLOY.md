# Railway Deployment Guide

## Voraussetzungen

1. Railway Account: https://railway.app
2. Railway CLI installiert (optional)
3. Git Repository mit diesem Projekt

## Deployment Schritte

### 1. Neues Projekt auf Railway erstellen

1. Gehe zu https://railway.app/new
2. Wähle "Deploy from GitHub repo"
3. Verbinde dein GitHub Repository
4. Wähle dieses Repository aus

### 2. Environment Variables setzen

Im Railway Dashboard:

```
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

**Wichtig:** Ohne diesen API Key funktioniert die Analyse nicht!

### 3. Docker Compose Deployment

Railway erkennt automatisch die `docker-compose.yml` und deployed beide Services:
- **Backend**: Port 8000 (intern) → Railway assigned Port
- **Frontend**: Port 80 (intern) → Railway assigned Port

### 4. Domain konfigurieren (Optional)

Railway gibt dir automatisch eine Domain wie:
```
https://your-app.railway.app
```

Du kannst auch eine eigene Domain verbinden unter:
Settings → Domains → Add Domain

## Wichtige Hinweise

### Ports

Railway mapped automatisch die Ports:
- Frontend wird öffentlich verfügbar gemacht
- Backend läuft intern und wird vom Frontend proxied (via nginx)

### Health Checks

Railway nutzt `/health` endpoint für Health Checks:
- URL: `http://backend:8000/health`
- Timeout: 100 Sekunden
- Restart bei Failure

### File Uploads

- Max Upload Size: 50MB (konfiguriert in nginx & FastAPI)
- Railway hat eigene Timeout-Limits (10 Minuten für requests)

### Kosten

Mit Docker Compose deployment:
- 2 Services = ~$10-15/Monat (Starter Plan)
- Pay-as-you-go: ~$0.000463/GB-minute

**Tipp:** Hobby Plan für $5/Monat empfohlen (500 Stunden Execution)

## Logs & Monitoring

### Logs ansehen

```bash
railway logs
```

Oder im Dashboard unter: Deployments → [Latest] → View Logs

### Services überwachen

- Backend Health: `https://your-app.railway.app/health`
- Frontend: `https://your-app.railway.app/`

## Troubleshooting

### Backend startet nicht

1. Check Environment Variables:
   ```bash
   railway variables
   ```

2. Setze `OPENROUTER_API_KEY`:
   ```bash
   railway variables set OPENROUTER_API_KEY=sk-or-v1-...
   ```

### Frontend kann Backend nicht erreichen

- Stelle sicher dass beide Services im selben Railway Project sind
- nginx.conf nutzt `http://backend:8000` (interne DNS-Namen)

### File Upload schlägt fehl

- Check nginx `client_max_body_size` (aktuell: 50MB)
- Check Railway timeout limits

### "Out of Memory" Errors

- AI-Analyse kann speicher-intensiv sein
- Railway free tier hat 512MB RAM
- Upgrade zu Starter Plan ($5/Monat) für mehr RAM

## Lokale Entwicklung vs. Production

### Lokal testen:

```bash
docker-compose up
```

Frontend: http://localhost:3010
Backend: http://localhost:8001

### Production:

Railway nutzt die gleichen Dockerfiles, aber:
- Kein `--reload` Flag (Production Mode)
- 2 Uvicorn Workers für bessere Performance
- Automatische SSL (HTTPS)

## Updates deployen

### Mit GitHub Integration (empfohlen):

```bash
git add .
git commit -m "feat: new feature"
git push
```

Railway deployed automatisch!

### Mit Railway CLI:

```bash
railway up
```

## Support

- Railway Docs: https://docs.railway.app
- Scene Analyzer Docs: Siehe README.md
- Issues: GitHub Issues
