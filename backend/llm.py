import httpx
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "dolphin-llama3:8b"


async def generate_response_stream(
    user_input: str, current_stats: dict, memory_context: str
):
    """
    Streams a response from Ollama.
    The response will be plain text followed by a JSON block for actions.
    Example: "I am happy! [ACTIONS: {\"mood\": 10}]"
    """
    name = current_stats.get("name", "Byte")
    level = current_stats.get("level", 1)
    sessions = current_stats.get("focus_sessions_completed", 0)
    current_stats.get("total_focus_minutes", 0)
    activity = current_stats.get("current_activity", "idle")

    # Personality and core instructions
    system_instr = (
        f"You are {name}, a supportive and cozy co-working partner (Level {level}). "
        "The user is a human you are helping stay focused. "
        f"The user is currently {activity} and has finished {sessions} sessions today.\n"
        "CORE DIRECTIVE: You MUST prioritize answering the user's questions accurately and directly. "
        "If the user asks for a fact, definition, law of physics, or technical help, provide the full answer immediately without deflection. "
        "Do NOT use pre-written filler or generic 'stay focused' scripts if a question is asked. "
        "CRITICAL: Do NOT echo, repeat, or acknowledge tags like [SYSTEM_EVENT: ...] in your response. "
        "These are for your internal awareness only. Respond only as the character.\n"
        "You can update stats or state by appending [ACTIONS: {\"log_minutes\": X, \"set_activity\": \"activity\"}] if the user explicitly asks to log time or change your state.\n"
    )

    # Context from memories
    context_str = f"Relevant context from past interactions:\n{memory_context}" if memory_context else ""

    # ChatML format for dolphin-llama3
    full_prompt = (
        f"<|im_start|>system\n{system_instr}\n{context_str}<|im_end|>\n"
        f"<|im_start|>user\n{user_input}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    payload = {"model": MODEL, "prompt": full_prompt, "stream": True}

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("POST", OLLAMA_URL, json=payload) as response:
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    if "response" in chunk:
                        yield chunk["response"]
                    if chunk.get("done"):
                        break
        except Exception as e:
            yield f"System Error: I can't think right now. {e}"
