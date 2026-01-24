# 📊 Multiagent LLM News - Comprehensive Project Report

> **Generated:** January 24, 2026  
> **Project Path:** `e:\LLM News`  
> **Repository:** [Mohit-3111/LLM-News](https://github.com/Mohit-3111/LLM-News)

---

## 📋 Executive Summary

**Multiagent LLM News** is an intelligent, automated news curation system powered by multiple specialized AI agents. The system automatically:

1. **Aggregates** trending news from multiple sources (NewsAPI, GNews)
2. **Curates** content using LLM (Groq with Llama 3.3 70B)
3. **Generates** AI images (Pollinations.ai → ImageKit CDN)
4. **Publishes** to a modern Next.js website
5. **Broadcasts** to Telegram subscribers

The pipeline runs every **30 minutes** (configurable), processing articles through a 5-stage pipeline with intelligent article ranking to select the most trending stories.

---

## 📋 Article Status Lifecycle

The system uses a **status-based workflow** to track articles through the pipeline. Each status represents a specific stage of processing.

### Status Flow Diagram

```
                                    ┌─────────────────┐
                                    │   API SOURCES   │
                                    │ (NewsAPI/GNews) │
                                    └────────┬────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                              STATUS: 'raw'                                  │
│  • Article just fetched from API                                           │
│  • Full text extracted via BeautifulSoup                                   │
│  • Basic metadata stored (title, URL, source, description)                 │
│  • Waiting for curation                                                    │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │      ARTICLE RANKING AGENT      │
                    │   (if ARTICLE_RANKING.ENABLED)  │
                    └────────────────┬────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  STATUS: 'filtered' │  │    STATUS: 'raw'    │  │  (Other articles)   │
│                     │  │   (Best article)    │  │  STATUS: 'filtered' │
│  • Not selected by  │  │                     │  │                     │
│    LLM ranking      │  │  • Selected as most │  │  • Marked filtered  │
│  • Will NOT be      │  │    trending/worthy  │  │  • Will NOT proceed │
│    processed        │  │  • Continues to     │  │                     │
│  • Archived in DB   │  │    curation stage   │  │                     │
└─────────────────────┘  └──────────┬──────────┘  └─────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                            STATUS: 'curated'                                │
│  • LLM summarization complete                                              │
│  • Content rewritten to avoid plagiarism                                   │
│  • Entities extracted (people, orgs, locations)                            │
│  • Hashtags generated                                                      │
│  • Platform-specific content created:                                      │
│    - Website: SEO headline + 3 paragraphs                                  │
│    - Telegram: Emoji teaser message                                        │
│    - Instagram: Caption + hashtags                                         │
│  • Ready for image generation                                              │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                       STATUS: 'generating_images'                           │
│  • Temporary status during image generation                                │
│  • LLM creates 3 creative image prompts                                    │
│  • Pollinations.ai generates images                                        │
│  • Images uploaded to ImageKit CDN                                         │
│  • Prevents duplicate processing if pipeline restarts                      │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           STATUS: 'processed'                               │
│  • FINAL STATUS - Article fully ready                                      │
│  • All content curated and finalized                                       │
│  • All images generated and hosted on CDN                                  │
│  • Visible on website immediately                                          │
│  • Eligible for Telegram broadcast                                         │
│  • Fields populated:                                                       │
│    - curated: {summary, rewritten_content, entities, hashtags}            │
│    - platforms: {website, telegram, instagram}                             │
│    - images: {website: {url}, telegram: {url}, instagram: [{url}...]}     │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    TELEGRAM BROADCAST (telegram_broadcast: true)            │
│  • Article sent to all Telegram subscribers                                │
│  • Includes image + teaser + link to website                               │
│  • Marked with telegram_broadcast_at timestamp                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Status Reference Table

| Status | Description | Next Action | Agent Responsible |
|--------|-------------|-------------|-------------------|
| `raw` | Fresh from API, unprocessed | Ranking or Curation | Scraper Agent |
| `filtered` | Not selected by LLM ranking | None (archived) | Ranking Agent |
| `curated` | LLM content generated | Image generation | Curation Agent |
| `generating_images` | Image pipeline in progress | Wait for completion | Image Agent |
| `processed` | Fully complete, published | Telegram broadcast | Image Agent |

### Additional Status Flags

| Field | Type | Description |
|-------|------|-------------|
| `telegram_broadcast` | Boolean | Whether article was sent to Telegram |
| `telegram_broadcast_at` | DateTime | When broadcast occurred |
| `image_retry_count` | Integer | Number of image generation retries (max 3) |

---

## 🧠 LLM Selection: Why Groq + Llama 3.3 70B

### The Decision Matrix

When selecting an LLM for this project, we evaluated several options:

| Provider | Model | Cost | Speed | Quality | Context | Selected? |
|----------|-------|------|-------|---------|---------|-----------|
| **Groq** | Llama 3.3 70B | **FREE** | ⚡ 500+ tok/s | ★★★★★ | 128K | ✅ **YES** |
| OpenAI | GPT-4o | $2.50/1M tokens | ~100 tok/s | ★★★★★ | 128K | ❌ |
| Anthropic | Claude 3.5 Sonnet | $3/1M tokens | ~80 tok/s | ★★★★★ | 200K | ❌ |
| Google | Gemini 1.5 Pro | $1.25/1M tokens | ~150 tok/s | ★★★★☆ | 2M | ❌ |
| Hugging Face | Zephyr 7B | FREE | ~20 tok/s | ★★★☆☆ | 8K | ❌ |
| Local | Llama 3.1 8B | FREE | ~5 tok/s | ★★★☆☆ | 8K | ❌ |

### Why Groq Won

#### 1. **Zero Cost (Free Tier)**
```
Daily Limit: ~14,000 requests/day
Token Limit: ~500,000 tokens/day
Perfect for: Hobby projects, startups, MVPs
```

For a news pipeline running every 30 minutes (48 runs/day) with ~5 LLM calls per article, we use approximately:
- **240 LLM calls/day** (well under limit)
- **~100,000 tokens/day** (well under limit)

#### 2. **Insane Speed (LPU Architecture)**

Groq uses custom **LPU (Language Processing Unit)** hardware:

| Metric | Groq LPU | NVIDIA GPU | Improvement |
|--------|----------|------------|-------------|
| Inference Speed | 500+ tok/s | ~100 tok/s | **5x faster** |
| Latency | <100ms TTFT | 500ms+ TTFT | **5x lower** |
| Throughput | Linear scaling | Memory bound | **Deterministic** |

> **Why is Groq so fast?**  
> Traditional GPUs are memory-bandwidth limited. Groq's LPU is a **deterministic, single-core architecture** that eliminates memory bottlenecks by keeping the entire model in SRAM with direct data flow.

#### 3. **Llama 3.3 70B Quality**

Llama 3.3 70B is Meta's latest open-source model with exceptional performance:

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLAMA 3.3 70B BENCHMARKS                     │
├─────────────────────────────────────────────────────────────────┤
│  MMLU (Knowledge)            │  82.0%  │  ████████████████░░░  │
│  HellaSwag (Reasoning)       │  87.5%  │  █████████████████░░  │
│  HumanEval (Code)            │  81.7%  │  ████████████████░░░  │
│  GSM8K (Math)                │  93.2%  │  ██████████████████░  │
│  GPQA (Expert Q&A)           │  46.7%  │  █████████░░░░░░░░░░  │
└─────────────────────────────────────────────────────────────────┘
```

**For news curation specifically:**
- ★★★★★ **Summarization** - Coherent, accurate summaries
- ★★★★★ **Rewriting** - Natural, plagiarism-free content
- ★★★★☆ **Entity Extraction** - Reliable NER
- ★★★★★ **Creative Writing** - Engaging teasers and captions

#### 4. **128K Context Window**

Articles can be long. Llama 3.3 70B supports **128,000 tokens** (~300 pages):

```python
# We truncate to 4000 chars for efficiency, but could process much more
content = content[:4000]  # ~1000 tokens
```

### Llama 3.3 70B Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LLAMA 3.3 70B ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         INPUT EMBEDDING                              │   │
│  │  Vocabulary: 128,256 tokens | Embedding Dim: 8,192                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    TRANSFORMER DECODER LAYERS                        │   │
│  │                         (80 layers total)                            │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  GROUPED QUERY ATTENTION (GQA)                               │    │   │
│  │  │  • 64 attention heads                                        │    │   │
│  │  │  • 8 key-value heads (8:1 grouping)                         │    │   │
│  │  │  • Head dimension: 128                                       │    │   │
│  │  │  • RoPE positional encoding (θ=500,000)                     │    │   │
│  │  │  • Supports 128K context via position interpolation         │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  FEED-FORWARD NETWORK (SwiGLU)                               │    │   │
│  │  │  • Hidden dimension: 28,672                                  │    │   │
│  │  │  • SwiGLU activation (gate * swish(x) * linear(x))          │    │   │
│  │  │  • 3x parameter efficiency vs standard FFN                   │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                              │                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  RMSNorm (Pre-normalization)                                 │    │   │
│  │  │  • Applied before attention and FFN                          │    │   │
│  │  │  • More stable than LayerNorm                                │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │                         × 80 Layers                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         OUTPUT HEAD                                  │   │
│  │  Linear projection → Softmax → Token probabilities                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  TOTAL PARAMETERS: 70.6 Billion                                            │
│  TRAINING DATA: 15T+ tokens (curated web, code, multilingual)             │
│  TRAINING COMPUTE: ~6.4M GPU hours (H100)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Innovations

#### 1. **Grouped Query Attention (GQA)**
```
Standard Multi-Head Attention:
  Q heads: 64 | K heads: 64 | V heads: 64 → Expensive!

Grouped Query Attention (8:1):
  Q heads: 64 | K heads: 8 | V heads: 8 → 8x less KV cache!
```

Benefits:
- **8x reduction** in KV cache memory
- Enables longer context windows
- Minimal quality loss vs full MHA

#### 2. **SwiGLU Activation**
```python
# Standard: ReLU(x) or GELU(x)
# SwiGLU: gate * SiLU(linear1(x)) * linear2(x)

def swiglu(x):
    gate = linear1(x)
    up = linear2(x)
    return SiLU(gate) * up  # Element-wise
```

Benefits:
- Better gradient flow
- Improved training stability
- Higher quality outputs

#### 3. **RoPE (Rotary Position Embeddings)**
```
θ = 500,000 (base frequency)

Encodes position by rotating query/key vectors:
  q_rotated = q * cos(mθ) + rotate(q) * sin(mθ)
```

Benefits:
- Relative position awareness
- Extrapolates to longer sequences
- More efficient than absolute positional embeddings

### How We Use the LLM

Our configuration in `config.yaml`:

```yaml
LLM:
  PROVIDER: "groq"
  API_KEY: "gsk_..."
  MODEL: "llama-3.3-70b-versatile"
  MAX_TOKENS: 2048
  TEMPERATURE: 0.7
```

**Temperature Setting (0.7):**
- Balanced between creativity and consistency
- Good for rewriting and creative teasers
- Slightly deterministic for entity extraction

**LLM Calls Per Article:**

| Stage | Purpose | Max Tokens | Temperature |
|-------|---------|------------|-------------|
| 1. Summarize & Rewrite | Content transformation | 2048 | 0.7 |
| 2. Extract Entities | NER | 500 | 0.7 |
| 3. Generate Hashtags | Social media tags | 200 | 0.7 |
| 4. Website Content | SEO headline + paragraphs | 2048 | 0.7 |
| 5. Telegram Teaser | Catchy message | 300 | 0.7 |
| 6. Instagram Caption | Engagement caption | 200 | 0.7 |
| 7. Image Prompts | Creative prompts | 500 | 0.7 |

**Total: ~7 LLM calls per article** (with rate limiting delays)

### Rate Limiting Strategy

```python
# Content Curation - 2 second delay between calls
CONTENT_CURATION:
  DELAY_BETWEEN_CALLS: 2

# Image Agent - exponential backoff for rate limits
max_retries = 3
for attempt in range(max_retries):
    try:
        response = groq_client.chat.completions.create(...)
        time.sleep(2)  # Post-call delay
        return response
    except RateLimitError:
        wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s
        time.sleep(wait_time)
```

---

## 🏗️ System Architecture

### High-Level Pipeline Flow

```
                    ┌─────────────────────────────────────┐
                    │       ORCHESTRATOR AGENT            │
                    │    (APScheduler - 30 min cycle)     │
                    └─────────────────┬───────────────────┘
                                      │
        ┌──────────────┬──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼              ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   SCRAPER     │ │   RANKER      │ │   CURATOR     │ │   IMAGE GEN   │ │   TELEGRAM    │
│   AGENT       │→│   AGENT       │→│   AGENT       │→│   AGENT       │→│   BOT AGENT   │
├───────────────┤ ├───────────────┤ ├───────────────┤ ├───────────────┤ ├───────────────┤
│ • NewsAPI     │ │ • LLM-based   │ │ • Summarize   │ │ • Prompt Gen  │ │ • Subscribe   │
│ • GNews       │ │   selection   │ │ • Rewrite     │ │ • Pollinations│ │ • Broadcast   │
│ • Full text   │ │ • Top N pick  │ │ • Entities    │ │ • ImageKit    │ │ • Commands    │
│   extraction  │ │ • Filter rest │ │ • Platforms   │ │   upload      │ │   /start/stop │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘
        │                                   │              │                    │
        └───────────────────────────────────┴──────────────┴────────────────────┘
                                            │
                                            ▼
                              ┌───────────────────────────┐
                              │         MONGODB           │
                              │    (llm_news database)    │
                              │ ├── articles collection   │
                              │ ├── telegram_subscribers  │
                              │ └── pageviews collection  │
                              └─────────────┬─────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
           ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
           │  NEWS WEBSITE │      │ADMIN DASHBOARD│      │  TELEGRAM     │
           │  (Port 3000)  │      │  (Port 3001)  │      │  SUBSCRIBERS  │
           │   Next.js 14  │      │   Next.js 14  │      │  (Bot Users)  │
           └───────────────┘      └───────────────┘      └───────────────┘
```

---

## 🤖 Agent Deep Dive

### 1. Scraper Agent (`agents/scraper_agent.py`)

**Purpose:** Fetches trending news from multiple sources and stores in MongoDB.

| Attribute | Details |
|-----------|---------|
| **Lines of Code** | 422 lines |
| **File Size** | 16.9 KB |
| **Sources** | NewsAPI, GNews |
| **Default Fetch** | 3 from NewsAPI, 2 from GNews |

**Key Methods:**
- `fetch_trending_newsapi(category)` - Fetches top headlines by category
- `fetch_gnews(category, max_articles)` - Fetches from GNews API
- `_process_article(raw_article, api_source)` - Extracts full article content
- `_select_diverse_articles(articles, max_count)` - Ensures source diversity
- `run(newsapi_count, gnews_count, use_trending)` - Main execution method

**Article Processing:**
1. Fetch headlines from APIs
2. Extract full article text using BeautifulSoup
3. Ensure diverse sources (different news agencies)
4. Store with `status: 'raw'` in MongoDB
5. Skip duplicates (unique index on URL)

---

### 2. Orchestrator Agent (`agents/orchestrator_agent.py`)

**Purpose:** The brain of the operation - schedules and coordinates all agents.

| Attribute | Details |
|-----------|---------|
| **Lines of Code** | 351 lines |
| **File Size** | 14.2 KB |
| **Scheduler** | APScheduler (BackgroundScheduler) |
| **Default Interval** | 30 minutes |

**Pipeline Stages:**
```python
def run_pipeline(self):
    1. _run_scraper()      # Fetch news from APIs
    2. _run_ranker()       # LLM-based article selection
    3. _run_curator()      # Summarize, rewrite, platform content
    4. _run_image_generator()  # AI image generation
    5. _run_telegram_broadcaster()  # Broadcast to subscribers
```

**Features:**
- Graceful shutdown via signal handlers (SIGINT, SIGTERM)
- Configurable initial run on start
- Status tracking and metrics
- Error isolation per stage

---

### 3. Article Ranking Agent (`agents/article_ranking_agent.py`)

**Purpose:** Uses LLM to select the most trending/newsworthy article.

| Attribute | Details |
|-----------|---------|
| **Lines of Code** | 232 lines |
| **File Size** | 8.5 KB |
| **LLM** | Groq (Llama 3.3 70B) |
| **Selection** | Top N articles (default: 1) |

**How It Works:**
1. Fetches all `raw` articles from database
2. Builds prompt with article titles and descriptions
3. Asks LLM: "Which article is MOST trending/newsworthy?"
4. Selected articles remain `raw`, others marked `filtered`
5. Only selected articles proceed to curation

**Configuration:**
```yaml
ARTICLE_RANKING:
  ENABLED: true   # Toggle feature on/off
  TOP_N: 1        # Number of best articles to keep
```

---

### 4. Content Curation Agent (`agents/content_curation_agent.py`)

**Purpose:** Processes raw articles through LLM to generate platform-specific content.

| Attribute | Details |
|-----------|---------|
| **Lines of Code** | 575 lines |
| **File Size** | 19.7 KB |
| **LLM** | Groq (Llama 3.3 70B) |
| **Temperature** | 0.7 |
| **Max Tokens** | 2048 |

**Processing Pipeline:**
```
┌────────────────────────────────────────────────────────────────────┐
│                    CONTENT CURATION PIPELINE                        │
├─────────────┬─────────────┬─────────────┬─────────────┬────────────┤
│ Step 1      │ Step 2      │ Step 3      │ Step 4      │ Step 5     │
│ Summarize & │ Extract     │ Generate    │ Platform    │ Update     │
│ Rewrite     │ Entities    │ Hashtags    │ Content     │ Database   │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────┤
│ • 2-3 sent  │ • People    │ • 5-8 tags  │ • Website:  │ • Status:  │
│   summary   │ • Orgs      │ • Trending  │   title,    │   curated  │
│ • Rewritten │ • Locations │ • CamelCase │   3 paras   │ • curated  │
│   3 paras   │             │             │ • Telegram: │   object   │
│             │             │             │   teaser    │ • platforms│
│             │             │             │ • Instagram:│   object   │
│             │             │             │   caption   │            │
└─────────────┴─────────────┴─────────────┴─────────────┴────────────┘
```

**Platform Content Structure:**
```json
{
  "website": {
    "title": "SEO-friendly headline",
    "summary": "Professional summary paragraph",
    "paragraphs": ["para1", "para2", "para3"]
  },
  "telegram": {
    "teaser": "🚀 Catchy teaser with emoji..."
  },
  "instagram": {
    "caption": "📱 Punchy caption...",
    "hashtags": ["#AI", "#TechNews", ...]
  }
}
```

---

### 5. Image Creation Agent (`agents/image_creation_agent.py`)

**Purpose:** Generates AI images for articles using Pollinations.ai API.

| Attribute | Details |
|-----------|---------|
| **Lines of Code** | 808 lines |
| **File Size** | 32.0 KB |
| **Image API** | Pollinations.ai (free, unlimited) |
| **Storage** | ImageKit CDN (20GB free tier) |
| **Models** | turbo, flux, seedream (fallback chain) |

**Image Specifications:**

| Platform | Dimensions | Aspect Ratio | Purpose |
|----------|-----------|--------------|---------|
| **Website** | 1280 × 720 | 16:9 (Landscape) | Hero image |
| **Telegram** | 512 × 512 | 1:1 (Square) | Message preview |
| **Instagram** | 1080 × 1350 | 4:5 (Portrait) | Carousel post |

**Processing Flow:**
```
1. Generate 3 creative prompts using LLM
2. Download Image 1 (Website - landscape)
   → Upload to ImageKit → Get CDN URL
3. Download Image 2 (Telegram - square)
   → Upload to ImageKit → Get CDN URL
4. Download Image 3 (Instagram - portrait)
   → Upload to ImageKit → Get CDN URL
5. Update article with image URLs
6. Mark article status: 'processed'
```

**Retry Mechanism:**
- Max 3 retries per article
- Exponential backoff for rate limits
- Model fallback: turbo → flux → seedream
- Incomplete image sets can be retried

---

### 6. Telegram Bot Agent (`agents/telegram_bot_agent.py`)

**Purpose:** Manages Telegram subscriptions and broadcasts news.

| Attribute | Details |
|-----------|---------|
| **Lines of Code** | 397 lines |
| **File Size** | 14.4 KB |
| **Library** | python-telegram-bot v22.5+ |
| **Mode** | Async (asyncio) |

**Bot Commands:**
| Command | Description |
|---------|-------------|
| `/start` | Subscribe to news updates |
| `/stop` | Unsubscribe from updates |
| `/status` | Check subscription status |

**Broadcast Features:**
- Sends photo + caption with article teaser
- Links to full article on website
- Tracks broadcast status per article
- Rate limiting (0.1s between messages)

**Running Modes:**
```bash
# Command mode - listen for subscriptions
python agents/telegram_bot_agent.py

# Broadcast mode - send pending articles
python agents/telegram_bot_agent.py --broadcast
```

---

## 💾 Database Layer

### MongoDB Manager (`database/mongodb.py`)

| Attribute | Details |
|-----------|---------|
| **Lines of Code** | 466 lines |
| **File Size** | 18.1 KB |
| **Driver** | PyMongo |
| **Database** | `llm_news` |

**Collections:**

| Collection | Purpose |
|------------|---------|
| `articles` | Main article storage |
| `telegram_subscribers` | Bot subscribers |
| `pageviews` | Website analytics |

**Article Status Flow:**
```
raw → curated → generating_images → processed
  ↓
filtered (if not selected by ranker)
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `insert_article(article)` | Store new article |
| `get_raw_articles(limit)` | Fetch unprocessed articles |
| `update_article_curated_content(id, data)` | Add LLM content |
| `update_article_images(id, data)` | Add image URLs |
| `get_articles_to_broadcast(limit)` | Get unbroadcast articles |
| `add_telegram_subscriber(chat_id, username)` | Add subscriber |
| `get_all_telegram_subscribers()` | List all active subs |

---

## 🌐 Frontend Applications

### 1. News Website (`website/`)

| Attribute | Details |
|-----------|---------|
| **Framework** | Next.js 14 (App Router) |
| **Port** | 3000 |
| **React Version** | 19.2.3 |
| **Styling** | Vanilla CSS (Custom design system) |

**File Structure:**
```
website/src/
├── app/
│   ├── page.js              # Homepage
│   ├── layout.js            # Root layout
│   ├── globals.css          # Design system (19.5 KB)
│   ├── about/page.js        # About page
│   ├── article/[id]/        # Article pages
│   └── api/
│       ├── articles/        # GET articles
│       ├── publish/         # POST publish
│       └── track/           # Analytics tracking
├── components/
│   ├── Header.js            # Navigation
│   ├── Footer.js            # Footer
│   ├── HeroSection.js       # Featured article
│   ├── NewsGrid.js          # Article grid
│   ├── ArticleCard.js       # Individual card
│   └── AnalyticsTracker.js  # View tracking
└── lib/
    └── mongodb.js           # DB connection
```

**Design Features:**
- 🌙 Dark mode with purple/indigo gradients
- ✨ Glassmorphism UI with backdrop blur
- 📱 Fully responsive design
- ⚡ Server-side rendering
- 🔄 Auto-refresh every 5 minutes

---

### 2. Admin Dashboard (`admin/`)

| Attribute | Details |
|-----------|---------|
| **Framework** | Next.js 14 |
| **Port** | 3001 |
| **Charts** | Chart.js + react-chartjs-2 |

**Pages:**
```
admin/src/pages/
├── index.js        # Main dashboard (8.5 KB)
├── analytics.js    # Analytics page (17.8 KB)
├── _app.js         # App wrapper
├── _document.js    # HTML document
└── api/
    └── ...         # API routes
```

**Dashboard Features:**
- 📊 Article counts by status (raw, curated, processed, filtered, errors)
- 📰 Article table with filtering
- 🔗 Links to view articles on website or original source
- 📈 Analytics charts (bar charts, pie charts)
- 🏆 Top articles by view count
- 🔄 Auto-refresh every 30 seconds

---

## 🔧 Utilities

### Helper Functions (`utils/helpers.py`)

| Function | Purpose |
|----------|---------|
| `extract_article_text(url, user_agent, timeout)` | Scrape full article content |
| `clean_text(text)` | Sanitize extracted text |
| `parse_datetime(date_string)` | Parse various date formats |

**Text Extraction:**
- Uses BeautifulSoup for HTML parsing
- Extracts all `<p>` tags
- Cleans problematic characters
- Returns None if content < 100 chars

---

## ⚙️ Configuration

### config.yaml Structure

```yaml
# News APIs
NEWS_API_ORG:
  API_KEY: "..."        # NewsAPI.org key

GOOGLE_NEWS:
  API_KEY: "..."        # GNews.io key

# Database
MONGODB:
  CONNECTION_URL: "mongodb+srv://..."
  DATABASE_NAME: "llm_news"
  COLLECTION_NAME: "articles"

# Scraper Settings
SCRAPER:
  USER_AGENT: "Mozilla/5.0..."
  REQUEST_TIMEOUT: 10
  NEWSAPI_COUNT: 3      # Articles per cycle
  GNEWS_COUNT: 2

# Scheduler
SCHEDULER:
  INTERVAL_MINUTES: 30
  RUN_ON_START: true

# LLM (Groq)
LLM:
  PROVIDER: "groq"
  API_KEY: "gsk_..."
  MODEL: "llama-3.3-70b-versatile"
  MAX_TOKENS: 2048
  TEMPERATURE: 0.7

# Content Curation
CONTENT_CURATION:
  BATCH_SIZE: 10
  DELAY_BETWEEN_CALLS: 2  # Rate limiting

# Image Generation
IMAGE_GENERATION:
  ENABLED: true
  OUTPUT_DIR: "generated_images"
  BATCH_SIZE: 10
  DELAY_BETWEEN_CALLS: 1
  WEBSITE:
    WIDTH: 1280
    HEIGHT: 720
  TELEGRAM:
    WIDTH: 512
    HEIGHT: 512
  INSTAGRAM:
    WIDTH: 1080
    HEIGHT: 1350

# ImageKit CDN
IMAGEKIT:
  PRIVATE_KEY: "private_..."
  PUBLIC_KEY: "public_..."
  URL_ENDPOINT: "https://ik.imagekit.io/..."

# Article Ranking
ARTICLE_RANKING:
  ENABLED: true
  TOP_N: 1              # Best articles to keep

# Telegram Bot
TELEGRAM:
  BOT_TOKEN: "..."
  ENABLED: true
  WEBSITE_URL: "https://llm-news-nu.vercel.app"
```

---

## 📦 Dependencies

### Python (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | ≥2.31.0 | HTTP requests |
| `beautifulsoup4` | ≥4.12.0 | HTML parsing |
| `pymongo` | ≥4.6.0 | MongoDB driver |
| `pyyaml` | ≥6.0.0 | YAML parsing |
| `python-dotenv` | ≥1.0.0 | Environment variables |
| `APScheduler` | ≥3.10.0 | Task scheduling |
| `groq` | ≥0.4.0 | Groq LLM client |
| `Pillow` | ≥10.0.0 | Image processing |
| `imagekitio` | ≥5.0.0 | ImageKit SDK |
| `python-telegram-bot` | ≥22.5 | Telegram Bot API |

### Website (`website/package.json`)

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 16.1.1 | React framework |
| `react` | 19.2.3 | UI library |
| `react-dom` | 19.2.3 | DOM rendering |
| `mongodb` | 7.0.0 | Database driver |
| `js-yaml` | 4.1.1 | YAML parsing |

### Admin (`admin/package.json`)

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 16.1.1 | React framework |
| `react` | 19.2.3 | UI library |
| `mongodb` | 7.0.0 | Database driver |
| `chart.js` | 4.5.1 | Charting library |
| `react-chartjs-2` | 5.3.1 | React Chart.js wrapper |

---

## 📊 Article Data Schema

```json
{
  "_id": "ObjectId",
  "source": "BBC News",
  "apiSource": "NewsAPI",
  "title": "Article headline",
  "description": "Brief description",
  "url": "https://original-article-url.com",
  "content": "Full article text...",
  "status": "processed",
  "createdAt": "2026-01-24T12:00:00Z",
  "updatedAt": "2026-01-24T12:15:00Z",
  
  "curated": {
    "summary": "2-3 sentence summary",
    "rewritten_content": "Full rewritten article",
    "entities": {
      "people": ["Elon Musk", "Sam Altman"],
      "organizations": ["OpenAI", "Tesla"],
      "locations": ["San Francisco", "USA"]
    },
    "hashtags": ["#AI", "#Technology", "#Innovation"]
  },
  
  "platforms": {
    "website": {
      "title": "SEO-optimized headline",
      "summary": "Professional summary",
      "paragraphs": ["Para 1...", "Para 2...", "Para 3..."]
    },
    "telegram": {
      "teaser": "🚀 Eye-catching teaser message..."
    },
    "instagram": {
      "caption": "📱 Engaging caption...",
      "hashtags": ["#AI", "#TechNews", "#Innovation"]
    }
  },
  
  "images": {
    "website": {
      "url": "https://ik.imagekit.io/.../article_website.jpg",
      "prompt": "Image generation prompt...",
      "dimensions": { "width": 1280, "height": 720 }
    },
    "telegram": {
      "url": "https://ik.imagekit.io/.../article_telegram.jpg",
      "prompt": "...",
      "dimensions": { "width": 512, "height": 512 }
    },
    "instagram": [
      { "url": "https://ik.imagekit.io/.../article_ig1.jpg", ... },
      { "url": "https://ik.imagekit.io/.../article_ig2.jpg", ... },
      { "url": "https://ik.imagekit.io/.../article_ig3.jpg", ... }
    ]
  },
  
  "image_prompts": ["Prompt 1", "Prompt 2", "Prompt 3"],
  "processed_at": "2026-01-24T12:10:00Z",
  "images_generated_at": "2026-01-24T12:14:00Z",
  "telegram_broadcast": true,
  "telegram_broadcast_at": "2026-01-24T12:16:00Z"
}
```

---

## 🚀 Usage Commands

### Basic Operations

```bash
# Single pipeline run (process once and exit)
python main.py --run-once

# Continuous scheduled mode (default: every 30 min)
python main.py

# Scraper only (legacy mode)
python main.py --scrape-only

# Custom interval
python main.py --interval 15

# Skip initial run on start
python main.py --no-initial-run

# Custom article counts
python main.py --newsapi-count 5 --gnews-count 3

# Verbose logging
python main.py -v
```

### Run Individual Agents

```bash
# Scraper
python agents/scraper_agent.py

# Content Curation
python agents/content_curation_agent.py

# Image Generation
python agents/image_creation_agent.py

# Article Ranking
python agents/article_ranking_agent.py

# Telegram Bot (command mode)
python agents/telegram_bot_agent.py

# Telegram Bot (broadcast mode)
python agents/telegram_bot_agent.py --broadcast
```

### Frontend

```bash
# News Website
cd website && npm install && npm run dev
# Visit: http://localhost:3000

# Admin Dashboard
cd admin && npm install && npm run dev
# Visit: http://localhost:3001
```

---

## 📈 Metrics & Monitoring

### Pipeline Metrics (per run)

| Metric | Description |
|--------|-------------|
| `totalFetched` | Articles fetched from APIs |
| `uniqueSelected` | After source diversity filter |
| `inserted` | New articles stored |
| `duplicates` | Skipped (already in DB) |
| `errors` | Failed to process |
| `processed` | Successfully curated |
| `images_generated` | Images created |
| `broadcast_sent` | Telegram messages sent |
| `duration_seconds` | Total pipeline time |

### Database Stats

Query article counts by status:
```python
db.get_article_count()
# Returns: {'raw': 5, 'curated': 2, 'processed': 15, 'filtered': 8}
```

### Logging

- **Console:** INFO level by default
- **File:** `pipeline.log` (all logs)
- **Scraper:** `scraper.log` (scraper-specific)

---

## 🛣️ Roadmap Status

| Feature | Status |
|---------|--------|
| ✅ Scraper Agent (NewsAPI + GNews) | Complete |
| ✅ Orchestrator Agent (APScheduler) | Complete |
| ✅ Content Curation Agent (Groq LLM) | Complete |
| ✅ Image Generation Agent (Pollinations.ai) | Complete |
| ✅ News Website (Next.js) | Complete |
| ✅ Telegram Bot Integration | Complete |
| ✅ Web Analytics Dashboard | Complete |
| ✅ Article Ranking (LLM-based) | Complete |
| ✅ ImageKit Cloud Storage | Complete |
| ⬜ Instagram Auto-Posting | Planned |

---

## 🔒 Security Notes

> ⚠️ **Important:** The `config.yaml` file contains sensitive credentials. Ensure it's added to `.gitignore` and never committed to version control.

**Sensitive data in config:**
- MongoDB connection string
- NewsAPI key
- GNews API key
- Groq LLM API key
- ImageKit private/public keys
- Telegram bot token

**Recommended:**
- Use `config.yaml.example` as template
- Store credentials in environment variables
- Use secrets management for production

---

## 📁 Full Project Structure

```
e:\LLM News\
├── 📄 main.py                          # Entry point (6.1 KB)
├── 📄 config.yaml                      # Active configuration (2.0 KB)
├── 📄 config.yaml.example              # Template for new users
├── 📄 requirements.txt                 # Python dependencies
├── 📄 README.md                        # Project documentation (13.8 KB)
├── 📄 pipeline.log                     # Execution logs (492 KB)
├── 📄 scraper.log                      # Scraper logs (81 KB)
├── 📄 .gitignore                       # Git exclusions
│
├── 📁 agents/                          # AI Agents
│   ├── 📄 __init__.py
│   ├── 📄 scraper_agent.py             # News fetching (17.0 KB)
│   ├── 📄 orchestrator_agent.py        # Pipeline coordination (14.2 KB)
│   ├── 📄 content_curation_agent.py    # LLM processing (19.7 KB)
│   ├── 📄 image_creation_agent.py      # AI images (32.0 KB)
│   ├── 📄 article_ranking_agent.py     # Trend selection (8.5 KB)
│   └── 📄 telegram_bot_agent.py        # Telegram integration (14.4 KB)
│
├── 📁 database/                        # Data Layer
│   ├── 📄 __init__.py
│   └── 📄 mongodb.py                   # MongoDB manager (18.1 KB)
│
├── 📁 utils/                           # Utilities
│   ├── 📄 __init__.py
│   └── 📄 helpers.py                   # Helper functions (3.1 KB)
│
├── 📁 website/                         # News Website (Next.js)
│   ├── 📄 package.json
│   ├── 📄 next.config.mjs
│   ├── 📁 src/
│   │   ├── 📁 app/                     # App Router
│   │   │   ├── 📄 page.js              # Homepage
│   │   │   ├── 📄 layout.js
│   │   │   ├── 📄 globals.css          # Design system
│   │   │   ├── 📁 about/
│   │   │   ├── 📁 article/[id]/
│   │   │   └── 📁 api/
│   │   ├── 📁 components/              # React components
│   │   │   ├── 📄 Header.js
│   │   │   ├── 📄 Footer.js
│   │   │   ├── 📄 HeroSection.js
│   │   │   ├── 📄 NewsGrid.js
│   │   │   ├── 📄 ArticleCard.js
│   │   │   └── 📄 AnalyticsTracker.js
│   │   └── 📁 lib/
│   │       └── 📄 mongodb.js
│   └── 📁 public/
│
├── 📁 admin/                           # Admin Dashboard (Next.js)
│   ├── 📄 package.json
│   ├── 📁 src/
│   │   ├── 📁 pages/
│   │   │   ├── 📄 index.js             # Dashboard
│   │   │   ├── 📄 analytics.js         # Analytics
│   │   │   └── 📁 api/
│   │   ├── 📁 lib/
│   │   └── 📁 styles/
│   └── 📁 public/
│
├── 📁 generated_images/                # Local image cache
└── 📁 venv/                            # Python virtual environment
```

---

## 📝 Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Python Files** | 9 |
| **Total Python LOC** | ~3,200 lines |
| **Total Agents** | 6 |
| **Frontend Apps** | 2 (website + admin) |
| **External APIs** | 5 (NewsAPI, GNews, Groq, Pollinations, ImageKit) |
| **Database Collections** | 3 |
| **Supported Platforms** | Website, Telegram, Instagram (prepared) |

---

*This report was auto-generated by analyzing the project structure and source code.*
