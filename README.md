# 🗞️ Multiagent LLM News

An intelligent, automated news curation system powered by multiple specialized AI agents. The system automatically gathers news from multiple sources, processes them, and prepares content for multi-platform publishing.

## ✨ Features

- **Multi-Source News Aggregation**: Fetches trending articles from NewsAPI and GNews
- **Diverse Coverage**: Ensures articles from different news agencies (BBC, CNN, TechCrunch, etc.)
- **LLM Content Curation**: Summarizes, rewrites, and extracts key entities using Groq LLM
- **AI Image Generation**: Creates unique images for each article using Pollinations.ai
- **Multi-Platform Content**: Tailored content for Website, Telegram, and Instagram
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
```

### Agents

| Agent | Status | Description |
|-------|--------|-------------|
| **Scraper Agent** | ✅ Complete | Fetches trending news from NewsAPI & GNews APIs |
| **Orchestrator Agent** | ✅ Complete | Schedules and coordinates pipeline execution |
| **Curation Agent** | ✅ Complete | LLM-powered summarization, rewriting, and entity extraction |
| **Image Agent** | ✅ Complete | AI image generation using Pollinations.ai (turbo model) |
| **Publisher Agent** | 🔜 Planned | Multi-platform publishing (Website, Telegram, Instagram) |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- MongoDB Atlas account (or local MongoDB)
- API Keys:
  - [NewsAPI](https://newsapi.org/) (free tier available)
  - [GNews](https://gnews.io/) (free tier available)
  - [Groq](https://console.groq.com/) (free tier for LLM - required for curation)

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
   
   LLM:
     API_KEY: "your_groq_api_key"
     MODEL: "llama-3.3-70b-versatile"
   
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
├── main.py                        # Entry point
├── config.yaml.example            # Configuration template
├── requirements.txt               # Python dependencies
├── agents/
│   ├── scraper_agent.py           # News fetching agent
│   ├── orchestrator_agent.py      # Pipeline scheduler
│   ├── content_curation_agent.py  # LLM summarization & rewriting
│   └── image_creation_agent.py    # AI image generation
├── database/
│   └── mongodb.py                 # MongoDB connection manager
├── utils/
│   └── helpers.py                 # Utility functions
└── generated_images/              # Output directory for AI images
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
  OUTPUT_DIR: "generated_images"
  BATCH_SIZE: 10

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
    "website": { "path": "generated_images/.../website_01.jpg" },
    "telegram": { "path": "generated_images/.../telegram_01.jpg" },
    "instagram": [{ "path": "..." }]
  },
  "createdAt": "2024-01-02T10:15:00Z"
}
```

## 🛣️ Roadmap

- [x] Scraper Agent (NewsAPI + GNews)
- [x] Orchestrator Agent (APScheduler)
- [x] Content Curation Agent (Groq LLM - summarization, rewriting, entity extraction)
- [x] Image Generation Agent (Pollinations.ai - turbo model)
- [ ] Multi-Platform Publisher (Website, Telegram, Instagram)
- [ ] Web Dashboard

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
