#!/usr/bin/env python3
"""
scrape_discourse_content.py

This script provides a robust and efficient utility for downloading a GitHub repository (either a specific branch or commit) as a ZIP archive, extracting its contents, and retaining only Markdown (.md) files—excluding 'README.md' and any files containing 'sidebar' in their names. It is designed for automation and integration into content pipelines, particularly where only documentation files are needed from a repository.
Main Features:
--------------
- Downloads a GitHub repository as a ZIP file, supporting both branch and commit references.
- Securely extracts the ZIP archive, preventing path traversal vulnerabilities.
- Cleans the extracted directory tree, retaining only relevant Markdown files.
- Handles all file operations efficiently, using streaming and temporary directories for optimal performance and safety.
- Provides informative progress and error messages throughout the process.
Functions:
----------
- download_repo_zip(repo_url: str, ref: str, is_commit: bool = False, dest_path: str = None) -> str:
    Downloads a GitHub repository as a ZIP file from a specified branch or commit. Streams the download to minimize memory usage and saves the ZIP to the provided destination path. Raises errors for invalid paths or failed downloads.
- extract_repo_zip(zip_path: str, extract_to: str) -> None:
    Securely extracts the contents of a ZIP file to a specified directory. Ensures that all extracted files remain within the target directory to prevent path traversal attacks. Raises errors for invalid ZIP files or extraction issues.
- keep_only_md(root_dir: str) -> None:
    Traverses the given directory tree (bottom-up) and deletes all files except Markdown (.md) files, while also excluding 'README.md' and files containing 'sidebar' in their names (case-insensitive). Removes empty directories after file deletion.
- parse_args() -> argparse.Namespace:
    Parses command-line arguments for the script, supporting mutually exclusive options for branch or commit selection, and an optional output directory. Defaults to the 'main' branch if neither branch nor commit is specified.
- main():
    Orchestrates the entire workflow: argument parsing, ZIP download, secure extraction, moving the extracted content to the output directory, and cleaning up non-Markdown files. Handles errors and prints progress messages.
Usage Example:
--------------
    python scrape_discourse_content.py https://github.com/user/repo --branch main --output res/discourse_content
Command-Line Arguments:
-----------------------
    repo_url    : GitHub repository URL (required).
    --branch    : Branch name to download (default: "main").
    --commit    : Specific commit SHA to download (mutually exclusive with --branch).
    --output    : Output directory for extracted files (default: <repo>-<ref>).
Intended Use Cases:
-------------------
- Automated documentation extraction from GitHub repositories.
- Content filtering pipelines where only Markdown files are required.
- Secure and efficient repository archiving for offline processing.
Requirements:
-------------
- Python 3.6+
- requests
"""

import argparse
import os
import requests
import shutil
import tempfile
import zipfile

from urllib.parse import urlparse

def download_repo_zip(repo_url: str, ref: str, is_commit: bool = False, dest_path: str = None) -> str:
    """
    Efficiently downloads a GitHub repository as a ZIP file from a specific branch or commit.

    Args:
        repo_url  (str)  : Base URL of the GitHub repository (e.g., https://github.com/user/repo).
        ref       (str)  : Branch name (e.g., "main") or commit SHA to download.
        is_commit (bool) : If True, download the specific commit; otherwise, download the branch.
        dest_path (str)  : Path to save the downloaded ZIP file. Must not be None.

    Returns:
        str: The absolute path to the downloaded ZIP file.

    Raises:
        ValueError: If dest_path is not provided.
        requests.HTTPError: If the download fails.
    """
    if not dest_path:
        raise ValueError("Destination path for ZIP file must be specified.")
    repo_url = repo_url.rstrip('/')
    if is_commit:
        zip_url = f"{repo_url}/archive/{ref}.zip"
        print(f"Downloading commit {ref} from {repo_url} as ZIP...")
    else:
        zip_url = f"{repo_url}/archive/refs/heads/{ref}.zip"
        print(f"Downloading branch {ref} from {repo_url} as ZIP...")
    with requests.get(zip_url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded ZIP file to {dest_path}")

def extract_repo_zip(zip_path: str, extract_to: str) -> None:
    """
    Efficiently extracts all contents of a ZIP file to a specified directory.
    This function uses buffered extraction for optimal performance and ensures
    that extraction is secure (prevents path traversal attacks).

    Args:
        zip_path (str)     : Absolute path to the ZIP file to extract.
        extract_to (str)   : Directory where the contents will be extracted.

    Raises:
        FileNotFoundError  : If the ZIP file does not exist.
        zipfile.BadZipFile : If the file is not a valid ZIP archive.
        Exception          : For any extraction errors.
    """
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")
    print(f"Extracting {zip_path} to {extract_to}...")

    def is_within_directory(directory, target):
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
        return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            member_path = os.path.join(extract_to, member.filename)
            if not is_within_directory(extract_to, member_path):
                raise Exception(f"Unsafe ZIP: {member.filename} would extract outside {extract_to}")
        zip_ref.extractall(extract_to)
    print(f"Extraction complete. Contents are in {extract_to}.")

def keep_only_md(root_dir: str) -> None:
    """
    Efficiently removes all files in the given directory tree except Markdown (.md) files,
    while also excluding 'README.md' and any file whose name contains 'sidebar' (case-insensitive).
    Traverses the directory tree bottom-up for safe deletion.

    Args:
        root_dir (str): The root directory to clean.

    Behavior:
        - Keeps only files ending with '.md' (case-insensitive), except:
            - Files named 'README.md' (case-insensitive) are deleted.
            - Files containing 'sidebar' in their name (case-insensitive) are deleted.
        - All other files are deleted.
        - Traverses the directory tree bottom-up for efficient and safe deletion.

    Raises:
        OSError: If file deletion fails.
    """
    md_ext = '.md'
    readme = 'readme.md'
    sidebar = 'sidebar'

    for dirpath, _, filenames in os.walk(root_dir, topdown=False):
        for filename in filenames:
            lower = filename.lower()
            keep = (
                lower.endswith(md_ext)
                and lower != readme
                and sidebar not in lower
            )
            if not keep:
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    print(f"\033[1;91mdelete\033[0m {file_path}")
                except Exception as e:
                    print(f"Failed to delete files{file_path}: {e}")
        try:
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
                print(f"\033[1;91mdelete\033[0m {dirpath}")
        except Exception as e:
            print(f"Failed to delete directory {dirpath}: {e}")


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for downloading and extracting a GitHub repository.

    Returns:
        argparse.Namespace: Parsed arguments with the following attributes:
            - repo_url (str): GitHub repository URL.
            - branch (str or None): Branch name to download (default: "main").
            - commit (str or None): Commit SHA to download.
            - output (str or None): Output directory for extracted files.
    """
    parser = argparse.ArgumentParser(
        description="Download a GitHub repo as ZIP (branch or specific commit), extract it, and keep only .md files."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--branch", type=str, help="Branch name to download (default: main)."
    )
    group.add_argument(
        "--commit", type=str, help="Specific commit SHA to download."
    )
    parser.add_argument(
        "repo_url", type=str, help="GitHub repository URL (e.g., https://github.com/user/repo)"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Output directory (default: <repo>-<ref>)"
    )
    args = parser.parse_args()
    if not args.branch and not args.commit:
        args.branch = "main"
    return args

def main():
    """
    Orchestrates the process of downloading a GitHub repository (branch or commit) as a ZIP,
    extracting its contents, moving them to the output directory, and retaining only Markdown files
    (excluding 'README.md' and files containing 'sidebar' in their name).

    Steps:
        1. Parse command-line arguments for repo URL, branch/commit, and output directory.
        2. Download the specified branch or commit as a ZIP file to a temporary directory.
        3. Securely extract the ZIP file in the temporary directory.
        4. Locate the extracted root folder and move it to the output directory, replacing any existing one.
        5. Remove all files except Markdown files (excluding 'README.md' and files with 'sidebar' in their name).
        6. Print progress and completion messages.

    Optimizations:
        - Uses tempfile.TemporaryDirectory for automatic cleanup and isolation.
        - Streams ZIP download to minimize memory usage.
        - Extracts ZIP securely to prevent path traversal.
        - Moves (not copies) extracted directory for efficiency.
        - Traverses directory tree bottom-up for safe file deletion.

    Raises:
        FileNotFoundError: If the extracted directory cannot be located.
        Exception: For any errors during download, extraction, or file operations.
    """
    args = parse_args()
    parsed = urlparse(args.repo_url)
    repo_name = os.path.basename(parsed.path.rstrip('/'))
    is_commit = args.commit is not None
    ref = args.commit if is_commit else args.branch
    out_dir = args.output or f"{repo_name}-{ref}"

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, f"{repo_name}.zip")
        download_repo_zip(args.repo_url, ref, is_commit, zip_path)
        extract_repo_zip(zip_path, tmp)
        extracted_folder = next(
            (os.path.join(tmp, item) for item in os.listdir(tmp)
             if os.path.isdir(os.path.join(tmp, item))),
            None
        )
        if not extracted_folder:
            raise FileNotFoundError("Could not locate extracted directory.")
        if os.path.exists(out_dir):
            print(f"Removing existing directory {out_dir}...")
            shutil.rmtree(out_dir)
        shutil.move(extracted_folder, out_dir)
        print(f"Moved contents to {out_dir}")
    keep_only_md(out_dir)
    print("\033[1;93mCleanup Complete: Only relevant .md files are retained.\033[0m")

if __name__ == "__main__":
    main()