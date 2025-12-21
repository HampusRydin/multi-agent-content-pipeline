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


class WriterAgent:
    """
    Agent responsible for writing blog post drafts based on PRD (Product Requirements Document)
    and research data. Logs outputs and metrics to Supabase.
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
    
    def _extract_prd(self, state: Dict[str, Any]) -> str:
        """
        Extract PRD from state. Can be in 'prd' field or within research_data.
        
        Args:
            state: Current workflow state
            
        Returns:
            PRD content as string
        """
        # Check for explicit PRD field
        prd = state.get("prd", "")
        if prd:
            return prd
        
        # Check if PRD is in research_data
        research_data = state.get("research_data", {})
        if isinstance(research_data, dict):
            prd = research_data.get("prd", "")
            if prd:
                return prd
        
        # If no PRD found, use research findings as context
        if isinstance(research_data, dict):
            findings = research_data.get("findings", [])
            key_points = research_data.get("key_points", [])
            
            prd_context = ""
            if key_points:
                prd_context = "\n".join(key_points[:5])  # Use top 5 key points
            elif findings:
                prd_context = "\n".join([f.get("snippet", "") for f in findings[:3]])
            
            return prd_context if prd_context else "No PRD or research data provided"
        
        return "No PRD or research data provided"
    
    def _generate_blog_post(self, prd: str, topic: str, target_length: int, style: str, research_data: Dict[str, Any]) -> str:
        """
        Generate blog post draft using LLM based on PRD and research data.
        
        Args:
            prd: Product Requirements Document
            topic: Blog post topic
            target_length: Target word count
            style: Writing style
            research_data: Research findings for context
            
        Returns:
            Generated blog post draft
        """
        if not self.client:
            # Fallback if OpenAI client not available
            return f"# {topic}\n\n[Blog post draft based on PRD]\n\nPRD Content:\n{prd[:500]}..."
        
        # Prepare research context
        research_context = ""
        if research_data:
            findings = research_data.get("findings", [])
            sources = research_data.get("sources", [])
            
            if findings:
                research_context = "\n\nResearch Findings:\n"
                for i, finding in enumerate(findings[:5], 1):
                    research_context += f"{i}. {finding.get('title', '')}: {finding.get('snippet', '')}\n"
        
        # Construct prompt
        prompt = f"""You are an expert blog post writer. Create a compelling blog post draft based on the following Product Requirements Document (PRD) and research findings.

Topic: {topic}
Target Length: Approximately {target_length} words
Writing Style: {style}

PRD (Product Requirements Document):
{prd}
{research_context}

Please create a well-structured blog post draft that:
1. Has an engaging introduction that hooks the reader
2. Clearly explains the product/feature based on the PRD
3. Incorporates relevant information from the research findings
4. Uses a {style} writing style
5. Has a strong conclusion
6. Is approximately {target_length} words

Format the response as markdown with appropriate headings, subheadings, and paragraphs."""

        try:
            # Calculate max_tokens: roughly 1.3 tokens per word for English text
            # Add buffer for markdown formatting
            estimated_tokens = int(target_length * 1.3) + 200  # Extra buffer for formatting
            
            response = self.client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an expert technical writer who creates comprehensive, detailed blog posts. Always meet the target word count exactly. Never abbreviate or summarize - write the full content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=estimated_tokens
            )
            
            draft_content = response.choices[0].message.content
            return draft_content.strip()
        except Exception as e:
            print(f"Error generating blog post: {str(e)}")
            # Fallback content
            return f"# {topic}\n\n[Error generating content: {str(e)}]\n\nPRD:\n{prd[:500]}"
    
    async def _generate_blog_post_async(self, prd: str, topic: str, target_length: int, style: str, research_data: Dict[str, Any]) -> str:
        """
        Async version of blog post generation.
        
        Args:
            prd: Product Requirements Document
            topic: Blog post topic
            target_length: Target word count
            style: Writing style
            research_data: Research findings for context
            
        Returns:
            Generated blog post draft
        """
        if not self.async_client:
            # Fallback if async client not available
            return f"# {topic}\n\n[Blog post draft based on PRD]\n\nPRD Content:\n{prd[:500]}..."
        
        # Prepare research context
        research_context = ""
        if research_data:
            findings = research_data.get("findings", [])
            
            if findings:
                research_context = "\n\nResearch Findings:\n"
                for i, finding in enumerate(findings[:5], 1):
                    research_context += f"{i}. {finding.get('title', '')}: {finding.get('snippet', '')}\n"
        
        # Construct prompt
        prompt = f"""You are an expert blog post writer. Create a compelling blog post draft based on the following Product Requirements Document (PRD) and research findings.

CRITICAL REQUIREMENTS:
- Target length: EXACTLY {target_length} words (aim for {target_length} words, not less)
- Writing style: {style}
- Topic: {topic}

PRD (Product Requirements Document) - THIS IS YOUR PRIMARY SOURCE:
{prd}
{research_context if research_context else "Note: Limited research data available. Focus on the PRD content."}

Your blog post MUST:
1. Start with a compelling introduction (100-150 words) that hooks the reader and introduces the topic
2. Dedicate the main body (500-600 words) to explaining the product/feature in detail based on the PRD:
   - What the product/feature is
   - Key features and capabilities from the PRD
   - How it works
   - Who it's for (target audience from PRD)
   - Benefits and value proposition
3. Include relevant information from research findings if available
4. End with a strong conclusion (100-150 words) that summarizes key points
5. Use {style} writing style throughout
6. Be EXACTLY around {target_length} words - this is critical

Format as markdown with clear headings (H2 for main sections, H3 for subsections) and well-structured paragraphs.
Write the full blog post now - do not summarize or abbreviate."""

        try:
            # Calculate max_tokens: roughly 1.3 tokens per word for English text
            # Add buffer for markdown formatting
            estimated_tokens = int(target_length * 1.3) + 200  # Extra buffer for formatting
            
            response = await self.async_client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an expert technical writer who creates comprehensive, detailed blog posts. Always meet the target word count exactly. Never abbreviate or summarize - write the full content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=estimated_tokens
            )
            
            draft_content = response.choices[0].message.content
            return draft_content.strip()
        except Exception as e:
            print(f"Error generating blog post: {str(e)}")
            # Fallback content
            return f"# {topic}\n\n[Error generating content: {str(e)}]\n\nPRD:\n{prd[:500]}"
    
    def _log_to_supabase(
        self,
        prd: str,
        draft_content: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Log writer outputs and metrics to Supabase.
        
        Schema: id (int8), agent (text), input (text), output (text), 
                timestamp (timestamptz), metadata (json)
        
        Args:
            prd: Product Requirements Document (input)
            draft_content: Generated blog post draft (output)
            metrics: Performance metrics (timing, word count, etc.)
        """
        if not self.supabase:
            return
        
        try:
            # Prepare log entry matching the schema
            log_entry = {
                "agent": "writer",
                "input": prd[:5000] if len(prd) > 5000 else prd,  # Limit input length
                "output": draft_content[:10000] if len(draft_content) > 10000 else draft_content,  # Limit output length
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "word_count": len(draft_content.split()),
                    "prd_length": len(prd),
                    "draft_length": len(draft_content),
                    **metrics  # Include all metrics in metadata
                }
            }
            
            # Insert into Supabase agent_logs table
            response = self.supabase.table("agent_logs").insert(log_entry).execute()
            
            if response.data:
                print(f"Writer logged to Supabase: {len(response.data)} record(s)")
        except Exception as e:
            print(f"Error logging to Supabase: {str(e)}")
            # Don't fail the writing if logging fails
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous writing execution.
        
        Args:
            state: Current workflow state containing research_data and optionally prd
            
        Returns:
            Updated state with draft_content
        """
        import time
        start_time = time.time()
        
        research_data = state.get("research_data", {})
        topic = state.get("topic", "")
        target_length = state.get("target_length", 1000)
        style = state.get("style", "professional")
        
        print(f"Writing blog post draft for topic: {topic}")
        
        # Extract PRD from state
        prd = self._extract_prd(state)
        
        # Generate blog post draft
        draft_content = self._generate_blog_post(prd, topic, target_length, style, research_data)
        
        # Calculate metrics
        elapsed_time = time.time() - start_time
        word_count = len(draft_content.split())
        metrics = {
            "execution_time_seconds": elapsed_time,
            "word_count": word_count,
            "target_length": target_length,
            "style": style,
            "prd_provided": bool(prd and prd != "No PRD or research data provided")
        }
        
        # Log to Supabase
        self._log_to_supabase(prd, draft_content, metrics)
        
        print(f"Blog post draft completed: {word_count} words, {elapsed_time:.2f}s")
        
        state["draft_content"] = draft_content
        return state
    
    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous writing execution.
        
        Args:
            state: Current workflow state containing research_data and optionally prd
            
        Returns:
            Updated state with draft_content
        """
        import asyncio
        import time
        start_time = time.time()
        
        research_data = state.get("research_data", {})
        topic = state.get("topic", "")
        target_length = state.get("target_length", 1000)
        style = state.get("style", "professional")
        
        print(f"Writing blog post draft for topic: {topic}")
        
        # Extract PRD from state
        prd = self._extract_prd(state)
        
        # Generate blog post draft
        draft_content = await self._generate_blog_post_async(prd, topic, target_length, style, research_data)
        
        # Calculate metrics
        elapsed_time = time.time() - start_time
        word_count = len(draft_content.split())
        metrics = {
            "execution_time_seconds": elapsed_time,
            "word_count": word_count,
            "target_length": target_length,
            "style": style,
            "prd_provided": bool(prd and prd != "No PRD or research data provided")
        }
        
        # Log to Supabase (run in executor to avoid blocking)
        if self.supabase:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._log_to_supabase,
                prd,
                draft_content,
                metrics
            )
        
        print(f"Blog post draft completed: {word_count} words, {elapsed_time:.2f}s")
        
        state["draft_content"] = draft_content
        return state

