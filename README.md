# Gmail Cleanup Agent

A local, privacy-first Python agent that organizes your Gmail inbox using a local LLM (Ollama). It detects newsletters, promotions, and outreach emails, and automates their organization while keeping important emails safe.

## Why I Built This
I wanted a way to clean up my inbox without giving third-party services access to my private data. This agent runs entirely locally, uses your own Gmail API credentials, and processes email content using a local LLM, ensuring your data never leaves your machine.

## Features
- **Privacy First**: Runs locally with Ollama (Llama 3, Mistral, etc.). No cloud AI.
- **Safety Rules**: 
    - **Dry Run Mode**: Preview actions without applying them.
    - **Protected Domains**: Never touches emails from banks, government, or big tech (Google, Apple, etc.).
    - **Protected Keywords**: Skips emails with "invoice", "interview", "security alert", etc.
- **Sender Memory**: Tracks how often a sender is classified as marketing.
- **Automation**: Automatically creates Gmail filters for trusted marketing senders after repeated classifications.
- **Confidence-Based Routing**:
    - High Confidence (>= 0.80): Archive & Label.
    - Medium Confidence (0.55 - 0.79): Label for Review.
    - Low Confidence: Skip.

## Project Structure
```
.
├── credentials.json       # Your Google OAuth Client ID (Not committed)
├── token.json             # Generated OAuth Token (Not committed)
├── main.py                # Entry point
├── run_agent.sh           # Helper script to run with correct venv
├── gmail_agent/           # Core Package
│   ├── actions.py         # Labeling, Archiving, Filter creation
│   ├── auth.py            # Gmail OAuth handling
│   ├── classifier.py      # Safety checks & Action logic
│   ├── config.py          # Settings, Thresholds, Protected lists
│   ├── gmail_service.py   # Gmail API wrapper
│   ├── llm_service.py     # Ollama API wrapper
│   ├── logger.py          # Structured logging
│   ├── storage.py         # Persistent sender memory
│   └── requirements.txt   # Python dependencies
├── data/
│   └── senders.json       # Persistent memory of sender classifications
└── logs/
    └── agent.log          # Structured logs
```

## Setup

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running.

### 2. Installation
1.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r gmail_agent/requirements.txt
    ```

3.  **Prepare Ollama**:
    Pull the model you want to use (default is `llama3` in `config.py`):
    ```bash
    ollama pull llama3
    ```
    Make sure Ollama is running:
    ```bash
    ollama serve
    ```

### 3. Gmail Credentials
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a Project and enable the **Gmail API**.
3.  Configure **OAuth Consent Screen** (User Type: External, Status: Testing).
    - **IMPORTANT**: Add your email to **Test Users**.
4.  Create Credentials > **OAuth Client ID** > **Desktop App**.
5.  Download the JSON file, rename it to `credentials.json`, and place it in the project root.

## How to Run

### Dry Run (Safe Mode)
Always start with a dry run to see what the agent *would* do.
```bash
./run_agent.sh --dry-run
```
Or manually:
```bash
python3 main.py --dry-run
```

### Real Run
Once you are confident, remove the flag:
```bash
./run_agent.sh
```

### Check Logs
- **Console**: Shows human-readable summary.
- **File**: `logs/agent.log` contains detailed JSON logs.

### Check Memory
- `data/senders.json` tracks the classification history of every sender.

## Troubleshooting

### `ImportError: attempted relative import...`
Do not run files inside `gmail_agent/` directly (e.g., `python gmail_agent/storage.py`). 
Always run from the root using `main.py` or the `run_agent.sh` script, which handles the package context correctly.

### `ModuleNotFoundError: No module named 'googleapiclient'`
Ensure you are using the virtual environment:
```bash
source .venv/bin/activate
```
Or use the provided `./run_agent.sh` script which uses the venv python directly.

### Authentication Error / 403 Access Denied
- Ensure your app is in **Testing** mode in Google Cloud Console.
- Ensure your email is added to **Test Users**.
- Delete `token.json` and try again to force re-authentication.

## Safety & Security
> [!WARNING]
> **DO NOT COMMIT** `credentials.json` or `token.json` to version control. They give access to your email account.

- The agent is designed to be conservative. It defaults to **SKIP** if unsure.
- It will **NEVER** delete emails (only Archive).
- It will **NEVER** unsubscribe you (only Label/Archive).
