#!/usr/bin/env python3
"""
Classify chat categories into broader groups and create hierarchical structure.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


BROAD_CATEGORIES = {
    "Tech & Development": {
        "keywords": [
            # Programming languages & frameworks
            "code", "programming", "python", "javascript", "typescript", "react",
            "vue", "angular", "flutter", "swift", "kotlin", "java", "c++", "rust",
            "go", "ruby", "php", "node", "django", "flask", "rails", "spring",
            # Web & mobile development
            "api", "rest", "graphql", "git", "github", "gitlab", "app", "web",
            "ios", "android", "mobile", "responsive", "pwa",
            # Database & infrastructure
            "database", "sql", "nosql", "mongodb", "postgres", "mysql", "redis",
            "docker", "kubernetes", "aws", "azure", "gcp", "cloud", "serverless",
            # Frontend
            "html", "css", "sass", "tailwind", "bootstrap", "npm", "webpack",
            "vite", "frontend", "backend", "fullstack",
            # AI & ML
            "tensorflow", "pytorch", "ai", "ml", "machine learning", "llm",
            "chatgpt", "openai", "claude", "gpt", "neural network", "deep learning",
            "nlp", "computer vision", "embeddings", "prompt", "fine-tuning",
            # DevOps & tools
            "deploy", "ci/cd", "pipeline", "dns", "ssl", "nginx", "linux",
            "terminal", "bash", "shell", "cli", "automation", "scripting",
            # General dev
            "debug", "fix", "error", "bug", "refactor", "optimize", "performance",
            "testing", "unit test", "integration", "development", "developer",
            "software", "engineering", "architecture", "microservices",
            "algorithm", "data structure", "tech", "it ", "scraping", "crawler"
        ],
        "patterns": [
            r"\.py$", r"\.js$", r"\.tsx?$", r"code", r"script", r"function",
            r"variable", r"terminal", r"bash", r"setup", r"deploy", r"api",
            r"database", r"server", r"client"
        ]
    },
    "Career & Professional": {
        "keywords": [
            # Job search
            "resume", "cv", "interview", "job", "career", "recruiter", "hiring",
            "job search", "job hunting", "job application", "job offer",
            # Applications
            "cover letter", "application", "portfolio", "references",
            "recommendation", "background check",
            # Education & credentials
            "internship", "apprenticeship", "mba", "degree", "certification",
            "bootcamp", "training program",
            # Industries
            "consulting", "finance", "tech", "healthcare", "marketing",
            "engineering", "design", "sales", "operations",
            # Roles
            "pm", "product manager", "engineer", "analyst", "manager",
            "director", "executive", "founder", "ceo", "cto",
            # Workplace
            "work", "employee", "employer", "team", "colleague", "boss",
            "leadership", "management", "scrum", "agile", "remote work",
            # Compensation
            "offer", "salary", "compensation", "negotiation", "benefits",
            "equity", "bonus", "raise", "promotion",
            # Networking
            "linkedin", "networking", "professional", "conference",
            "mentor", "mentorship", "referral",
            # Entrepreneurship
            "startup", "entrepreneur", "founder", "venture", "vc",
            "pitch", "investor", "funding"
        ],
        "patterns": [
            r"interview", r"resume", r"career", r"job", r"professional",
            r"recruiter", r"hiring", r"intern", r"salary", r"work"
        ]
    },
    "Relationships & Social": {
        "keywords": [
            # Dating
            "flirt", "dating", "date", "match", "swipe", "online dating",
            "first date", "blind date",
            # Relationships
            "relationship", "boyfriend", "girlfriend", "partner", "spouse",
            "husband", "wife", "couple", "significant other",
            # Romance
            "love", "romantic", "romance", "attraction", "chemistry", "crush",
            "affection", "intimacy",
            # Life events
            "marriage", "wedding", "engagement", "anniversary", "breakup",
            "divorce", "separation",
            # Social
            "communication", "feelings", "emotional", "friend", "friendship",
            "social", "family", "parents", "siblings", "relatives",
            # Occasions
            "birthday", "holiday", "celebration", "party", "gathering",
            "reunion", "valentine",
            # Social media
            "caption", "instagram", "facebook", "twitter", "tiktok", "post",
            "social media",
            # Communication
            "response", "reply", "text", "message", "conversation", "chat",
            "dms", "reconnect", "catch up"
        ],
        "patterns": [
            r"flirt", r"dating", r"relationship", r"romantic", r"love",
            r"caption", r"response", r"reply", r"friend", r"family"
        ]
    },
    "Health & Wellness": {
        "keywords": [
            # Medical general
            "health", "medical", "doctor", "physician", "nurse", "hospital",
            "clinic", "healthcare", "patient", "appointment", "checkup",
            # Conditions & symptoms
            "symptom", "pain", "sick", "illness", "disease", "condition",
            "injury", "infection", "fever", "headache", "fatigue",
            # Treatment
            "treatment", "diagnosis", "therapy", "surgery", "procedure",
            "medication", "prescription", "medicine", "recovery", "healing",
            # Fitness
            "exercise", "workout", "gym", "fitness", "training", "cardio",
            "strength", "muscle", "stretching", "yoga", "pilates", "running",
            "swimming", "sports", "athletic",
            # Nutrition
            "diet", "nutrition", "meal plan", "calorie", "protein", "carbs",
            "fats", "macros", "supplement", "vitamin", "mineral", "hydration",
            # Mental health
            "mental health", "anxiety", "depression", "stress", "burnout",
            "therapy", "counseling", "psychologist", "psychiatrist",
            "mindfulness", "self-care",
            # Sleep & lifestyle
            "sleep", "insomnia", "rest", "energy", "wellness", "balance",
            "healthy lifestyle", "prevention", "immune system",
            # Body
            "weight", "bmi", "body", "posture", "flexibility", "mobility"
        ],
        "patterns": [
            r"health", r"medical", r"symptom", r"treatment", r"workout",
            r"fitness", r"diet", r"mental", r"wellness", r"exercise"
        ]
    },
    "Finance & Business": {
        "keywords": [
            # Personal finance
            "money", "finance", "budget", "expense", "saving", "spending",
            "income", "debt", "loan", "mortgage", "credit", "credit card",
            # Investing
            "investment", "invest", "stock", "bond", "etf", "mutual fund",
            "portfolio", "dividend", "returns", "compound interest",
            # Trading
            "trading", "market", "bull", "bear", "volatility", "options",
            "futures", "forex",
            # Crypto
            "crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain",
            "defi", "nft", "web3",
            # Business
            "business", "company", "corporation", "llc", "partnership",
            "entrepreneur", "startup", "small business",
            # Business operations
            "revenue", "profit", "loss", "margin", "cash flow", "balance sheet",
            "income statement", "accounting", "bookkeeping",
            # Taxes
            "tax", "taxes", "deduction", "refund", "filing",
            # Economics
            "economy", "inflation", "interest rate", "gdp", "recession",
            "economic", "monetary policy",
            # Transactions
            "price", "cost", "payment", "transaction", "purchase", "sale",
            "subscription", "pricing", "discount", "wholesale", "retail",
            # Financial planning
            "financial", "roi", "growth", "wealth", "retirement",
            "pension", "insurance"
        ],
        "patterns": [
            r"finance", r"invest", r"stock", r"money", r"business",
            r"market", r"price", r"cost", r"budget", r"tax", r"crypto"
        ]
    },
    "Language & Translation": {
        "keywords": [
            # Translation
            "translate", "translation", "translator", "interpret", "localize",
            "localization",
            # Languages
            "chinese", "english", "spanish", "french", "german", "italian",
            "portuguese", "japanese", "korean", "arabic", "russian", "hindi",
            "cantonese", "mandarin", "vietnamese", "thai", "dutch", "swedish",
            # Language learning
            "language", "bilingual", "multilingual", "fluent", "fluency",
            "vocabulary", "grammar", "pronunciation", "accent", "dialect",
            # Linguistics
            "meaning", "definition", "phrase", "idiom", "slang", "word",
            "expression", "colloquial", "formal", "informal",
            # Tools & resources
            "dictionary", "thesaurus", "language app", "flashcard",
            "immersion", "practice", "conversation partner",
            # Characters
            "翻译", "中文", "英文", "字", "词",
            # Concepts
            "terminology", "clarification", "sentence", "paragraph",
            "context", "nuance", "connotation", "literal", "figurative"
        ],
        "patterns": [
            r"翻译", r"中文", r"meaning", r"translate", r"definition",
            r"什么", r"解释", r"英文", r"language", r"词"
        ]
    },
    "Creative & Entertainment": {
        "keywords": [
            # Music
            "music", "song", "album", "artist", "band", "concert", "playlist",
            "genre", "melody", "rhythm", "lyrics", "singing", "instrument",
            # Visual arts
            "art", "artist", "painting", "drawing", "illustration", "sketch",
            "sculpture", "gallery", "museum", "exhibition",
            # Design
            "design", "graphic design", "ui design", "ux design", "logo",
            "branding", "typography", "color", "aesthetic",
            # Photography & video
            "photo", "photography", "camera", "video", "film", "filmmaking",
            "editing", "cinematography", "animation", "vfx",
            # Entertainment
            "movie", "tv show", "series", "streaming", "netflix", "youtube",
            "podcast", "entertainment", "media",
            # Gaming
            "game", "gaming", "video game", "esports", "streamer", "twitch",
            # Writing
            "creative writing", "story", "novel", "fiction", "poetry", "poem",
            "screenplay", "script", "narrative",
            # Events
            "dance", "party", "event", "festival", "performance", "show",
            "theater", "comedy", "standup",
            # Social content
            "caption", "content", "creator", "influencer", "viral"
        ],
        "patterns": [
            r"music", r"song", r"art", r"creative", r"design", r"video",
            r"caption", r"entertainment", r"film", r"game", r"photo"
        ]
    },
    "Learning & Education": {
        "keywords": [
            # Education
            "learn", "learning", "education", "educational", "academic",
            "student", "teacher", "professor", "instructor",
            # Institutions
            "school", "college", "university", "academy", "institute",
            "online course", "mooc", "bootcamp",
            # Activities
            "course", "class", "lecture", "seminar", "workshop", "study",
            "homework", "assignment", "project", "thesis", "dissertation",
            # Assessment
            "exam", "test", "quiz", "grade", "gpa", "assessment", "evaluation",
            # Learning materials
            "tutorial", "guide", "textbook", "resource", "curriculum",
            "syllabus", "lesson", "module",
            # Comprehension
            "explanation", "understand", "concept", "theory", "principle",
            "framework", "model", "methodology",
            # Subjects
            "science", "math", "mathematics", "physics", "chemistry", "biology",
            "history", "geography", "literature", "philosophy", "psychology",
            "sociology", "economics", "political science", "law",
            # Skills
            "skill", "knowledge", "expertise", "competency", "proficiency",
            "certification", "credential",
            # Research
            "research", "study", "paper", "journal", "academic writing"
        ],
        "patterns": [
            r"learn", r"education", r"course", r"explain", r"understand",
            r"theory", r"concept", r"lecture", r"study", r"school"
        ]
    },
    "Food & Cooking": {
        "keywords": [
            # Cooking
            "food", "cook", "cooking", "bake", "baking", "grill", "roast",
            "fry", "steam", "boil", "kitchen", "chef", "homemade",
            # Recipes
            "recipe", "ingredient", "dish", "cuisine", "flavor", "seasoning",
            "spice", "herb", "sauce", "marinade",
            # Meals
            "meal", "dinner", "lunch", "breakfast", "brunch", "snack",
            "appetizer", "entree", "dessert", "side dish",
            # Dining
            "restaurant", "cafe", "bistro", "diner", "takeout", "delivery",
            "reservation", "menu", "order",
            # Drinks
            "drink", "beverage", "cocktail", "wine", "beer", "coffee", "tea",
            "juice", "smoothie", "mocktail",
            # Food types
            "meat", "beef", "pork", "chicken", "fish", "seafood", "vegetable",
            "fruit", "grain", "pasta", "rice", "bread", "salad", "soup",
            # Dietary
            "vegetarian", "vegan", "gluten-free", "dairy-free", "keto",
            "paleo", "organic", "healthy eating",
            # Cuisines
            "italian", "chinese", "mexican", "japanese", "indian", "thai",
            "french", "korean", "mediterranean", "american"
        ],
        "patterns": [
            r"food", r"cook", r"recipe", r"meal", r"restaurant", r"drink",
            r"kitchen", r"ingredient", r"dish", r"cuisine"
        ]
    },
    "Product & Ideas": {
        "keywords": [
            # Ideation
            "idea", "concept", "innovation", "brainstorm", "creative thinking",
            "problem solving", "solution", "inspiration",
            # Product development
            "product", "feature", "functionality", "capability", "enhancement",
            "improvement", "iteration", "version",
            # Design process
            "design", "prototype", "mockup", "wireframe", "sketch", "draft",
            "ux", "ui", "user experience", "user interface",
            # Planning
            "proposal", "suggestion", "recommendation", "plan", "strategy",
            "roadmap", "timeline", "milestone",
            # Documentation
            "mvp", "prd", "requirement", "spec", "specification",
            "documentation", "user story", "use case",
            # Feedback
            "feedback", "review", "critique", "evaluation", "validation",
            "user testing", "usability",
            # Business
            "market fit", "value proposition", "competitive analysis",
            "target audience", "user persona",
            # Technology
            "app idea", "software", "platform", "tool", "service",
            "saas", "hardware", "device", "wearable", "iot"
        ],
        "patterns": [
            r"idea", r"product", r"feature", r"concept", r"innovation",
            r"design", r"prototype", r"strategy", r"mvp", r"ux"
        ]
    },
    "Travel & Lifestyle": {
        "keywords": [
            # Travel
            "travel", "trip", "vacation", "holiday", "getaway", "adventure",
            "explore", "tourism", "tourist", "traveler",
            # Transportation
            "flight", "airplane", "airport", "airline", "train", "bus",
            "car rental", "road trip", "cruise", "ferry",
            # Accommodation
            "hotel", "hostel", "airbnb", "resort", "motel", "booking",
            "reservation", "check-in", "check-out",
            # Destinations
            "destination", "city", "country", "beach", "mountain", "island",
            "national park", "landmark", "attraction",
            # Planning
            "itinerary", "schedule", "plan", "route", "guide", "map",
            "visa", "passport", "luggage", "packing",
            # Activities
            "sightseeing", "tour", "excursion", "hiking", "camping",
            "beach day", "museum visit", "local food",
            # Lifestyle
            "lifestyle", "living", "routine", "daily life", "work-life balance",
            # Home
            "home", "house", "apartment", "condo", "rent", "move", "moving",
            "furniture", "decor", "interior design", "organization",
            # Shopping
            "shopping", "purchase", "buy", "store", "mall", "online shopping",
            "deal", "sale", "discount"
        ],
        "patterns": [
            r"travel", r"trip", r"flight", r"hotel", r"vacation",
            r"destination", r"home", r"lifestyle", r"shopping"
        ]
    },
    "Personal & Reflection": {
        "keywords": [
            # Self-reflection
            "personal", "reflection", "introspection", "self-awareness",
            "self-discovery", "identity", "values", "beliefs",
            # Journaling
            "journal", "diary", "writing", "thoughts", "feelings",
            "emotions", "expression",
            # Goals
            "goal", "objective", "aspiration", "dream", "ambition",
            "resolution", "intention", "purpose",
            # Growth
            "growth", "development", "improvement", "progress", "change",
            "transformation", "evolution", "journey",
            # Motivation
            "motivation", "inspiration", "drive", "passion", "enthusiasm",
            "determination", "perseverance", "resilience",
            # Mindset
            "mindset", "attitude", "perspective", "outlook", "optimism",
            "positivity", "gratitude", "appreciation",
            # Habits
            "habit", "routine", "discipline", "consistency", "commitment",
            "accountability", "productivity",
            # Life
            "life", "lifestyle", "balance", "fulfillment", "happiness",
            "satisfaction", "meaning", "purpose",
            # Decision making
            "decision", "choice", "dilemma", "priority", "trade-off",
            "pros and cons", "advice", "guidance",
            # Spirituality
            "spiritual", "meditation", "mindfulness", "peace", "calm",
            "inner peace", "self-care", "well-being"
        ],
        "patterns": [
            r"personal", r"reflection", r"journal", r"self", r"life",
            r"goal", r"motivation", r"advice", r"growth", r"mindset"
        ]
    },
    "Communication & Email": {
        "keywords": [
            # Email
            "email", "inbox", "subject line", "signature", "cc", "bcc",
            "forward", "reply all", "attachment",
            # Writing
            "message", "letter", "memo", "note", "draft", "write", "compose",
            "correspondence", "communication",
            # Editing
            "rephrase", "rewrite", "refine", "polish", "edit", "proofread",
            "revise", "improve", "enhance",
            # Formatting
            "summarize", "summary", "bullet point", "outline", "format",
            "structure", "organize", "condense",
            # Style
            "tone", "voice", "formal", "informal", "professional", "casual",
            "friendly", "concise", "clear",
            # Types
            "one-liner", "punchy", "shorten", "brief", "detailed", "elaborate",
            # Content
            "post", "article", "blog", "content", "copy", "copywriting",
            # Feedback
            "phrasing", "wording", "tips", "suggestion", "feedback",
            "review", "critique",
            # Requests
            "request", "inquiry", "follow-up", "reminder", "thank you",
            "apology", "announcement", "invitation",
            # Professional
            "business writing", "technical writing", "report", "proposal",
            "presentation", "pitch", "executive summary"
        ],
        "patterns": [
            r"email", r"message", r"draft", r"write", r"rephrase",
            r"refine", r"summarize", r"tone", r"formal", r"letter"
        ]
    },
    "Data & Research": {
        "keywords": [
            # Data
            "data", "dataset", "database", "big data", "data science",
            "data analysis", "data visualization", "analytics",
            # Research
            "research", "study", "investigation", "inquiry", "exploration",
            "experiment", "methodology", "findings",
            # Reports
            "report", "paper", "publication", "documentation", "whitepaper",
            "case study", "analysis report",
            # Statistics
            "statistics", "statistical", "quantitative", "qualitative",
            "sample", "population", "correlation", "regression",
            # Visualization
            "chart", "graph", "plot", "diagram", "infographic", "dashboard",
            "visualization", "visual",
            # Metrics
            "metrics", "kpi", "indicator", "measure", "benchmark", "trend",
            "pattern", "insight",
            # Collection
            "survey", "questionnaire", "interview", "poll", "census",
            "data collection", "sampling",
            # Processing
            "extract", "extraction", "transform", "clean", "process",
            "aggregate", "filter", "query",
            # Tools
            "excel", "spreadsheet", "tableau", "power bi", "sql",
            "pandas", "numpy", "r", "spss"
        ],
        "patterns": [
            r"data", r"research", r"analysis", r"report", r"study",
            r"statistic", r"chart", r"graph", r"metric", r"survey"
        ]
    },
    "Fun & Miscellaneous": {
        "keywords": [
            # Fun
            "fun", "funny", "humor", "laugh", "entertainment", "amusing",
            "playful", "lighthearted",
            # Jokes
            "joke", "pun", "riddle", "comedy", "meme", "viral", "trending",
            # Random
            "random", "miscellaneous", "other", "general", "various",
            "mixed", "assorted",
            # Games
            "game", "puzzle", "trivia", "quiz", "challenge", "brain teaser",
            "word game", "guessing game",
            # Hobbies
            "hobby", "pastime", "leisure", "recreation", "interest",
            "collection", "craft", "diy",
            # Pets
            "pet", "cat", "dog", "animal", "puppy", "kitten", "bird", "fish",
            # Social
            "emoji", "gif", "sticker", "reaction", "trend",
            # Curiosity
            "curious", "interesting", "fascinating", "weird", "unusual",
            "fact", "trivia", "did you know",
            # Celebration
            "celebrate", "party", "event", "occasion", "festive"
        ],
        "patterns": [
            r"fun", r"random", r"joke", r"trivia", r"hobby", r"pet",
            r"game", r"meme", r"emoji"
        ]
    }
}


def classify_category(title: str) -> Tuple[str, float]:
    """Classify a category title into a broad category with confidence score."""
    title_lower = title.lower()
    scores = {}

    for broad_cat, rules in BROAD_CATEGORIES.items():
        score = 0

        for keyword in rules["keywords"]:
            if keyword.lower() in title_lower:
                score += 2
                if title_lower.startswith(keyword.lower()):
                    score += 1

        for pattern in rules["patterns"]:
            if re.search(pattern, title_lower, re.IGNORECASE):
                score += 1

        scores[broad_cat] = score

    if max(scores.values()) == 0:
        return "Miscellaneous", 0.0

    best_category = max(scores, key=scores.get)
    confidence = scores[best_category] / (sum(scores.values()) + 1)

    return best_category, confidence


def reorganize_data(original_data: Dict[str, Any]) -> Dict[str, Any]:
    """Reorganize data into hierarchical structure."""
    conversations_by_category = original_data.get("conversations_by_category", {})

    hierarchical = {}
    classification_map = {}

    for sub_category, conversations in conversations_by_category.items():
        broad_category, confidence = classify_category(sub_category)
        classification_map[sub_category] = {
            "broad_category": broad_category,
            "confidence": confidence
        }

        if broad_category not in hierarchical:
            hierarchical[broad_category] = {
                "sub_categories": {},
                "total_conversations": 0,
                "total_qa_pairs": 0
            }

        hierarchical[broad_category]["sub_categories"][sub_category] = conversations

        hierarchical[broad_category]["total_conversations"] += len(conversations)
        hierarchical[broad_category]["total_qa_pairs"] += sum(
            len(conv.get("qa_pairs", [])) for conv in conversations
        )

    sorted_hierarchical = dict(
        sorted(
            hierarchical.items(),
            key=lambda x: x[1]["total_qa_pairs"],
            reverse=True
        )
    )

    for broad_cat in sorted_hierarchical:
        sorted_hierarchical[broad_cat]["sub_categories"] = dict(
            sorted(
                sorted_hierarchical[broad_cat]["sub_categories"].items(),
                key=lambda x: sum(
                    len(conv.get("qa_pairs", [])) for conv in x[1]
                ),
                reverse=True
            )
        )

    summary = {
        "total_broad_categories": len(sorted_hierarchical),
        "total_sub_categories": len(conversations_by_category),
        "total_conversations": original_data.get("summary", {}).get("total_conversations", 0),
        "total_qa_pairs": original_data.get("summary", {}).get("total_qa_pairs", 0),
        "broad_categories": [
            {
                "name": cat,
                "sub_categories_count": len(data["sub_categories"]),
                "conversations_count": data["total_conversations"],
                "qa_pairs_count": data["total_qa_pairs"]
            }
            for cat, data in sorted_hierarchical.items()
        ]
    }

    return {
        "summary": summary,
        "hierarchy": sorted_hierarchical,
        "classification_map": classification_map
    }


def main():
    input_path = Path(__file__).parent / "organized_chats.json"
    output_path = Path(__file__).parent / "categorized_chats.json"

    print(f"Reading {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    print("Classifying and reorganizing data...")
    reorganized = reorganize_data(original_data)

    print(f"Writing to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reorganized, f, indent=2, ensure_ascii=False)

    print("\nDone! Summary:")
    print(f"  Broad Categories: {reorganized['summary']['total_broad_categories']}")
    print(f"  Sub-Categories: {reorganized['summary']['total_sub_categories']}")
    print(f"  Total Q&A Pairs: {reorganized['summary']['total_qa_pairs']}")

    print("\nBreakdown by broad category:")
    for cat_info in reorganized["summary"]["broad_categories"]:
        print(f"  {cat_info['name']}: {cat_info['sub_categories_count']} sub-categories, "
              f"{cat_info['qa_pairs_count']} Q&A pairs")

    print(f"\nOutput saved to: {output_path}")


if __name__ == "__main__":
    main()
