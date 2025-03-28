import subprocess
import sys
import logging

# Approved LLM models installed on your local machine.
LLM_MODELS = [
    "phi4",
    "mistral",
    "llama3.2",
    "gemma3",
    "deepseek-r1:8b"
]

logging.basicConfig(level=logging.INFO)

def call_ollama_sync(model: str, prompt: str) -> str:
    """Synchronous call to Ollama using subprocess."""
    try:
        command = ["ollama", "run", model]
        logging.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(
            command,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            timeout=300
        )
        # Remove markdown formatting if present.
        return result.stdout.strip().replace("```", "")
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"Timeout: Model {model} took too long.\n")
        return "Error: Request timed out."
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Error calling {model}: {e.stderr}\n")
        return f"Error calling {model}: {e.stderr}"

def generate_ad_copy(prompt: str, model: str = "llama3.2") -> str:
    """Generate text using the specified model via Ollama.
    
    Args:
        prompt (str): The prompt for the LLM.
        model (str): The name of the model to use.
        
    Returns:
        str: The generated text or an error message.
    """
    if model not in LLM_MODELS:
        return f"Model '{model}' is not available. Please select a valid model."
    logging.info(f"Generating text using model: {model}")
    return call_ollama_sync(model, prompt)
