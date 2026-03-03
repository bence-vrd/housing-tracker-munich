# Housing Tracker Munich

An automated web scraping and alerting service designed to monitor Munich housing market. The bot aggregates listings from Kleinanzeigen and WG-Gesucht and sends push notifications via Telegram every 10 minutes.

The bot is currently deployed on **Render.com**, running 24/7. It utilizes a Flask-based keep-alive server and external cron-jobs to maintain high availability within the free tier environment.

### System Architecture
1. **Scraper Modules:** Extracts raw data (Title, Price, Time, Link) nad cleanses the HTML entities.
2. **Database Layer:** Checks for existing entries
3. **Notification Service:** Formats and dispatches HTML-Styled messages to the Telegram bot.
4. **Execution Loop:** Manages timing and runs a parallel thread for the Flask web server.

## Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/bence-vrd/housing-tracker-munich.git](https://github.com/bence-vrd/housing-tracker-munich.git)
cd housing-tracker-munich
````

### 2. Install Dependencies
````bash
pip install -r requirements.txt
````

### 3. Environment Variables (.env)
Create a .env file in the root directory
````Code-Snippet
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DATABASE_URL=postgresql://user:password@host:port/dbname
````

### 4. Run Locally
````bash
python main.py
````

## Deployment (Render.com)
- **Build Command:** ````pip install -r requirements.txt````
- **Start Command:** ````python main.py````
- **Region:** Frankfurt (EU Central)
- **Environment Variables:** Must be set in the Render Dashboard under the “Environment” tab.