from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from graph import create_workflow

# Load environment variables
load_dotenv()

app = FastAPI(title="Multi-Agent Content Pipeline API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the workflow
workflow = create_workflow()


class ContentRequest(BaseModel):
    topic: str
    target_length: Optional[int] = None
    style: Optional[str] = None


class ContentResponse(BaseModel):
    content: str
    status: str
    metadata: Optional[dict] = None


@app.get("/")
async def root():
    return {"message": "Multi-Agent Content Pipeline API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """
    Generate content using the multi-agent pipeline.
    """
    try:
        # Run the workflow with the provided topic
        result = await workflow.ainvoke({
            "topic": request.topic,
            "target_length": request.target_length,
            "style": request.style or "professional"
        })
        
        return ContentResponse(
            content=result.get("final_content", ""),
            status="success",
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        return ContentResponse(
            content="",
            status=f"error: {str(e)}",
            metadata=None
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

