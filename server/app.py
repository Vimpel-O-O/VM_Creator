import queue
import threading
import time
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager  # <-- 1. ADD THIS IMPORT

# --- Import P3's function ---
from server.stability_client import render_scene

# --- 1. Define Data Structures ---
job_queue = queue.PriorityQueue()
scene_data: Dict[str, Any] = {}
scene_status: Dict[str, Any] = {}
style_bible_global: str = "default style bible"

NUM_WORKERS = 4


# --- 2. Define Pydantic Models ---
class Scene(BaseModel):
    id: str
    bg: Dict[str, str]
    characters: List[Dict[str, Any]]
    camera: str
    mood: str
    dialogue: List[str]


class StoryPayload(BaseModel):
    style_bible: str
    scenes: List[Scene]


# --- 3. Define the Worker Function ---
# (This is the same function as before)
def process_queue():
    while True:
        try:
            priority, scene_id = job_queue.get()
            print(f"[Worker {threading.current_thread().name}] Picked up job: {scene_id}")

            if scene_id in scene_status:
                scene_status[scene_id]["status"] = "rendering"

            scene_to_render = scene_data.get(scene_id)

            if scene_to_render:
                try:
                    filename = render_scene(scene_to_render, style_bible_global)
                    scene_status[scene_id]["status"] = "ready"
                    scene_status[scene_id]["url"] = f"http://127.0.0.1:5000/cdn/{filename}"
                    print(f"[Worker {threading.current_thread().name}] Job {scene_id} complete.")
                except Exception as e:
                    print(f"[Worker {threading.current_thread().name}] Job {scene_id} FAILED: {e}")
                    scene_status[scene_id]["status"] = "failed"

            job_queue.task_done()
        except Exception as e:
            print(f"[Worker {threading.current_thread().name}] CRITICAL ERROR: {e}")
            time.sleep(1)


# --- 4. Define the Lifespan Event Handler (The New Way) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup:
    print(f"Starting {NUM_WORKERS} background worker threads...")
    for i in range(NUM_WORKERS):
        worker_thread = threading.Thread(
            target=process_queue,
            daemon=True,
            name=f"Worker-{i + 1}"
        )
        worker_thread.start()

    # This 'yield' is the point where the app is "alive"
    yield

    # This code runs on shutdown (optional)
    print("Application shutting down...")


# --- 5. Create FastAPI App ---
app = FastAPI(lifespan=lifespan)  # <-- 2. ATTACH THE LIFESPAN
app.mount("/cdn", StaticFiles(directory="cdn"), name="cdn")


# --- 6. REMOVE THE OLD STARTUP EVENT ---
# @app.on_event("startup")  <-- DELETE THIS FUNCTION


# --- 7. Endpoints ---
# (No changes needed to your endpoints)

@app.get("/")
def read_root():
    return {"status": "Pypiline server is running"}


@app.post("/enqueue_scenes")
def enqueue_scenes(payload: StoryPayload):
    global style_bible_global
    print(f"Received job with {len(payload.scenes)} scenes.")
    style_bible_global = payload.style_bible
    HIGH_PRIORITY_COUNT = 3
    for i, scene in enumerate(payload.scenes):
        scene_id = scene.id
        priority = 0 if i < HIGH_PRIORITY_COUNT else 1
        scene_data[scene_id] = scene.model_dump()
        scene_status[scene_id] = {"status": "queued", "url": None}
        job_queue.put((priority, scene_id))
        print(f"Queued scene {scene_id} with priority {priority}")
    return {"status": "success", "queued_scenes": len(payload.scenes)}


@app.get("/status")
def get_status():
    status_list = []
    for scene_id, status_info in scene_status.items():
        status_list.append({
            "id": scene_id,
            "status": status_info["status"],
            "url": status_info.get("url")
        })
    return {"scenes": status_list}