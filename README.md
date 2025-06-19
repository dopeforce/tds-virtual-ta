# TDS Virtual TA
![Image](https://github.com/user-attachments/assets/f4e42031-6e02-4ffc-9467-2bd9ef51c10d)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/dopeforce/tds-virtual-ta)](https://github.com/dopeforce/tds-virtual-ta/issues)
[![GitHub forks](https://img.shields.io/github/forks/dopeforce/tds-virtual-ta)](https://github.com/dopeforce/tds-virtual-ta/network)
[![GitHub stars](https://img.shields.io/github/stars/dopeforce/tds-virtual-ta)](https://github.com/dopeforce/tds-virtual-ta/stargazers)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.1-ff69b4.svg)](CODE_OF_CONDUCT.md)

## 📝 Description

Virtual Teaching Assistant (Virtual TA) is an innovative, intelligent and automated assistant designed specifically for the Tools in Data Science (TDS) course offered by the IIT Madras Online Degree Program. This cutting-edge system revolutionizes the learning experience by providing students with accurate, context-aware answers to their questions.

**Project Status:** Active Development **Last Updated:** 2025-05-18

## ✨ Features

- **Automated Responses:** Provides quick answers to frequently asked questions.
- **Discourse Integration:** Seamlessly works with discourse platforms.
- **Course-Specific:** Tailored for the IITM BS TDS course curriculum and common queries.
- **Extensible:** Designed to be easily updated with new Q&A pairs and functionalities.

## 💽 Tech Stack

- **Language**: Python 3.8+
- **Embedding Model**: `all-MiniLM-L6-v2` (sentence-transformers)
- **Vector Database**: FAISS
- **API Framework**: FastAPI
- **Deployment**: Docker, Docker Compose
- **Dependencies**: See [requirements.txt](requirements.txt)

## 📂 Project Structure

```
dopeforce/tds-virtual-ta/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── app/                                          + main code required for application
├── inc/                                          + Test suites for `promptfoo`
|   ├── project-tds-virtual-ta-promptfoo.yaml
|   └── project-tds-virtual-ta-q1               
├── res/                                          + Contains discourse scraped data
│   ├── discourse_content/                        + Scraped Markdown or HTML files
│   ├── discourse_threads/                        + Scraped and Proccesed JSON files
│   ├── discourse_posts/                          + Scraped and Processed Text files
│   └── model/
│       ├── metadata.json
│       └── virtual-ta.faiss
├── scr/                                          + Utility and automation scripts
├── src/                                          + Contains the course content scraping scripts
|   ├── scraping/  
|       ├── scrape_course.py
│       └── scrape_discourse.py
├── .dockerignore                                 + Docker Ignore configuration
├── .env.example                                  + Example environment variables
├── .gitignore                                    + Specifies intentionally untracked files that Git should ignore
├── Dockerfile                                    + Defines the Docker image
├── docker-compose.yml                            + Docker Compose configuration
├── CODE_OF_CONDUCT.md                            + Community guidelines              | not included
├── CONTRIBUTING.md                               + Guidelines for contributors       | not included
├── LICENSE                                       + Project license (MIT License)
├── README.md                                     + Project overview and instructions
└── requirements.txt                              + Python dependencies
```

## 💲 Envirnment Setup

### Prerequisites

- Python 3.x
- Docker (Optional, for containerized deployment)
- Git

## ✳️ Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/dopeforce/tds-virtual-ta.git
    cd tds-virtual-ta
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv

    # On Linux use `venv/bin/activate`
    source venv/bin/activate

    # On Windows use `venv\Scripts\activate`
    venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Rename `.env.example` to `.env` and fill in the necessary configuration details.
    ```bash
    cp .env.example .env
    # Open .env and required update variables
    ```

## 📟 Data Preparation

This directory contains various utility and automation scripts for data preparation, processing, and automation:

## Scrape Discourse Threads
### [ ✅ Click Here :  ](https://github.com/dopeforce/tds-virtual-ta/tree/meta/res/discourse_threads)[`scrape_discourse_threads.py`](res/scrape_discourse_threads.py)

- **Purpose:** Downloads all Discourse threads in a specific category between two dates, including all posts in each thread (with pagination support). Supports authentication via API key or cookies.

- **Description:**

  ```python
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
  ```

- **Usage:**
  ```bash
  python scr/scrape_discourse_threads.py \
    --base-url "https://discourse.onlinedegree.iitm.ac.in" \
    --category-path "courses/tds-kb/34" \
    --start-date "2025-01-01" \
    --end-date "2025-04-14" \
    --output-dir "data/raw_discourse_threads" \
    [--api-key KEY --api-username USER] \
    [--cookies "name=value; name2=value2"]
  ```

---

## Convert JSON to Markdown
### [ ✅ Click Here :  ](https://github.com/dopeforce/tds-virtual-ta/tree/meta/res/discourse_posts)[`jsonpost_2_markdownfile.py`](res/jsonpost_2_markdownfile.py)

- **Purpose:** Converts Discourse thread JSON files into plain-text Markdown summaries. Can process a single file or all JSON files in a directory.
- **Usage:**
  ```bash
  python scripts/jsonpost_2_markdownfile.py input_path [--output OUTPUT_DIR]
  # Example:
  python scripts/jsonpost_2_markdownfile.py thread.json
  python scripts/jsonpost_2_markdownfile.py data/raw_discourse_threads --output data/discourse_posts
  ```

## Scrape Course Content
### [ ✅ Click Here :  ](https://github.com/dopeforce/tds-virtual-ta/tree/meta/res/discourse_content)[`scrape_discourse_content.py`](scripts/scrape_discourse_content.py)

[](https://github.com/dopeforce/tds-virtual-ta/tree/meta/res/discourse_content)

- **Purpose:** Downloads a GitHub repository (by branch or commit) as a ZIP, extracts it, and keeps only `.md` files, deleting everything else.

- **Usage:**

  ```bash
  # Command
  python scr/scrape_discourse_content.py [--branch BRANCH | --commit SHA] <repo_url> [--output OUTPUT_DIR]

  # Example:
  python scr/scrape_discourse_content.py --branch tds-2025-01 --output res/discourse_content https://github.com/sanand0/tools-in-data-science-public
  ```

---

## Build Vector Database
### [ ✅ Click Here :  ](https://github.com/dopeforce/tds-virtual-ta/tree/meta/res/model)[`create_vector_db.py`](res/create_vector_db_openai.py)

- **Purpose:** Builds a FAISS vector database from text, Markdown, or HTML files (e.g., course content or discourse posts). Chunks and embeds text using OpenAI API, and saves the index and metadata for later retrieval.

- **Usage:**  
   Edit configuration variables if needed, then run:

  ```bash
  # Command:
  python scr/create_vector_db.py      # Choose from openai or transformers

  # Example:
  python scr/create_vector_db_openai.py       # For openai
  python scr/create_vector_db_manual.py       # For transformers
  ```

  By default, processes content in the `res/` directory and saves output to `model/`.

- **Resource Structure:**
  ```
  project/
  ├── res/
  │   ├── discourse_content/          + Scraped Markdown or HTML files
  │   ├── discourse_threads/          + Scraped and Proccesed JSON files
  │   ├── discourse_posts/            + Scraped and Processed Text files
  │   └── model/
  │       ├── metadata.json
  │       └── virtual-ta.faiss
  ├── .env (optional, not required for new script)
  ├── scr/
  |   ├── create_vector_db_openai.py  + Required python script for openai
  |   └── create_vector_db_manual.py  + Required python Script for transformers
  └── + Required Python Script and dependencies
  ```

For more details about each script, see the script source files in the [`scr/`](scr) directory.

## 🔃 Running the Application

- **Directly with Python:**

  ```bash
  # (Ensure your virtual environment is activated and .env is configured)
  # Runs at localhost:8000

  # 01
  uvicorn app.main:app --reload

  # 02
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```

- **With Docker:**
  1.  Build the Docker image:
      ```bash
      docker build -t tds-virtual-ta .
      ```
  2.  Run using Docker Compose:
      ```bash
      docker-compose up
      ```
      Or run the image directly:
      ```bash
      docker run -d --env-file .env tds-virtual-ta
      ```


## ↗️ API Usage

Send a POST request to `/api/` with a JSON payload:

```bash
curl -X POST "http://localhost:8000/api/" \
     -H "Content-Type: application/json" \
     -d '{"question": "Should I use gpt-4o-mini or gpt-3.5-turbo?", "image": ""}'
```

Response format:

```json
{
  "answer": "Use gpt-3.5-turbo-0125 as specified in the course.",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
      "text": "Use the model mentioned in the question."
    }
  ]
}
```

## Reporting Issues

- Use the [issue tracker](https://github.com/dopeforce/tds-virtual-ta/issues).
- Choose the appropriate template (bug report or feature request).
- Provide detailed information, including steps to reproduce, environment, and expected behavior.

## Community Standards

We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please ensure your interactions are respectful and inclusive.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
