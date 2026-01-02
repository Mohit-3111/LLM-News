# 🗞️ Multiagent LLM News

An intelligent, automated news curation system powered by multiple specialized AI agents. The system automatically gathers news from multiple sources, processes them, and prepares content for multi-platform publishing.

## ✨ Features

- **Multi-Source News Aggregation**: Fetches trending articles from NewsAPI and GNews
- **Diverse Coverage**: Ensures articles from different news agencies (BBC, CNN, TechCrunch, etc.)
- **Automated Scheduling**: Runs pipeline every 15 minutes (configurable)
- **MongoDB Storage**: Persistent storage with duplicate detection
- **Extensible Pipeline**: Designed for future LLM summarization, image generation, and multi-platform publishing

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                        │
│              (15-minute scheduled pipeline)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Scraper Agent                            │
│         (NewsAPI + GNews → MongoDB)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      MongoDB                                 │
│              (Articles Collection)                           │
└─────────────────────────────────────────────────────────────┘
```

### Agents

| Agent | Status | Description |
|-------|--------|-------------|
| **Scraper Agent** | ✅ Complete | Fetches news from NewsAPI & GNews APIs |
| **Orchestrator Agent** | ✅ Complete | Schedules and coordinates pipeline execution |
| **Curation Agent** | 🔜 Planned | LLM-powered summarization and rewriting |
| **Image Agent** | 🔜 Planned | AI image generation for articles |
| **Publisher Agent** | 🔜 Planned | Multi-platform publishing (Web, Telegram, Instagram) |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- MongoDB Atlas account (or local MongoDB)
- API Keys:
  - [NewsAPI](https://newsapi.org/) (free tier available)
  - [GNews](https://gnews.io/) (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/multiagent-llm-news.git
   cd multiagent-llm-news
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**
   ```bash
   cp config.yaml.example config.yaml
   ```
   
   Edit `config.yaml` with your API keys:
   ```yaml
   NEWS_API_ORG:
     API_KEY: "your_newsapi_key"
   
   GOOGLE_NEWS:
     API_KEY: "your_gnews_key"
   
   MONGODB:
     CONNECTION_URL: "mongodb+srv://..."
   ```

### Usage

**Single Run** - Fetch articles once:
```bash
python main.py
```

**Scheduled Mode** - Continuous pipeline (default: every 15 minutes):
```bash
python main.py --scheduler
```

**Custom Interval** - Run every N minutes:
```bash
python main.py --scheduler --interval 5
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
├── main.py                    # Entry point
├── config.yaml.example        # Configuration template
├── requirements.txt           # Python dependencies
├── agents/
│   ├── scraper_agent.py       # News fetching agent
│   └── orchestrator_agent.py  # Pipeline scheduler
├── database/
│   └── mongodb.py             # MongoDB connection manager
└── utils/
    └── helpers.py             # Utility functions
```

## ⚙️ Configuration

All settings are in `config.yaml`:

```yaml
NEWS_API_ORG:
  API_KEY: "your_key"

GOOGLE_NEWS:
  API_KEY: "your_key"

MONGODB:
  CONNECTION_URL: "mongodb+srv://..."
  DATABASE_NAME: "llm_news"
  COLLECTION_NAME: "articles"

SCRAPER:
  NEWSAPI_COUNT: 5      # Articles from NewsAPI
  GNEWS_COUNT: 2        # Articles from GNews

SCHEDULER:
  INTERVAL_MINUTES: 15  # Pipeline interval
  RUN_ON_START: true    # Run immediately on start
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
  "imageUrl": "https://...",
  "publishedAt": "2024-01-02T10:00:00Z",
  "content": "Full article text...",
  "status": "raw",
  "createdAt": "2024-01-02T10:15:00Z"
}
```

## 🛣️ Roadmap

- [x] Scraper Agent (NewsAPI + GNews)
- [x] Orchestrator Agent (APScheduler)
- [ ] Content Curation Agent (LLM summarization)
- [ ] Image Generation Agent
- [ ] Multi-Platform Publisher (Website, Telegram, Instagram)
- [ ] Web Dashboard

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
