from fastapi import FastAPI, Request
from google.cloud import storage
from google.adk.runners import InMemoryRunner
from google.genai import types
from transcript_agent.agent import root_agent

# 1. Pure, lightweight FastAPI server
app = FastAPI()

@app.post("/")
async def eventarc_webhook(request: Request):
    """Listens for Cloud Storage file finalization events."""
    headers = request.headers
    
    # Extract bucket and file name
    bucket_name = headers.get("ce-source").split("buckets/")[1]
    file_name = headers.get("ce-subject").split("objects/")[1]  
    
    # Download the transcript
    client = storage.Client()
    blob = client.bucket(bucket_name).blob(file_name)
    transcript_text = blob.download_as_text()
    
    # 2. Spin up the AI Runner directly inside the webhook 
    runner = InMemoryRunner(agent=root_agent, app_name="transcript_app")
    
    # 3. Explicitly create a unique session for this specific file
    session_id = f"session-{file_name.replace('/', '-')}"
    await runner.session_service.create_session(
        app_name="transcript_app",
        user_id="webhook_system",
        session_id=session_id
    )
    
    # 4. Create a strictly typed Google GenAI Content object
    user_message = types.Content(
        role="user", 
        parts=[types.Part(text=f"Please process this transcript:\n\n{transcript_text}")]
    )
    
    # 5. Stream the typed message and print the events!
    async for event in runner.run_async(
        user_id="webhook_system",
        session_id=session_id,
        new_message=user_message
    ):
        # This pushes the AI's internal dialogue and tool errors to your logs
        print(f"ADK EVENT: {event}")
        
    return {"status": f"Tasks extracted successfully for {file_name}"}