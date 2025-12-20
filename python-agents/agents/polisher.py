from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


class PolisherAgent:
    """
    Agent responsible for polishing and refining the final content.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        # Initialize your LLM client here
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous polishing execution.
        
        Args:
            state: Current workflow state containing fact_checked_content
            
        Returns:
            Updated state with final_content
        """
        fact_checked_content = state.get("fact_checked_content", "")
        draft_content = state.get("draft_content", "")
        style = state.get("style", "professional")
        target_length = state.get("target_length", 1000)
        
        # Use fact_checked_content if available, otherwise fall back to draft_content
        # This handles cases where fact-check failed but we proceed anyway
        content_to_polish = fact_checked_content if fact_checked_content and fact_checked_content.strip() and fact_checked_content != "N/A" else draft_content
        
        if not content_to_polish or content_to_polish.strip() == "" or content_to_polish == "N/A":
            print("Warning: No valid content to polish, using draft content")
            content_to_polish = draft_content
        
        # For now, just return the content as-is (polisher is a placeholder)
        # TODO: Implement actual polishing with LLM
        final_content = content_to_polish
        
        state["final_content"] = final_content
        state["metadata"] = {
            "word_count": len(final_content.split()) if final_content else 0,
            "style": style,
            "status": "completed"
        }
        
        return state
    
    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous polishing execution.
        
        Args:
            state: Current workflow state containing fact_checked_content
            
        Returns:
            Updated state with final_content
        """
        fact_checked_content = state.get("fact_checked_content", "")
        draft_content = state.get("draft_content", "")
        style = state.get("style", "professional")
        target_length = state.get("target_length", 1000)
        
        # Use fact_checked_content if available, otherwise fall back to draft_content
        # This handles cases where fact-check failed but we proceed anyway
        content_to_polish = fact_checked_content if fact_checked_content and fact_checked_content.strip() and fact_checked_content != "N/A" else draft_content
        
        if not content_to_polish or content_to_polish.strip() == "" or content_to_polish == "N/A":
            print("Warning: No valid content to polish, using draft content")
            content_to_polish = draft_content
        
        # For now, just return the content as-is (polisher is a placeholder)
        # TODO: Implement actual polishing with LLM
        final_content = content_to_polish
        
        state["final_content"] = final_content
        state["metadata"] = {
            "word_count": len(final_content.split()) if final_content else 0,
            "style": style,
            "status": "completed"
        }
        
        return state

