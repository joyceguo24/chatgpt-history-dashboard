# ChatGPT History Dashboard

A tool to parse, organize, and visualize your ChatGPT conversation history with a clean, searchable dashboard.

![Dashboard Preview](https://img.shields.io/badge/UI-Dark%20Theme-1a1a1a) ![Python](https://img.shields.io/badge/Python-3.7%2B-blue) ![Dependencies](https://img.shields.io/badge/Dependencies-None-green)

## Features

- **Hierarchical Organization** - Conversations grouped into broad categories (Tech, Career, Health, etc.)
- **Automatic Topic Detection** - Q&A pairs within conversations are grouped by content similarity
- **Searchable Dashboard** - IDE-style sidebar with expandable folders and full-text search
- **Collapsible Topics** - Click to expand/collapse topic sections
- **Dark Theme** - ChatGPT-style interface
- **Privacy First** - All processing happens locally, no data sent anywhere

---

## Quick Start

### Step 1: Export Your ChatGPT Data

1. Go to [chat.openai.com](https://chat.openai.com)
2. Click your **profile icon** (bottom left)
3. Go to **Settings** → **Data controls**
4. Click **Export data** → **Confirm export**
5. Wait for email, then download the zip file
6. Extract the zip and locate the `chat.html` file

### Step 2: Process Your Data

```bash
# Clone or download this project
cd gpt_demo

# Run with your chat.html file
python run.py /path/to/your/chat.html

# Or place chat.html in this folder and run
python run.py
```

### Step 3: View the Dashboard

```bash
# Start a local server
python -m http.server 8080
```

Open your browser to: **http://localhost:8080/dashboard.html**

---

## Project Structure

```
gpt_demo/
├── run.py                   # Main entry point - runs the full pipeline
├── parse_chat.py            # Step 1: Parse ChatGPT HTML export
├── classify_categories.py   # Step 2: Classify into broad categories
├── group_topics.py          # Step 3: Group Q&As into topics
├── dashboard.html           # Web dashboard (single HTML file)
└── README.md                # This file
```

### Generated Files (after running)

```
gpt_demo/
├── organized_chats.json              # Flat Q&A pairs by conversation
├── categorized_chats.json            # Hierarchical with broad categories
└── categorized_chats_with_topics.json # Final data with topics (used by dashboard)
```

---

## How It Works

### Pipeline Overview

```
chat.html → parse_chat.py → classify_categories.py → group_topics.py → dashboard.html
    │              │                  │                    │                │
    │              │                  │                    │                │
    ▼              ▼                  ▼                    ▼                ▼
 ChatGPT      Extract Q&A       Classify into        Group Q&As       Display in
  Export        pairs          16 categories        into topics        browser
```

### Step 1: `parse_chat.py`

Extracts the embedded JSON data from ChatGPT's HTML export and organizes Q&A pairs:

- Parses the `jsonData` variable from `chat.html`
- Extracts user questions and assistant answers
- Preserves timestamps and conversation metadata
- Outputs: `organized_chats.json`

### Step 2: `classify_categories.py`

Classifies conversations into broad categories using keyword matching:

**16 Built-in Categories:**
| Category | Examples |
|----------|----------|
| Tech & Development | code, api, git, react, python |
| Career & Professional | resume, interview, job, mba |
| Health & Wellness | medical, symptom, workout, diet |
| Finance & Business | investment, stock, budget, tax |
| Language & Translation | translate, meaning, chinese |
| Creative & Entertainment | music, art, design, video |
| Learning & Education | course, study, concept, theory |
| Communication & Email | email, draft, rephrase, summarize |
| Relationships & Social | dating, friend, conversation |
| Food & Cooking | recipe, restaurant, meal |
| Travel & Lifestyle | flight, hotel, vacation |
| Personal & Reflection | journal, advice, motivation |
| Product & Ideas | product, feature, prototype |
| Data & Research | data, research, analysis |
| Fun & Miscellaneous | games, puzzles, random |
| Miscellaneous | uncategorized items |

- Outputs: `categorized_chats.json`

### Step 3: `group_topics.py`

Groups Q&A pairs within each conversation into topics:

- Uses keyword extraction and Jaccard similarity
- Conservative approach - only splits on clear topic transitions
- Merges small topics to avoid fragmentation
- Generates descriptive topic names from keywords
- Outputs: `categorized_chats_with_topics.json`

### Step 4: `dashboard.html`

Single-file web dashboard with:

- Sidebar with expandable folder tree
- Full-text search across all conversations
- Topic sections (collapsed by default)
- Q&A display with user/assistant styling
- Conversation metadata (date, topic count, Q&A count)

---

## Data Structure

The final JSON has this hierarchy:

```
{
  "summary": {
    "total_broad_categories": 16,
    "total_sub_categories": 423,
    "total_conversations": 430,
    "total_qa_pairs": 5505,
    "total_topics": 913
  },
  "hierarchy": {
    "Tech & Development": {
      "sub_categories": {
        "React Native Setup": [
          {
            "title": "React Native Setup",
            "created": "2024-01-15 10:30:00",
            "updated": "2024-01-15 11:45:00",
            "topics": [
              {
                "topic_name": "Project & Configuration",
                "qa_pairs": [
                  {
                    "question": "How do I set up React Native?",
                    "answer": "To set up React Native...",
                    "timestamp": "2024-01-15 10:30:15"
                  }
                ]
              }
            ]
          }
        ]
      },
      "total_conversations": 85,
      "total_qa_pairs": 1545
    }
  }
}
```

---

## Customization

### Adding/Modifying Categories

Edit `classify_categories.py` and modify the `BROAD_CATEGORIES` dictionary:

```python
BROAD_CATEGORIES = {
    "Your New Category": {
        "keywords": ["keyword1", "keyword2", "keyword3"],
        "patterns": [r"regex_pattern1", r"regex_pattern2"]
    },
    # ... existing categories
}
```

### Adjusting Topic Sensitivity

Edit `group_topics.py`:

```python
# In detect_topic_shifts() - lower = fewer topics
threshold: float = 0.05  # Default: 0.05

# Minimum Q&As before attempting to split
if len(qa_pairs) <= 5:  # Change this number
    return [single_topic]
```

### Changing Dashboard Appearance

Edit `dashboard.html` CSS variables:

```css
:root {
  --bg-primary: #212121;      /* Main background */
  --bg-secondary: #171717;    /* Sidebar background */
  --accent-color: #10a37f;    /* Highlight color */
  --text-primary: #ececec;    /* Main text */
}
```

---

## Requirements

- **Python 3.7+**
- No external dependencies (uses only standard library)
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## Troubleshooting

### "No chat.html found"

Make sure you:
1. Exported data from ChatGPT (Settings → Data controls → Export)
2. Extracted the zip file
3. Provided the correct path to `chat.html`

### "Could not find jsonData in HTML file"

The ChatGPT export format may have changed. Check that your `chat.html` contains a `var jsonData = [...]` section.

### Dashboard shows "Error loading data"

Make sure you're running a local server (`python -m http.server 8080`) and not opening the HTML file directly. Browsers block local file access for security.

### Topics are too granular/too broad

Adjust the `threshold` value in `group_topics.py`:
- Higher threshold (e.g., 0.1) = more topics
- Lower threshold (e.g., 0.02) = fewer topics

---

## Privacy

- All processing happens **locally** on your machine
- No data is sent to any external server
- No API keys or authentication required
- You can delete generated JSON files anytime

---

## License

MIT License - feel free to modify and use as you wish.
