from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from supabase import create_client, Client

from graph import create_workflow_async
from load_env import load_environment

# Load environment variables (from root .env or local .env)
load_environment()

app = FastAPI(title="Multi-Agent Content Pipeline API")

# Initialize Supabase client for posts table
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
else:
    print("Warning: Supabase credentials not found. Posts will not be saved.")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the async workflow
workflow = create_workflow_async()


class ContentRequest(BaseModel):
    prd: str  # Product Requirements Document
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
        # Run the workflow with PRD and topic
        result = await workflow.ainvoke({
            "prd": request.prd,
            "topic": request.topic,
            "target_length": request.target_length or 1000,
            "style": request.style or "professional",
            "fact_check_iterations": 0  # Initialize iteration counter
        })
        
        final_content = result.get("final_content", "")
        
        # Save to posts table in Supabase
        print(f"Attempting to save post to Supabase...")
        print(f"Supabase client initialized: {supabase is not None}")
        print(f"Final content length: {len(final_content) if final_content else 0}")
        
        if not supabase:
            print("Warning: Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY in .env")
        elif not final_content or final_content.strip() == "":
            print("Warning: Final content is empty, skipping post save")
        else:
            try:
                post_entry = {
                    "prd": request.prd,
                    "final_post": final_content
                }
                print(f"Saving post entry (PRD length: {len(request.prd)}, Post length: {len(final_content)})...")
                response = supabase.table("posts").insert(post_entry).execute()
                
                if response.data:
                    print(f"\033[92m[SUCCESS]\033[0m Post saved to Supabase: {len(response.data)} record(s)")
                    print(f"Saved post ID: {response.data[0].get('id', 'unknown')}")
                else:
                    print("\033[93m[WARNING]\033[0m No data returned from Supabase insert")
                    print(f"Response: {response}")
                    # Check for RLS or permission errors
                    if hasattr(response, 'error') and response.error:
                        print(f"Supabase error: {response.error}")
            except Exception as e:
                error_msg = str(e)
                print(f"\033[91m[ERROR]\033[0m Error saving post to Supabase: {error_msg}")
                
                # Check for common Supabase errors
                if "permission" in error_msg.lower() or "policy" in error_msg.lower() or "rls" in error_msg.lower():
                    print("\n\033[93m[WARNING]\033[0m This looks like a Row Level Security (RLS) issue.")
                    print("   Check your Supabase table policies:")
                    print("   1. Go to Supabase Dashboard > Table Editor > posts")
                    print("   2. Click 'Policies' tab")
                    print("   3. Ensure INSERT policy allows your service role key")
                    print("   4. Or disable RLS temporarily for testing")
                
                import traceback
                traceback.print_exc()
                # Don't fail the request if saving fails
        
        return ContentResponse(
            content=final_content,
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

