from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from database import (
    init_db,
    get_stats,
    log_focus_session,
    update_activity,
    get_history,
    delete_history_item,
    clear_all_history,
    add_history,
    decay_stats,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from memory import save_memory, retrieve_context
from llm import generate_response_stream

# Global components for potential external reference
scheduler = AsyncIOScheduler()
stats = {} # Initial placeholder

async def run_decay():
    """Wrapper to run stat decay in the background."""
    global stats
    decay_stats()
    stats = get_stats()

class ChatRequest(BaseModel):
    message: str

class FocusCompleteRequest(BaseModel):
    minutes: int
    completed: bool = False

@asynccontextmanager 
async def lifespan(app: FastAPI):
    global stats
    # Startup logic
    init_db()
    stats = get_stats()
    
    # Start the scheduler for stat decay (every 5 minutes)
    if not scheduler.running:
        scheduler.add_job(run_decay, 'interval', minutes=5)
        scheduler.start()
        
    yield
    # Shutdown logic
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "alive", "component": "backend"}


@app.get("/stats")
async def get_pet_stats():
    stats = get_stats()
    if not stats:
        raise HTTPException(status_code=404, detail="Pet stats not found")
    return stats


@app.post("/focus/start")
async def start_focus():
    update_activity("focusing")
    return {"status": "success", "message": "Focus session started"}


@app.post("/focus/complete")
async def complete_focus(request: FocusCompleteRequest):
    log_focus_session(request.minutes, request.completed)
    update_activity("idle")
    return get_stats()


from fastapi.responses import StreamingResponse  # noqa: E402
import re  # noqa: E402


@app.post("/chat")
async def chat(request: ChatRequest):
    stats = get_stats()
    if not stats:
        raise HTTPException(status_code=404, detail="Pet stats not found")

    # 1. Retrieve relevant context from memory
    context = retrieve_context(request.message)

    async def event_generator():
        full_reply = ""
        async for chunk in generate_response_stream(request.message, stats, context):
            full_reply += chunk
            yield chunk

        # 1. Extract and Clean Reply
        actions_match = re.search(r"\[ACTIONS:\s*({.*?})\]", full_reply)
        
        # Strip both ACTIONS and SYSTEM_EVENT tags for the final saved/displayed reply
        cleaned_reply = re.sub(r"\[ACTIONS:.*?\]", "", full_reply)
        cleaned_reply = re.sub(r"\[SYSTEM_EVENT:.*?\]", "", cleaned_reply).strip()
        
        actions_dict = {}
        if actions_match:
            try:
                actions_dict = json.loads(actions_match.group(1))
            except Exception as e:
                print(f"Error parsing actions: {e}")

        # 2. Update stats based on LLM actions
        for a_type, a_val in actions_dict.items():
            if a_type == "log_minutes":
                # By default, manual logging via chat doesn't count as a "session" completion unless specified
                log_focus_session(int(a_val), actions_dict.get("session_completed", False))
            elif a_type == "set_activity":
                update_activity(str(a_val))

        # 3. Save to memory and history
        if not request.message.startswith("[SYSTEM_EVENT:"):
            save_memory(request.message, cleaned_reply)
            add_history("user", request.message)
        
        # Always add the bot's response to history so the user sees it
        add_history("bot", cleaned_reply)

    return StreamingResponse(event_generator(), media_type="text/plain")


@app.get("/history")
async def fetch_history():
    return {"history": get_history()}


@app.delete("/history/{item_id}")
async def delete_item(item_id: int):
    delete_history_item(item_id)
    return {"status": "success"}


@app.delete("/history")
async def clear_history():
    clear_all_history()
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
