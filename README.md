# Ad Scheduling App with LLM Integration

This project is a Flask-based advertisement scheduling application that integrates with locally installed LLM models via Ollama. The approved models include:

- **phi4**
- **llama3.2** (default)
- **deepseek-r1:8b**

## Features

- **Ad Campaign Scheduling:** Schedule new ad campaigns with start and end dates.
- **LLM Integration:** Generate creative ad copy using a selected local model via Ollama.
- **Model Selection:** Choose from a dropdown list on the ad copy generation page.
- **Health Check Endpoint:** Verify the application status at `/health`.

## Setup Instructions

1. **Clone or create the project folder** with the file structure provided.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
