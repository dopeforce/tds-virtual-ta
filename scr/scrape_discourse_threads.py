#!/usr/bin/env python3
"""
scrape_discourse_threads.py

Efficiently download all threads (with full post history) from a specified Discourse category within a date range.

Features:
- Fetches all topics in a category between --start-date and --end-date (inclusive).
- Retrieves all posts for each topic, handling Discourse pagination automatically.
- Supports authentication via API key/username or session cookies.
- Saves each thread (with all posts) as a JSON file in the specified output directory.

Usage:
    python scrape_discourse_threads.py \
        --base-url      "https://discourse.example.com" \
        --category-path "category/slug/123" \
        --start-date    "YYYY-MM-DD" \
        --end-date      "YYYY-MM-DD" \
        --output-dir    "output_directory" \
        [--api-key KEY --api-username USER] \
        [--cookies "name=value; ..."]

Arguments:
    --base-url        Root URL of the Discourse forum (e.g., https://discourse.example.com)
    --category-path   Path to the category (e.g., category/slug/123)
    --start-date      Start date (YYYY-MM-DD)
    --end-date        End date (YYYY-MM-DD)
    --output-dir      Directory to save thread JSON files
    --api-key         (Optional) Discourse API key for authentication
    --api-username    (Optional) Discourse API username
    --cookies         (Optional) Session cookies string for authentication

Examples:
    # Using API key and username
    python scrape_discourse_threads.py \
        --base-url "https://discourse.onlinedegree.iitm.ac.in" \
        --category-path "courses/tds-kb/34" \
        --start-date "2025-05-01" \
        --end-date "2025-05-10" \
        --output-dir "res/discourse_threads" \
        --api-key "your_api_key" \
        --api-username "your_username"

    # Using browser session cookies
    python scrape_discourse_threads.py \
        --base-url "https://discourse.onlinedegree.iitm.ac.in" \
        --category-path "courses/tds-kb/34" \
        --start-date "2025-05-01" \
        --end-date "2025-05-10" \
        --output-dir "res/discourse_threads" \
        --cookies "_gcl_au=1.1.255314418.1748771388; _ga=GA1.1.1357929948.1748771389; _fbp=fb.2.1748771388906.252972226954069369; _ga_5HTJMW67XK=GS2.1.s1750080989$o8$g0$t1750080998$j51$l0$h0; _ga_08NPRH5L4M=GS2.1.s1750080989$o14$g1$t1750081995$j58$l0$h0; _t=K%2BYiQubBYihwv8c8TgL2qygJBiIVYOSLeovoLZGeVjZPftT7hH6gcaNHwsQ0GpAGfg8hRrmf7UhUu11rcLpGT6%2FvsFO3Tz7%2BSXJX4Of5UaQdOt6ICBuxDCwsFgMzfK%2FiUbLWI7d2ODaDOfEQBlUcqmTETicwA%2BgLvuP1vs%2Bdk63AlPS0Hlz4LwDzDwIDg%2FI1kKiECalSPOY%2Fd0TdPKviOLdMEz%2BT6w2CcxYvgYbcBiJH7Oj1tlBslJKdbo83jaa5CpjwLtQCoUPEI54h31MrwIudFtun%2FSd4t%2Bhvy0SPJfeTbDC7oYbqMiJ%2BSL9xZG3t--nc6X1%2Flveqc8sWkD--Ie1VM98ZKYcRBfkkLwsXCw%3D%3D; _forum_session=2B2VSHb5aidNAUc3J%2BS36w5b%2F3vS0QXqPeD9fTacDbLh2o55xxXPqvAPaKsKjqIikgRXl7ICAoORAvCb5%2BtHwC2dTFrNduutRTEZ7%2Bqwl7A4PpdJ27WXUU1ZAMPUe6HDZinHCKX%2F3tOYu8hvebX%2BZdG2JPjU0avxEYFoOISNINYJlr44KeMSXIJtRRcUC6F43KhuSt%2BLdWy2IP259BZEiLDuMgEpamI0IncgvxLpxThXLqsWccMDZJojCO2aIVaErR2ALVFxHVa3xD%2FLeI9Ps%2FOf9x4D%2BmHiFEWWNFdVQHEMTBgWKkRk6mLvqiUrzDuywnRzV2M%2Bl%2FVPlxxxPifjT5c8myAj3ORirrIUSpa52Tsni71vDupcoV1q%2BUXIbdopWQz1suobybpMaTJsWpkCun5f5zOvRL%2BSfGSuWy0E--l%2Fu%2FqBGvugLLUE0%2B--QwvJy2HVbWWi3L22o5%2BALA%3D%3D"

Notes:
- Requires Python 3.7+ and the 'requests' library.
- Handles rate limits and retries automatically.
- Output files are named as <topic_id>.json in the output directory.
"""

import os
import json
import argparse
import requests

from math import ceil
from datetime import datetime, timezone
from dateutil import parser as date_parser

def parse_args():
    """
    Parse and validate command-line arguments for fetching Discourse threads.

    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - base_url (str): Root URL of the Discourse forum.
            - category_path (str): Path to the category.
            - start_date (str): Start date (YYYY-MM-DD).
            - end_date (str): End date (YYYY-MM-DD).
            - output_dir (str): Directory to save thread JSON files.
            - api_key (str, optional): Discourse API key.
            - api_username (str, optional): Discourse API username.
            - cookies (str, optional): Raw Cookie header for authentication.
    """
    parser = argparse.ArgumentParser(
        description="Efficiently download all threads (with full post history) from a specified Discourse category within a date range."
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Root URL of the Discourse forum (e.g., https://discourse.example.com)"
    )
    parser.add_argument(
        "--category-path",
        required=True,
        help="Path to the category (e.g., category/slug/123 or courses/tds-kb/34)"
    )
    parser.add_argument(
        "--start-date",
        required=True,
        help="Earliest creation date (inclusive), format: YYYY-MM-DD"
    )
    parser.add_argument(
        "--end-date",
        required=True,
        help="Latest creation date (inclusive), format: YYYY-MM-DD"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to save thread JSON files"
    )
    auth = parser.add_argument_group("authentication (at least one method required)")
    auth.add_argument(
        "--api-key",
        metavar="KEY",
        help="Discourse API key (requires --api-username)"
    )
    auth.add_argument(
        "--api-username",
        metavar="USER",
        help="Discourse API username (requires --api-key)"
    )
    auth.add_argument(
        "--cookies",
        metavar="COOKIE_HEADER",
        help="Raw Cookie header for authentication (e.g. 'name=val; name2=val2')"
    )
    return parser.parse_args()

def ensure_dir(path):
    """
    Ensure the specified directory exists, creating it if necessary.

    Args:
        path (str): Path to the directory to ensure.
    """
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def fetch_json(url, params=None, headers=None):
    """
    Fetch JSON data from a given URL with optional headers and parameters.

    Args:
        url (str): The URL to fetch data from.
        headers (dict, optional): HTTP headers to include in the request.
        params (dict, optional): Query parameters to include in the request.

    Returns:
        dict: Parsed JSON response.

    Raises:
        requests.RequestException: If the request fails or returns an error status code.
    """
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise SystemExit(f"Error fetching data from {url}: {e}")

def main():
    args = parse_args()
    if not (args.cookies or (args.api_key and args.api_username)):
        raise SystemExit("\033[1;36mMinimum one authentication method is required: \033[0m \n \033[1;33m--cookies\033[0m \nor\n \033[1;33m--api-key\033[0m and \033[1;33m--api-username\033[0m")
    srt_dt = datetime.fromisoformat(args.start_date).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(args.end_date).replace(tzinfo=timezone.utc) 
    end_dt = end_dt.replace(hour=23, minute=59, second=59)
    ensure_dir(args.output_dir)
    headers = {
        "User-Agent": "Fetched Discourse Threads",
        "Accept": "application/json",    
    }
    if args.api_key and args.api_username:
        headers["Api-Key"] = args.api_key
        headers["Api-Username"] = args.api_username
    else:
        headers["Cookie"] = args.cookies
    page = 0
    downloaded = 0
    print(f"Fetching threads from category: /c/{args.category_path}.json pages for threads from {srt_dt.date()} to {end_dt.date()}")
    while True:
        response = fetch_json(f"{args.base_url}/c/{args.category_path}.json", headers=headers, params={"page": page, "per_page": 100})
        topics = response.get("topic_list", {}).get("topics", [])
        if not topics:
            print("No topics found or invalid response format.")
            break
        for topic in topics:
            created_at = topic.get("created_at")
            if not created_at:
                print(f"Topic {topic.get('id', 'unknown')} has no creation date, skipping.")
                continue
            created_dt = date_parser.isoparse(created_at)
            if created_dt < srt_dt:
                continue
            if srt_dt <= created_dt <= end_dt:
                topic_id = topic["id"]
                title = topic.get("title", "")
                output_file = os.path.join(args.output_dir, f"{topic_id}.json")
                if os.path.exists(output_file):
                    print(f"Thread {topic_id} already downloaded, \033[1;33mskipping\033[0m")
                    continue
                first = fetch_json(f"{args.base_url}/t/{topic_id}.json", params={"track_visit": False, "forceLoad": True, "page": 1}, headers=headers)
                posts = first.get("post_stream", {}).get("posts", [])
                total_posts = first.get("post_count") or len(first.get("post_stream", {}).get("stream", []))
                per_page = len(posts)
                if per_page and total_posts > per_page:
                    pages = ceil(total_posts / per_page)
                    for page_num in range(2, pages + 1):
                        more = fetch_json(f"{args.base_url}/t/{topic_id}.json", params={"track_visit": False, "forceLoad": True, "page": page_num}, headers=headers)
                        more_posts = more.get("post_stream", {}).get("posts", [])
                        if not more_posts:
                            print(f"No more posts found for topic {topic_id} on page {page_num}.")
                            break
                        posts.extend(more_posts)
                combined = first
                combined["post_stream"]["posts"] = posts
                with open(output_file, "w", encoding="utf-8") as fd:
                    json.dump(combined, fd, ensure_ascii=False, indent=4)
                print(f"[\033[1;32msave\033[0m] : \033[1;33m{topic_id}\033[0m | \033[1;36m{created_dt.date()}\033[0m | [post: {len(posts)}] - {title}")
                downloaded += 1
        page += 1
    print(f"[\033[1;32mdone\033[0m] {downloaded} threads saved to {args.output_dir}.")

if __name__ == "__main__":
    main()