import torch
import time
import random
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer

# -----------------------------------------------------------
# LOGGING SETUP
# -----------------------------------------------------------
logger = logging.getLogger("assist_ai_model")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(handler)

# -----------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------
MODEL_NAME = "microsoft/phi-2"    # <-- You can replace
MAX_TOKENS = 250
TEMPERATURE = 0.6
TOP_P = 0.9

ENABLE_HISTORY = True
MAX_HISTORY_TURNS = 6

ENABLE_CLEANING = True
ENABLE_SHORTENING = True
ENABLE_SAFETY_FILTER = True
ENABLE_OUTPUT_CACHE = True

# -----------------------------------------------------------
# OUTPUT CACHE (reduces repeated compute)
# -----------------------------------------------------------
REPLY_CACHE = {}

# -----------------------------------------------------------
# LOAD MODEL + TOKENIZER
# -----------------------------------------------------------
logger.info("🚀 Loading Assist AI model: %s", MODEL_NAME)

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16
        if torch.cuda.is_available()
        else torch.float32,
        device_map="auto"
    )

    DEVICE = model.device
    logger.info("🔥 Model loaded on device: %s", DEVICE)

except Exception as e:
    logger.error("❌ Failed to load model: %s", e)
    raise SystemExit("Model failed to load. Fix and restart.")

# -----------------------------------------------------------
# PROMPT FORMATTER
# -----------------------------------------------------------
def format_prompt(system_msg, history, user_msg):
    prompt = ""

    # System Message
    prompt += f"<SYSTEM>\n{system_msg}\n</SYSTEM>\n\n"

    # Chat History
    if ENABLE_HISTORY and history:
        for turn in history[-MAX_HISTORY_TURNS:]:
            prompt += f"User: {turn['user']}\nAssistant: {turn['bot']}\n\n"

    # Current Message
    prompt += f"User: {user_msg}\nAssistant:"
    return prompt


# -----------------------------------------------------------
# CLEAN OUTPUT
# -----------------------------------------------------------
def clean_output(text):
    if not ENABLE_CLEANING:
        return text

    bad_tokens = ["<s>", "</s>", "<pad>", "[PAD]", "User:", "Assistant:"]
    for t in bad_tokens:
        text = text.replace(t, "")

    text = text.strip()

    # Remove repeated model echo
    if len(text) > 300:
        text = text[-300:]

    return text


# -----------------------------------------------------------
# SHORTEN OUTPUT TO 2 LINES (for ChatGPT-like style)
# -----------------------------------------------------------
def shorten_output(text):
    if not ENABLE_SHORTENING:
        return text

    # Split into sentences
    parts = text.split(".")
    cleaned = ". ".join(parts[:2]).strip()

    if not cleaned.endswith("."):
        cleaned += "."

    return cleaned


# -----------------------------------------------------------
# SAFETY FILTER (basic)
# -----------------------------------------------------------
def safety_filter(text):
    if not ENABLE_SAFETY_FILTER:
        return text

    blocked = [
        "kill", "suicide", "bomb", "hack", "illegal", "weapon",
        "porn", "sex", "nude", "drugs"
    ]

    low = text.lower()
    if any(b in low for b in blocked):
        return "I cannot help with that, please ask something safe."

    return text


# -----------------------------------------------------------
# GENERATE RAW MODEL OUTPUT
# -----------------------------------------------------------
def run_model(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_length=MAX_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            do_sample=True
        )

    text = tokenizer.decode(output[0], skip_special_tokens=False)
    return text


# -----------------------------------------------------------
# MAIN PUBLIC FUNCTION
# -----------------------------------------------------------
def generate_reply(prompt, history=None):
    """
    Main function used by Django.
    Handles:
    - cleaning
    - caching
    - formatting
    - safety
    - retry system
    """

    # --- CACHE CHECK -------------------------------------
    if ENABLE_OUTPUT_CACHE and prompt in REPLY_CACHE:
        return REPLY_CACHE[prompt]

    # --- RETRY SYSTEM ------------------------------------
    for attempt in range(3):
        try:
            raw = run_model(prompt)
            reply = clean_output(raw)
            reply = safety_filter(reply)
            reply = shorten_output(reply)

            # Save into cache
            if ENABLE_OUTPUT_CACHE:
                REPLY_CACHE[prompt] = reply

            return reply

        except Exception as e:
            logger.error("Error attempt %s: %s", attempt + 1, e)
            time.sleep(0.5)

    return "I’m sorry, my system is busy. Please try again."


# -----------------------------------------------------------
# HIGH-LEVEL CHAT FUNCTION (simple for views.py)
# -----------------------------------------------------------
def chat_response(system_msg, history, user_msg):
    formatted = format_prompt(system_msg, history, user_msg)
    reply = generate_reply(formatted, history=history)
    return reply


# -----------------------------------------------------------
# TEST ONLY
# -----------------------------------------------------------
if __name__ == "__main__":
    print("Model test:")
    sys_msg = "You are Assist AI. Reply shortly and clearly."

    hist = [
        {"user": "hello", "bot": "Hi! How can I assist you?"}
    ]

    out = chat_response(sys_msg, hist, "Who are you?")
    print("AI:", out)