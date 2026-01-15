# 🗞️ Multiagent LLM News

An intelligent, automated news curation system powered by multiple specialized AI agents. The system automatically gathers news from multiple sources, processes them, generates AI images, and publishes to a modern news website.

## ✨ Features

- **Multi-Source News Aggregation**: Fetches trending articles from NewsAPI and GNews
- **Diverse Coverage**: Ensures articles from different news agencies (BBC, CNN, TechCrunch, etc.)
- **LLM Content Curation**: Summarizes, rewrites, and extracts key entities using Groq LLM
- **AI Image Generation**: Creates unique images for each article using Pollinations.ai
- **Cloud Image Storage**: Stores generated images on ImageKit CDN (free tier: 20GB)
- **Multi-Platform Content**: Tailored content for Website, Telegram, and Instagram
- **Modern News Website**: Beautiful Next.js website with dark mode and glassmorphism design
- **Automated Scheduling**: Runs pipeline every 15 minutes (configurable)
- **MongoDB Storage**: Persistent storage with duplicate detection

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                        │
│              (15-minute scheduled pipeline)                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Scraper Agent │───▶│ Curation Agent│───▶│ Image Agent   │
│  (NewsAPI +   │    │   (Groq LLM)  │    │(Pollinations) │
│    GNews)     │    │               │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
              ┌───────────────────────────┐
              │         MongoDB           │
              │   (Articles Collection)   │
              └───────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │     LLM Daily Website     │
              │       (Next.js 14)        │
              └───────────────────────────┘
```

### Agents

| Agent | Status | Description |
|-------|--------|-------------|
| **Scraper Agent** | ✅ Complete | Fetches trending news from NewsAPI & GNews APIs |
| **Orchestrator Agent** | ✅ Complete | Schedules and coordinates pipeline execution |
| **Curation Agent** | ✅ Complete | LLM-powered summarization, rewriting, and entity extraction |
| **Image Agent** | ✅ Complete | AI image generation using Pollinations.ai (turbo model) |
| **Telegram Bot Agent** | ✅ Complete | Subscriber management and news broadcasting |
| **Publisher Agent** | ✅ Complete | Next.js website for publishing articles |

## 🌐 Website (LLM Daily)

The project includes a modern news website built with **Next.js 14**:

### Features
- 🌙 **Dark Mode** with purple/indigo gradient accents
- ✨ **Glassmorphism UI** with backdrop blur effects
- 📱 **Fully Responsive** design for all devices
- ⚡ **Server-Side Rendering** for SEO optimization
- 🖼️ **AI-Generated Images** served from ImageKit CDN
- 🔄 **Auto-refresh** every 5 minutes for fresh content

### Running the Website

```bash
cd website
npm install
npm run dev
```

Visit: **http://localhost:3000**

### Website Pages

| Page | Route | Description |
|------|-------|-------------|
| Homepage | `/` | Hero section with featured article + news grid |
| Article | `/article/[id]` | Full article with image and content |
| About | `/about` | Information about the platform |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/articles` | GET | Fetch articles with pagination |
| `/api/publish` | POST | Mark article as published |
| `/api/track` | POST/GET | Track article views for analytics |

## 📊 Analytics

The platform includes built-in analytics tracking:

### Website Analytics
- **Page View Tracking** - Automatic tracking of article views
- **View History** - Timestamps stored for each view
- **Real-time Data** - Stored in MongoDB `pageviews` collection

### Admin Analytics Dashboard
Access at: **http://localhost:3001/analytics**

- 📈 **Charts** - Bar and pie charts showing article performance
- 🏆 **Top Articles** - Ranked by view count
- 📅 **Time Trends** - View patterns over time
- 🔄 **Auto-refresh** - Updates every 30 seconds

## 🤖 Telegram Bot

Automatic news broadcasting to Telegram subscribers.

### Features
- 📲 **Subscribe/Unsubscribe** - `/start` and `/stop` commands
- 📰 **Auto-broadcast** - News sent when pipeline completes
- 🖼️ **Rich Messages** - Includes images and article links
- 📊 **Subscriber Management** - Stored in MongoDB

### Setup

1. **Create bot** via [@BotFather](https://t.me/BotFather) on Telegram
2. **Update config.yaml**:
   ```yaml
   TELEGRAM:
     BOT_TOKEN: "your_bot_token"
     ENABLED: true
     WEBSITE_URL: "https://your-site.vercel.app"
   ```

### Running the Bot

```bash
# Start bot to accept subscriptions
python agents/telegram_bot_agent.py

# Or run full pipeline (auto-broadcasts to subscribers)
python main.py --run-once
```

### Bot Commands
| Command | Description |
|---------|-------------|
| `/start` | Subscribe to news updates |
| `/stop` | Unsubscribe from updates |
| `/status` | Check subscription status |

A separate admin panel for monitoring and managing the news pipeline.

### Features
- 📊 **Stats Overview** - Article counts by status (raw, curated, processed, filtered, errors)
- 📰 **Article Table** - View all articles with status, source, and timestamps
- 🔗 **Dynamic Links** - Click to view processed articles on website or original source
- 🔍 **Filter Tabs** - Filter articles by status
- 🔄 **Auto-refresh** - Updates every 30 seconds

### Running the Admin Dashboard

```bash
cd admin
npm install
npm run dev
```

Visit: **http://localhost:3001**

### Configuration

To change the website URL for article links, edit `admin/src/pages/index.js`:

```javascript
const WEBSITE_URL = 'https://your-website.vercel.app';
```

## �🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+ (for website)
- MongoDB Atlas account (or local MongoDB)
- API Keys:
  - [NewsAPI](https://newsapi.org/) (free tier available)
  - [GNews](https://gnews.io/) (free tier available)
  - [Groq](https://console.groq.com/) (free tier for LLM - required for curation)
  - [ImageKit](https://imagekit.io/) (free tier: 20GB storage/bandwidth - for image hosting)
  - [Telegram Bot Token](https://t.me/BotFather) (optional - for Telegram broadcasting)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mohit-3111/LLM-News.git
   cd LLM-News
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Website dependencies**
   ```bash
   cd website
   npm install
   cd ..
   ```

5. **Configure API keys**
   ```bash
   cp config.yaml.example config.yaml
   ```
   
   Edit `config.yaml` with your API keys:
   ```yaml
   NEWS_API_ORG:
     API_KEY: "your_newsapi_key"
   
   GOOGLE_NEWS:
     API_KEY: "your_gnews_key"
   
   LLM:
     API_KEY: "your_groq_api_key"
     MODEL: "llama-3.3-70b-versatile"
   
   IMAGEKIT:
     PRIVATE_KEY: "private_xxxxxxxxxxxxx"
   
   MONGODB:
     CONNECTION_URL: "mongodb+srv://..."
   ```

### Usage

**Single Run** - Fetch and process articles once:
```bash
python main.py
```

**Scheduled Mode** - Continuous pipeline (default: every 15 minutes):
```bash
python main.py --scheduler
```

**Run Website** - Start the news website:
```bash
cd website
npm run dev
```

**Options**:
```
--scheduler          Run in scheduled mode (continuous cycles)
--interval N         Scheduler interval in minutes (default: from config.yaml)
--no-initial-run     Don't run pipeline immediately on start
--newsapi-count N    Number of articles from NewsAPI (default: 5)
--gnews-count N      Number of articles from GNews (default: 2)
-v, --verbose        Enable verbose logging
```

## 📁 Project Structure

```
multiagent-llm-news/
├── main.py                        # Entry point
├── config.yaml.example            # Configuration template
├── requirements.txt               # Python dependencies
├── agents/
│   ├── scraper_agent.py           # News fetching agent
│   ├── orchestrator_agent.py      # Pipeline scheduler
│   ├── content_curation_agent.py  # LLM summarization & rewriting
│   ├── image_creation_agent.py    # AI image generation
│   ├── article_ranking_agent.py   # LLM-based article selection
│   └── telegram_bot_agent.py      # Telegram subscriber & broadcast
├── database/
│   └── mongodb.py                 # MongoDB connection manager
├── utils/
│   └── helpers.py                 # Utility functions
├── admin/                         # Admin Dashboard (Next.js)
│   ├── src/
│   │   ├── pages/                 # Dashboard pages & API routes
│   │   ├── lib/                   # MongoDB connection
│   │   └── styles/                # CSS styles
│   └── package.json
└── website/                       # News Website (Next.js)
    ├── src/
    │   ├── app/                   # Next.js App Router pages
    │   ├── components/            # React components
    │   └── lib/                   # MongoDB utilities
    ├── package.json
    └── next.config.mjs
```

## ⚙️ Configuration

All settings are in `config.yaml`:

```yaml
NEWS_API_ORG:
  API_KEY: "your_key"

GOOGLE_NEWS:
  API_KEY: "your_key"

LLM:
  API_KEY: "your_groq_api_key"
  MODEL: "llama-3.3-70b-versatile"
  TEMPERATURE: 0.7
  MAX_TOKENS: 2000

MONGODB:
  CONNECTION_URL: "mongodb+srv://..."
  DATABASE_NAME: "llm_news"
  COLLECTION_NAME: "articles"

SCRAPER:
  NEWSAPI_COUNT: 5
  GNEWS_COUNT: 2

IMAGE_GENERATION:
  ENABLED: true
  BATCH_SIZE: 10

IMAGEKIT:
  PRIVATE_KEY: "your_private_key_here"
  PUBLIC_KEY: "your_public_key_here"
  URL_ENDPOINT: "your_url_endpoint_here"

SCHEDULER:
  INTERVAL_MINUTES: 15
  RUN_ON_START: true
```

## 📊 Article Schema

Articles are stored in MongoDB with this structure:

```json
{
  "source": "BBC News",
  "apiSource": "NewsAPI",
  "title": "Article headline",
  "description": "Brief description",
  "url": "https://...",
  "content": "Full article text...",
  "status": "processed",
  "curated": {
    "summary": "2-3 sentence summary",
    "rewritten_content": "Full rewritten article",
    "entities": { "people": [], "organizations": [], "locations": [] },
    "hashtags": ["#news", "#technology"]
  },
  "platforms": {
    "website": { "full_article": "..." },
    "telegram": { "teaser": "...", "link": "..." },
    "instagram": { "caption": "...", "hashtags": [] }
  },
  "images": {
    "website": { "url": "https://ik.imagekit.io/..." },
    "telegram": { "url": "https://ik.imagekit.io/..." },
    "instagram": [{ "url": "https://ik.imagekit.io/..." }]
  },
  "createdAt": "2024-01-02T10:15:00Z"
}
```

## 🛠️ Tech Stack

### Backend
- **Python 3.9+** - Core language
- **Groq LLM** - Content curation (Llama 3.3 70B)
- **Pollinations.ai** - AI image generation
- **MongoDB** - Database storage
- **APScheduler** - Task scheduling
- **ImageKit** - Cloud image storage & CDN

### Website
- **Next.js 14** - React framework with App Router
- **Vanilla CSS** - Custom design system
- **MongoDB Driver** - Direct database connection

## 🛣️ Roadmap

- [x] Scraper Agent (NewsAPI + GNews)
- [x] Orchestrator Agent (APScheduler)
- [x] Content Curation Agent (Groq LLM - summarization, rewriting, entity extraction)
- [x] Image Generation Agent (Pollinations.ai - turbo model)
- [x] News Website (Next.js with modern UI)
- [x] Telegram Bot Integration
- [ ] Instagram Auto-Posting
- [x] Web Analytics Dashboard

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
