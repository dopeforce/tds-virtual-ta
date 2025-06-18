#!/usr/bin/env python3
"""
This script converts Discourse thread JSON files into plain-text Markdown summaries.
Features:
- Processes a single JSON file or all JSON files in a directory.
- Extracts thread metadata and post content, converting HTML post bodies to plain text.
- Outputs each thread as a Markdown-formatted text file with metadata headers.
Arguments:
    input_path: Path to a JSON file or a directory containing JSON files.
    --output, -o: (Optional) Output directory for generated text files. Defaults to './discourse_posts'.
Functionality:
- Parses Discourse thread JSON files, extracting post streams and metadata.
- Converts HTML post bodies to plain text using BeautifulSoup.
- Writes each thread to a Markdown file, including thread metadata and all posts in chronological order.
- Handles errors in reading/writing files and missing input paths.
- Maintains a set of unique user titles encountered during processing (printed at the end).
Dependencies:
- Python 3
- BeautifulSoup4
Example:
    python jsonpost_2_markdownfile.py thread.json
    python jsonpost_2_markdownfile.py /path/to/json_dir --output ./out_texts
"""

import sys
import json
import argparse

from pathlib import Path
from bs4 import BeautifulSoup

def html_to_text(html: str) -> str:
    """
    Converts an HTML string to plain text, preserving line breaks and removing excess blank lines.
    This function parses the input HTML using BeautifulSoup, extracts the text content with line breaks
    between block elements, and then processes the resulting lines to remove trailing whitespace and
    collapse multiple consecutive blank lines into a single blank line.

    Args:
        html (str): The HTML content to convert to plain text.

    Returns:
        str: The plain text representation of the HTML, with normalized line breaks and no excess blank lines.

    Example:
        >>> html = "<p>Hello<br>World!</p><p>Another paragraph.</p>"
        >>> print(html_to_text(html))
        Hello
        World!
        Another paragraph.
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned.append("")
                prev_blank = True
        else:
            cleaned.append(line)
            prev_blank = False
    return "\n".join(cleaned).strip()

po = set()

def thread_to_text(data: dict) -> str:
    """
    Converts a Discourse thread JSON object into a plain text representation.

    Args:
        data (dict): A dictionary representing the JSON structure of a Discourse thread. 
            It is expected to contain a "post_stream" key with a "posts" list, where each 
            post is a dictionary containing information such as creation time, author, 
            user title, and post content.

    Returns:
        str: A plain text string representing the thread, where each post is formatted 
            with a header (including timestamp, author name, username, and user title if available) 
            followed by the post body converted from HTML to plain text. Posts are separated by 
            blank lines.

    Detailed Description:
        - The function extracts the list of posts from the thread data and sorts them 
          chronologically by their "created_at" timestamp.
        - For each post, it constructs a header line that includes:
            - The timestamp of the post.
            - The display name or username of the author.
            - The username (preceded by '@').
            - The user's title (if available), appended after a colon.
        - The body of each post is converted from HTML to plain text using the `html_to_text` function.
        - Each post's header and body are appended to the output, separated by blank lines.
        - The final output is a single string containing all posts in order, suitable for 
          plain text display or further processing.

    Note:
        - The function assumes the existence of a `html_to_text` function for HTML conversion.
        - There is a reference to a variable `po` which is not defined within the function scope; 
          its intended purpose is unclear and may require clarification or correction.
    """
    posts = data.get("post_stream", {}).get("posts", [])
    posts.sort(key=lambda x: x.get("created_at", ""))
    outlines = []
    for post in posts:
        ts = post.get("created_at", "")
        name = post.get("name") or post.get("username")
        user = post.get("username", "")
        user_post = post.get("user_title", None)
        if user_post not in po:
            po.add(user_post)
        header = f"[{ts}] {name} (@{user}{(': ' + user_post) if user_post else ''})"
        body = html_to_text(post.get("cooked", ""))
        outlines.append(header)
        outlines.append(body)
        outlines.append("")
    return "\n".join(outlines).strip()

def process_file(input_file: Path, output_dir: Path) -> None:
    """
    Reads a Discourse thread JSON file, extracts relevant metadata and post content, and writes the result as a Markdown-formatted text file.

    Args:
        input_file (Path): Path to the input JSON file containing the Discourse thread.
        output_dir (Path): Directory where the output text file will be saved.

    Functionality:
        - Opens and parses the input JSON file.
        - Extracts thread metadata such as thread ID, title, and creation timestamp.
        - Converts the thread's posts to plain text using the `thread_to_text` function.
        - Ensures the output directory exists.
        - Writes a Markdown-formatted text file containing metadata headers and the thread content.
        - Handles file reading and writing errors gracefully, printing error messages to stderr.
        - Prints a success message upon successful processing.

    Output:
        A text file named `<thread_id>.txt` is created in the specified output directory, containing the thread's metadata and all posts in plain text format.
    """
    try:
        with input_file.open(encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}", file=sys.stderr)
        return
    post_id = data.get("id", input_file.stem)
    title = data.get("title", "")
    created_at = data.get("created_at", "")
    text_content = thread_to_text(data)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{post_id}.txt"
    try:
        with out_path.open("w", encoding="utf-8") as txt:
            txt.write("---\n")
            txt.write(f"id:          {post_id}\n")
            txt.write(f"title:       {title}\n")
            txt.write(f"created_at:  {created_at}\n")
            txt.write("---\n\n")
            txt.write(text_content)
        print(f"\033[1;32mProcessed\033[0m {input_file} | {out_path}")
    except Exception as e:
        print(f"Error writing {out_path}: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="Process Discourse thread JSON files to text summaries."
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to a JSON file or a directory of JSON files.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("./discourse_posts"),
        help="Output directory for text files.",
    )
    args = parser.parse_args()
    if not args.input_path.exists():
        print(f"Error: {args.input_path} does not exist.", file=sys.stderr)
        sys.exit(1)
    if args.input_path.is_file():
        process_file(args.input_path, args.output)
    else:
        json_files = sorted(args.input_path.glob("*.json"))
        if not json_files:
            print(f"No JSON files found in {args.input_path}.", file=sys.stderr)
            sys.exit(1)
        for jf in json_files:
            process_file(jf, args.output)

if __name__ == "__main__":
    main()
    print(po)