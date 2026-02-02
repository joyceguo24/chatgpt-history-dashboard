#!/usr/bin/env python3
"""
Group Q&A pairs within conversations into topics based on content similarity.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Common stop words to ignore
STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she",
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
    "at", "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just",
    "don", "should", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren",
    "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma", "mightn",
    "mustn", "needn", "shan", "shouldn", "wasn", "weren", "won", "wouldn",
    "could", "would", "might", "must", "shall", "want", "like", "need", "also",
    "get", "got", "make", "made", "know", "think", "say", "said", "see", "look",
    "come", "go", "going", "one", "two", "first", "way", "may", "part", "use",
    "using", "used", "please", "help", "thanks", "thank", "okay", "ok", "yes",
    "yeah", "sure", "right", "well", "good", "great", "really", "actually",
    "basically", "something", "anything", "everything", "nothing", "someone",
    "anyone", "everyone", "thing", "things", "time", "much", "many", "even",
    "still", "back", "being", "trying", "try", "let", "give", "take", "put"
}

# Topic keywords for better naming
TOPIC_KEYWORDS = {
    "code": ["code", "programming", "function", "variable", "debug", "error", "bug", "script"],
    "api": ["api", "endpoint", "request", "response", "http", "rest", "fetch"],
    "design": ["design", "ui", "ux", "layout", "style", "css", "color", "font"],
    "database": ["database", "sql", "query", "table", "data", "schema", "mongodb"],
    "career": ["job", "interview", "resume", "career", "work", "company", "position"],
    "health": ["health", "medical", "symptom", "pain", "medication", "doctor", "treatment"],
    "finance": ["money", "investment", "stock", "price", "budget", "cost", "financial"],
    "writing": ["write", "email", "message", "draft", "letter", "text", "rephrase"],
    "translation": ["translate", "meaning", "chinese", "english", "spanish", "word"],
    "learning": ["learn", "study", "course", "understand", "explain", "concept"],
    "travel": ["travel", "trip", "flight", "hotel", "airport", "vacation"],
    "food": ["food", "recipe", "cook", "restaurant", "meal", "eat", "drink"],
    "relationships": ["relationship", "friend", "date", "love", "feel", "emotion"],
    "project": ["project", "app", "build", "create", "develop", "implement"],
    "advice": ["advice", "recommend", "suggest", "opinion", "think", "should"],
}


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract meaningful keywords from text."""
    if not text:
        return []

    # Lowercase and extract words
    words = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]+\b', text.lower())

    # Filter stop words and short words
    keywords = [
        w for w in words
        if w not in STOP_WORDS and len(w) >= min_length
    ]

    return keywords


def get_keyword_set(qa: Dict[str, Any]) -> Set[str]:
    """Get unique keywords from a Q&A pair."""
    question_keywords = extract_keywords(qa.get("question", ""))
    answer_keywords = extract_keywords(qa.get("answer", ""))[:50]  # Limit answer keywords
    return set(question_keywords + answer_keywords)


def calculate_similarity(keywords1: Set[str], keywords2: Set[str]) -> float:
    """Calculate Jaccard similarity between two keyword sets."""
    if not keywords1 or not keywords2:
        return 0.0

    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)

    return intersection / union if union > 0 else 0.0


def detect_topic_shifts(qa_pairs: List[Dict[str, Any]], threshold: float = 0.05) -> List[int]:
    """Detect indices where topic shifts occur. Very conservative - only split on clear transitions."""
    if len(qa_pairs) <= 3:
        return []  # Don't split very short conversations

    shifts = []
    keyword_sets = [get_keyword_set(qa) for qa in qa_pairs]

    # Build cumulative context for each position
    # This represents "what we've been talking about so far"
    cumulative_contexts = []
    for i in range(len(qa_pairs)):
        # Look back at the last 5 Q&As to build context
        start_idx = max(0, i - 5)
        context = set()
        for j in range(start_idx, i + 1):
            context.update(keyword_sets[j])
        cumulative_contexts.append(context)

    for i in range(1, len(qa_pairs)):
        current_keywords = keyword_sets[i]

        # Compare with immediate previous
        sim_prev = calculate_similarity(keyword_sets[i-1], current_keywords)

        # Compare with cumulative context (what we've been discussing)
        sim_context = calculate_similarity(cumulative_contexts[i-1], current_keywords)

        # Compare with last 3 Q&As individually and take the max
        max_recent_sim = sim_prev
        for j in range(max(0, i-3), i):
            sim = calculate_similarity(keyword_sets[j], current_keywords)
            max_recent_sim = max(max_recent_sim, sim)

        # Use the best similarity score
        best_similarity = max(sim_prev, sim_context * 0.8, max_recent_sim)

        # Only mark as shift if there's almost NO connection
        if best_similarity < threshold:
            # Double-check: is the next Q&A also disconnected from previous context?
            # This prevents single outlier Q&As from creating their own topic
            if i + 1 < len(qa_pairs):
                next_sim_to_current = calculate_similarity(current_keywords, keyword_sets[i+1])
                next_sim_to_prev = calculate_similarity(keyword_sets[i-1], keyword_sets[i+1])
                # If next Q&A connects back to previous context, don't split
                if next_sim_to_prev > threshold * 2:
                    continue
            shifts.append(i)

    return shifts


def generate_topic_name(qa_group: List[Dict[str, Any]], index: int) -> str:
    """Generate a descriptive name for a topic group."""
    # Combine all keywords from the group
    all_keywords = []
    for qa in qa_group:
        all_keywords.extend(extract_keywords(qa.get("question", "")))

    if not all_keywords:
        return f"Discussion {index + 1}"

    # Count keyword frequency
    keyword_counts = Counter(all_keywords)

    # Check against topic categories
    topic_scores = {}
    for topic, topic_words in TOPIC_KEYWORDS.items():
        score = sum(keyword_counts.get(w, 0) for w in topic_words)
        if score > 0:
            topic_scores[topic] = score

    # Get top keywords
    top_keywords = [k for k, v in keyword_counts.most_common(5)]

    # Generate name
    if topic_scores:
        best_topic = max(topic_scores, key=topic_scores.get)
        # Find a distinctive keyword to add
        distinctive = next((k for k in top_keywords if k not in TOPIC_KEYWORDS.get(best_topic, [])), None)
        if distinctive:
            return f"{best_topic.title()}: {distinctive.title()}"
        return best_topic.title()

    # Use top keywords
    if len(top_keywords) >= 2:
        return f"{top_keywords[0].title()} & {top_keywords[1].title()}"
    elif top_keywords:
        return top_keywords[0].title()

    return f"Discussion {index + 1}"


def group_qa_into_topics(qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group Q&A pairs into topics. Conservative approach - prefer fewer, larger topics."""
    if not qa_pairs:
        return []

    # For small conversations, keep as single topic
    if len(qa_pairs) <= 5:
        return [{
            "topic_name": generate_topic_name(qa_pairs, 0),
            "qa_pairs": qa_pairs
        }]

    # Detect topic shifts (very conservative)
    shifts = detect_topic_shifts(qa_pairs)

    # If no shifts detected, keep as single topic
    if not shifts:
        return [{
            "topic_name": generate_topic_name(qa_pairs, 0),
            "qa_pairs": qa_pairs
        }]

    # Group Q&As by topic shifts
    topics = []
    prev_idx = 0

    for shift_idx in shifts:
        if shift_idx > prev_idx:
            group = qa_pairs[prev_idx:shift_idx]
            topics.append({
                "topic_name": generate_topic_name(group, len(topics)),
                "qa_pairs": group
            })
            prev_idx = shift_idx

    # Add remaining Q&As
    if prev_idx < len(qa_pairs):
        group = qa_pairs[prev_idx:]
        topics.append({
            "topic_name": generate_topic_name(group, len(topics)),
            "qa_pairs": group
        })

    # Aggressively merge small topics (less than 3 Q&As) with adjacent ones
    merged_topics = merge_small_topics(topics)

    # If we still have too many topics relative to Q&A count, merge more
    # Aim for roughly 1 topic per 8-10 Q&As minimum
    while len(merged_topics) > 1 and len(qa_pairs) / len(merged_topics) < 5:
        merged_topics = merge_smallest_adjacent_topics(merged_topics)

    return merged_topics


def merge_small_topics(topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge topics with fewer than 3 Q&As into adjacent topics."""
    if len(topics) <= 1:
        return topics

    merged = []
    i = 0

    while i < len(topics):
        current = topics[i]

        # If this topic is small
        if len(current["qa_pairs"]) < 3:
            # Try to merge with previous if exists
            if merged:
                prev = merged[-1]
                # Check similarity
                curr_keywords = set()
                for qa in current["qa_pairs"]:
                    curr_keywords.update(get_keyword_set(qa))
                prev_keywords = set()
                for qa in prev["qa_pairs"]:
                    prev_keywords.update(get_keyword_set(qa))

                # Merge if any connection or if prev is also small
                if calculate_similarity(curr_keywords, prev_keywords) > 0.02 or len(prev["qa_pairs"]) < 3:
                    merged[-1] = {
                        "topic_name": generate_topic_name(prev["qa_pairs"] + current["qa_pairs"], len(merged) - 1),
                        "qa_pairs": prev["qa_pairs"] + current["qa_pairs"]
                    }
                    i += 1
                    continue

            # Try to merge with next if exists
            if i + 1 < len(topics):
                next_topic = topics[i + 1]
                curr_keywords = set()
                for qa in current["qa_pairs"]:
                    curr_keywords.update(get_keyword_set(qa))
                next_keywords = set()
                for qa in next_topic["qa_pairs"]:
                    next_keywords.update(get_keyword_set(qa))

                if calculate_similarity(curr_keywords, next_keywords) > 0.02:
                    # Merge current with next
                    merged.append({
                        "topic_name": generate_topic_name(current["qa_pairs"] + next_topic["qa_pairs"], len(merged)),
                        "qa_pairs": current["qa_pairs"] + next_topic["qa_pairs"]
                    })
                    i += 2
                    continue

        merged.append(current)
        i += 1

    return merged


def merge_smallest_adjacent_topics(topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find and merge the two smallest adjacent topics."""
    if len(topics) <= 1:
        return topics

    # Find the pair of adjacent topics with smallest combined size
    min_size = float('inf')
    merge_idx = 0

    for i in range(len(topics) - 1):
        combined_size = len(topics[i]["qa_pairs"]) + len(topics[i + 1]["qa_pairs"])
        if combined_size < min_size:
            min_size = combined_size
            merge_idx = i

    # Merge the pair
    merged = []
    for i in range(len(topics)):
        if i == merge_idx:
            combined = topics[i]["qa_pairs"] + topics[i + 1]["qa_pairs"]
            merged.append({
                "topic_name": generate_topic_name(combined, len(merged)),
                "qa_pairs": combined
            })
        elif i == merge_idx + 1:
            continue  # Skip, already merged
        else:
            merged.append(topics[i])

    return merged


def process_conversations(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process all conversations and add topic groupings."""
    hierarchy = data.get("hierarchy", {})

    total_topics = 0
    conversations_with_multiple_topics = 0

    for broad_cat, broad_data in hierarchy.items():
        for sub_cat, conversations in broad_data["sub_categories"].items():
            for conv in conversations:
                qa_pairs = conv.get("qa_pairs", [])

                # Group Q&As into topics
                topics = group_qa_into_topics(qa_pairs)
                conv["topics"] = topics

                total_topics += len(topics)
                if len(topics) > 1:
                    conversations_with_multiple_topics += 1

    # Update summary
    data["summary"]["total_topics"] = total_topics
    data["summary"]["conversations_with_multiple_topics"] = conversations_with_multiple_topics

    return data


def main():
    input_path = Path(__file__).parent / "categorized_chats.json"
    output_path = Path(__file__).parent / "categorized_chats_with_topics.json"

    print(f"Reading {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Grouping Q&A pairs into topics...")
    processed_data = process_conversations(data)

    print(f"Writing to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Summary:")
    print(f"  Total Topics: {processed_data['summary']['total_topics']}")
    print(f"  Conversations with Multiple Topics: {processed_data['summary']['conversations_with_multiple_topics']}")
    print(f"\nOutput saved to: {output_path}")

    # Show some examples
    print("\n=== Example Topic Groupings ===")
    count = 0
    for broad_cat, broad_data in processed_data["hierarchy"].items():
        for sub_cat, conversations in broad_data["sub_categories"].items():
            for conv in conversations:
                if len(conv.get("topics", [])) > 1:
                    print(f"\nConversation: {conv['title']}")
                    for i, topic in enumerate(conv["topics"]):
                        print(f"  Topic {i+1}: {topic['topic_name']} ({len(topic['qa_pairs'])} Q&As)")
                    count += 1
                    if count >= 5:
                        break
            if count >= 5:
                break
        if count >= 5:
            break


if __name__ == "__main__":
    main()
