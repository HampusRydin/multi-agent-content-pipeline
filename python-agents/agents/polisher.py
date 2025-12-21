from typing import Dict, Any, Optional
import os
import json
import time
from datetime import datetime

try:
    from openai import OpenAI
    from openai import AsyncOpenAI
except ImportError:
    OpenAI = None
    AsyncOpenAI = None

from supabase import create_client, Client

from load_env import load_environment

load_environment()


class PolisherAgent:
    """
    Agent responsible for polishing and refining the final content.
    Logs outputs and metrics to Supabase.
    """
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Initialize OpenAI client if available
        if self.openai_key and OpenAI:
            self.client = OpenAI(api_key=self.openai_key)
            self.async_client = AsyncOpenAI(api_key=self.openai_key) if AsyncOpenAI else None
        else:
            self.client = None
            self.async_client = None
            print("Warning: OpenAI client not available. Install openai package: pip install openai")
        
        # Initialize Supabase client for logging
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            self.supabase: Optional[Client] = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None
            print("Warning: Supabase credentials not found. Logging will be skipped.")
    
    def _polish_content(self, content: str, style: str, target_length: int) -> str:
        """
        Polish and refine content using LLM.
        
        Args:
            content: Content to polish
            style: Writing style
            target_length: Target word count
            
        Returns:
            Polished content
        """
        if not self.client:
            # Fallback if OpenAI client not available
            return content
        
        prompt = f"""You are an expert editor and content polisher. Refine and polish the following blog post to make it publication-ready.

Target Style: {style}
Target Length: Approximately {target_length} words

Blog Post to Polish:
{content}

Please:
1. Improve readability and flow
2. Enhance the {style} writing style and tone
3. Fix any grammar, spelling, or punctuation errors
4. Optimize sentence structure and paragraph flow
5. Ensure the content meets the target length ({target_length} words)
6. Make the introduction more engaging if needed
7. Strengthen the conclusion
8. Ensure consistent formatting and markdown structure
9. Maintain all factual content - only improve presentation

Return the polished version of the blog post. Keep the same markdown structure and headings."""

        try:
            response = self.client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an expert editor who polishes content to publication quality while maintaining accuracy and factual information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(target_length * 1.3) + 200
            )
            
            polished_content = response.choices[0].message.content
            return polished_content.strip()
        except Exception as e:
            print(f"Error polishing content: {str(e)}")
            # Return original content on error
            return content
    
    async def _polish_content_async(self, content: str, style: str, target_length: int) -> str:
        """
        Async version of content polishing.
        
        Args:
            content: Content to polish
            style: Writing style
            target_length: Target word count
            
        Returns:
            Polished content
        """
        if not self.async_client:
            # Fallback if async client not available
            return content
        
        prompt = f"""You are an expert editor and content polisher. Refine and polish the following blog post to make it publication-ready.

Target Style: {style}
Target Length: Approximately {target_length} words

Blog Post to Polish:
{content}

Please:
1. Improve readability and flow
2. Enhance the {style} writing style and tone
3. Fix any grammar, spelling, or punctuation errors
4. Optimize sentence structure and paragraph flow
5. Ensure the content meets the target length ({target_length} words)
6. Make the introduction more engaging if needed
7. Strengthen the conclusion
8. Ensure consistent formatting and markdown structure
9. Maintain all factual content - only improve presentation

Return the polished version of the blog post. Keep the same markdown structure and headings."""

        try:
            response = await self.async_client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an expert editor who polishes content to publication quality while maintaining accuracy and factual information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(target_length * 1.3) + 200
            )
            
            polished_content = response.choices[0].message.content
            return polished_content.strip()
        except Exception as e:
            print(f"Error polishing content: {str(e)}")
            # Return original content on error
            return content
    
    def _log_to_supabase(
        self,
        input_content: str,
        polished_content: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Log polisher outputs and metrics to Supabase.
        
        Schema: id (int8), agent (text), input (text), output (text), 
                timestamp (timestamptz), metadata (json)
        
        Args:
            input_content: Content before polishing (input)
            polished_content: Polished content (output)
            metrics: Performance metrics
        """
        if not self.supabase:
            return
        
        try:
            # Prepare log entry matching the schema
            log_entry = {
                "agent": "polisher",
                "input": input_content[:5000] if len(input_content) > 5000 else input_content,
                "output": polished_content[:10000] if len(polished_content) > 10000 else polished_content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "input_length": len(input_content),
                    "output_length": len(polished_content),
                    "input_word_count": len(input_content.split()),
                    "output_word_count": len(polished_content.split()),
                    **metrics  # Include all metrics in metadata
                }
            }
            
            # Insert into Supabase agent_logs table
            response = self.supabase.table("agent_logs").insert(log_entry).execute()
            
            if response.data:
                print(f"Polisher logged to Supabase: {len(response.data)} record(s)")
        except Exception as e:
            print(f"Error logging to Supabase: {str(e)}")
            # Don't fail the polishing if logging fails
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous polishing execution.
        
        Args:
            state: Current workflow state containing fact_checked_content
            
        Returns:
            Updated state with final_content
        """
        import time
        start_time = time.time()
        
        fact_checked_content = state.get("fact_checked_content", "")
        draft_content = state.get("draft_content", "")
        style = state.get("style", "professional")
        target_length = state.get("target_length", 1000)
        
        print(f"Polishing final content...")
        
        # Use fact_checked_content if available, otherwise fall back to draft_content
        # This handles cases where fact-check failed but we proceed anyway
        content_to_polish = fact_checked_content if fact_checked_content and fact_checked_content.strip() and fact_checked_content != "N/A" else draft_content
        
        if not content_to_polish or content_to_polish.strip() == "" or content_to_polish == "N/A":
            print("Warning: No valid content to polish, using draft content")
            content_to_polish = draft_content
        
        # Polish the content
        final_content = self._polish_content(content_to_polish, style, target_length)
        
        # Calculate metrics
        elapsed_time = time.time() - start_time
        word_count = len(final_content.split()) if final_content else 0
        metrics = {
            "execution_time_seconds": elapsed_time,
            "word_count": word_count,
            "target_length": target_length,
            "style": style
        }
        
        # Log to Supabase
        self._log_to_supabase(content_to_polish, final_content, metrics)
        
        print(f"Polishing completed: {word_count} words, {elapsed_time:.2f}s")
        
        state["final_content"] = final_content
        state["metadata"] = {
            "word_count": word_count,
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
        import asyncio
        import time
        start_time = time.time()
        
        fact_checked_content = state.get("fact_checked_content", "")
        draft_content = state.get("draft_content", "")
        style = state.get("style", "professional")
        target_length = state.get("target_length", 1000)
        
        print(f"Polishing final content...")
        
        # Use fact_checked_content if available, otherwise fall back to draft_content
        # This handles cases where fact-check failed but we proceed anyway
        content_to_polish = fact_checked_content if fact_checked_content and fact_checked_content.strip() and fact_checked_content != "N/A" else draft_content
        
        if not content_to_polish or content_to_polish.strip() == "" or content_to_polish == "N/A":
            print("Warning: No valid content to polish, using draft content")
            content_to_polish = draft_content
        
        # Polish the content
        final_content = await self._polish_content_async(content_to_polish, style, target_length)
        
        # Calculate metrics
        elapsed_time = time.time() - start_time
        word_count = len(final_content.split()) if final_content else 0
        metrics = {
            "execution_time_seconds": elapsed_time,
            "word_count": word_count,
            "target_length": target_length,
            "style": style
        }
        
        # Log to Supabase (run in executor to avoid blocking)
        if self.supabase:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._log_to_supabase,
                content_to_polish,
                final_content,
                metrics
            )
        
        print(f"Polishing completed: {word_count} words, {elapsed_time:.2f}s")
        
        state["final_content"] = final_content
        state["metadata"] = {
            "word_count": word_count,
            "style": style,
            "status": "completed"
        }
        
        return state

