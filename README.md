# Housing Tracker Munich

An automated web scraping and alerting service designed to monitor Munich housing market. The bot aggregates listings from **Kleinanzeigen** and **WG-Gesucht** and sends push notifications via Telegram every 10 minutes.

The bot is currently deployed on **Render.com**, running 24/7. It utilizes a Flask-based keep-alive server and external cron-jobs to maintain high availability within the free tier environment.

### System Architecture
1. **Scraper Modules:** Extracts raw data (Title, Price, Time, Link) nad cleanses the HTML entities.
2. **Database Layer:** Checks for existing entries
3. **Notification Service:** Formats and dispatches HTML-Styled messages to the Telegram bot.
4. **Execution Loop:** Manages timing and runs a parallel thread for the Flask web server.

## Quickstart (Docker)

The easiest way to run the project is using Docker. It will automatically spin up the PostgreSQL database and the Python application.

### 1. Clone the Repository
```bash
git clone [https://github.com/bence-vrd/housing-tracker-munich.git](https://github.com/bence-vrd/housing-tracker-munich.git)
cd housing-tracker-munich
````
### 2. Configure Environment Variables (.env)
Create a .env file in the root directory and add your credentials and search URLs:
````Code-Snippet
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DATABASE_URL=postgresql://user:password@host:port/dbname

KLEINANZEIGEN_URL="[https://www.kleinanzeigen.de/](https://www.kleinanzeigen.de/)..."
WG_GESUCHT_URL="[https://www.wg-gesucht.de/](https://www.wg-gesucht.de/)..."
````

### 3. Build and Run
````bash
docker-compose up --build
````
Once the containers are running, you can access the Web Dashboard at: http://localhost8080
and you will receive every 10 minutes updates via Telegram.

## Deployment (Render.com Free Tier)

This bot is optimized to run 24/7 on the free tier of [Render.com](https://render.com)

1. **Web Service Setup:** Create a new Web Service on Render and connect your GitHub repository.
2. **Environment:** Choose `Docker` as the runtime environment (Render will automatically detect the `Dockerfile`).
3. **Environment Variables:** Add your `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `DATABASE_URL`, `KLEINANZEIGEN_URL` and `WG-GESUCHT_URL` in the Render dashboard.
4. **Keep-Alive Strategy:** Render's free tier spins down web services after 15 minutes of inactivity. To prevent this, the bot runs a lightweight Flask web server. You must set up an external cron-job to ping the Web Dashboard URL every 5-10 minutes.