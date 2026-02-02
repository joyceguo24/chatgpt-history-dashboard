#!/usr/bin/env python3
"""
Parse ChatGPT export HTML and organize Q&A pairs by category and date.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def extract_json_from_html(html_path: str) -> List[Dict[str, Any]]:
    """Extract the jsonData array from the ChatGPT export HTML."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "var jsonData = "
    start_idx = content.find(start_marker)
    if start_idx == -1:
        raise ValueError("Could not find jsonData in HTML file")

    json_start = start_idx + len(start_marker)

    bracket_count = 0
    in_string = False
    escape_next = False
    json_end = json_start

    for i, char in enumerate(content[json_start:], start=json_start):
        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "[":
            bracket_count += 1
        elif char == "]":
            bracket_count -= 1
            if bracket_count == 0:
                json_end = i + 1
                break

    json_str = content[json_start:json_end]
    return json.loads(json_str)


def extract_qa_pairs(conversation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract Q&A pairs from a conversation's message mapping."""
    mapping = conversation.get("mapping", {})
    qa_pairs = []

    messages_by_id = {}
    for msg_id, msg_data in mapping.items():
        if msg_data.get("message"):
            messages_by_id[msg_id] = msg_data

    ordered_messages = []
    for msg_id, msg_data in messages_by_id.items():
        message = msg_data.get("message", {})
        author_role = message.get("author", {}).get("role")
        content = message.get("content", {})
        create_time = message.get("create_time")

        if author_role in ("user", "assistant"):
            parts = content.get("parts", [])
            text_parts = [p for p in parts if isinstance(p, str) and p.strip()]
            if text_parts:
                ordered_messages.append({
                    "role": author_role,
                    "content": "\n".join(text_parts),
                    "create_time": create_time,
                    "id": msg_id
                })

    ordered_messages.sort(key=lambda x: x.get("create_time") or 0)

    current_question = None
    for msg in ordered_messages:
        if msg["role"] == "user":
            current_question = msg
        elif msg["role"] == "assistant" and current_question:
            qa_pairs.append({
                "question": current_question["content"],
                "answer": msg["content"],
                "timestamp": current_question.get("create_time")
            })
            current_question = None

    return qa_pairs


def format_timestamp(timestamp: Optional[float]) -> str:
    """Convert Unix timestamp to readable date string."""
    if not timestamp:
        return "Unknown"
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "Unknown"


def categorize_conversations(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Organize conversations by title (category) and sort by date."""
    categorized = {}

    for conv in conversations:
        title = conv.get("title", "Untitled")
        create_time = conv.get("create_time")
        update_time = conv.get("update_time")

        qa_pairs = extract_qa_pairs(conv)

        if not qa_pairs:
            continue

        category_entry = {
            "title": title,
            "created": format_timestamp(create_time),
            "updated": format_timestamp(update_time),
            "create_timestamp": create_time,
            "qa_pairs": []
        }

        for qa in qa_pairs:
            category_entry["qa_pairs"].append({
                "question": qa["question"],
                "answer": qa["answer"],
                "timestamp": format_timestamp(qa.get("timestamp")),
                "timestamp_raw": qa.get("timestamp")
            })

        category_entry["qa_pairs"].sort(
            key=lambda x: x.get("timestamp_raw") or 0
        )

        if title not in categorized:
            categorized[title] = []
        categorized[title].append(category_entry)

    for title in categorized:
        categorized[title].sort(key=lambda x: x.get("create_timestamp") or 0)

    sorted_categories = dict(
        sorted(
            categorized.items(),
            key=lambda x: min(
                (conv.get("create_timestamp") or 0 for conv in x[1]),
                default=0
            )
        )
    )

    return sorted_categories


def generate_summary(categorized: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary statistics."""
    total_conversations = sum(len(convs) for convs in categorized.values())
    total_qa_pairs = sum(
        len(conv["qa_pairs"])
        for convs in categorized.values()
        for conv in convs
    )

    return {
        "total_categories": len(categorized),
        "total_conversations": total_conversations,
        "total_qa_pairs": total_qa_pairs,
        "categories": list(categorized.keys())
    }


def main():
    html_path = Path(__file__).parent / "chat.html"
    output_path = Path(__file__).parent / "organized_chats.json"

    print(f"Reading {html_path}...")
    conversations = extract_json_from_html(str(html_path))
    print(f"Found {len(conversations)} conversations")

    print("Extracting and categorizing Q&A pairs...")
    categorized = categorize_conversations(conversations)

    summary = generate_summary(categorized)

    output_data = {
        "summary": summary,
        "conversations_by_category": categorized
    }

    print(f"Writing to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Summary:")
    print(f"  Categories: {summary['total_categories']}")
    print(f"  Conversations: {summary['total_conversations']}")
    print(f"  Q&A Pairs: {summary['total_qa_pairs']}")
    print(f"\nOutput saved to: {output_path}")


if __name__ == "__main__":
    main()
