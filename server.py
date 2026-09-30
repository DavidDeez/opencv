from fastapi import FastAPI
from fastapi.responses import JSONResponse
from main import run_test

app = FastAPI(title="OpenCV Agentic Vision Endpoint")

@app.get("/")
def read_root():
    return {
        "status": "online", 
        "project": "OpenCV AI Competition 2026",
        "message": "Agent is standing by. Visit /run-agent to trigger the workflow."
    }

@app.get("/run-agent")
async def trigger_agent():
    try:
        # Trigger the Agentic Loop and get the logs
        logs = await run_test()
        return {
            "status": "success", 
            "agent_logs": logs
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
