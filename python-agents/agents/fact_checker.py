from typing import Dict, Any, Optional, Literal
import os
import json
import re
import time
from datetime import datetime
from dotenv import load_dotenv

try:
    from openai import OpenAI
    from openai import AsyncOpenAI
except ImportError:
    OpenAI = None
    AsyncOpenAI = None

from supabase import create_client, Client

load_dotenv()


class FactCheckerAgent:
    """
    Agent responsible for fact-checking the draft content against research data.
    Returns pass/fail status for conditional routing in LangGraph.
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
    
    def _fact_check_content(self, draft_content: str, research_data: Dict[str, Any]) -> tuple[str, Literal["pass", "fail"], Dict[str, Any]]:
        """
        Perform fact-checking on draft content using research data.
        
        Args:
            draft_content: Draft content to fact-check
            research_data: Research findings to verify against
            
        Returns:
            Tuple of (fact_checked_content, status, issues_dict)
        """
        if not self.client:
            # Fallback if OpenAI client not available
            return draft_content, "pass", {"issues": [], "note": "Fact-checker not available"}
        
        # Prepare research context for verification
        research_context = ""
        if research_data:
            findings = research_data.get("findings", [])
            sources = research_data.get("sources", [])
            key_points = research_data.get("key_points", [])
            
            research_context = "Research Findings for Verification:\n\n"
            if key_points:
                research_context += "Key Points:\n"
                for i, point in enumerate(key_points[:10], 1):
                    research_context += f"{i}. {point}\n"
            
            if findings:
                research_context += "\nDetailed Findings:\n"
                for i, finding in enumerate(findings[:10], 1):
                    research_context += f"{i}. {finding.get('title', '')}\n"
                    research_context += f"   {finding.get('snippet', '')}\n"
                    research_context += f"   Source: {finding.get('source', '')}\n\n"
        
        # Construct fact-checking prompt
        prompt = f"""You are an expert fact-checker. Review the following blog post draft and verify all factual claims against the provided research data.

Blog Post Draft:
{draft_content}

{research_context}

Please:
1. Identify any factual claims, statistics, or statements in the draft
2. Verify each claim against the research data provided
3. Flag any claims that cannot be verified or contradict the research
4. Provide a corrected version of the content if issues are found
5. Determine if the content passes fact-checking (all verifiable claims are accurate) or fails (unverified or incorrect claims exist)

Respond in JSON format:
{{
    "status": "pass" or "fail",
    "issues": ["list of issues found"],
    "corrected_content": "corrected version of the content, or original if no changes needed",
    "verification_summary": "brief summary of what was checked"
}}"""

        try:
            # Check if model supports response_format (only newer models)
            model = os.getenv("LLM_MODEL", "gpt-4")
            supports_json_mode = any(x in model.lower() for x in [
                "gpt-4-turbo", "gpt-4-0125", "gpt-3.5-turbo-0125", 
                "gpt-4o", "gpt-4o-mini", "o1", "o3"
            ])
            
            # Build request parameters
            request_params = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a meticulous fact-checker. Always respond with valid JSON only, no additional text."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            # Only add response_format if model supports it
            if supports_json_mode:
                request_params["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**request_params)
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if response_format wasn't used
            if not supports_json_mode:
                # Try to find JSON in the response (might have extra text)
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(0)
            
            result = json.loads(result_text)
            
            status = result.get("status", "fail").lower()
            if status not in ["pass", "fail"]:
                status = "fail"
            
            fact_checked_content = result.get("corrected_content", draft_content)
            
            # Ensure we always return valid content
            if not fact_checked_content or fact_checked_content.strip() == "" or fact_checked_content == "N/A":
                fact_checked_content = draft_content
            
            issues = result.get("issues", [])
            
            return fact_checked_content, status, {
                "issues": issues,
                "verification_summary": result.get("verification_summary", ""),
                "status": status
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing fact-check JSON: {str(e)}")
            print(f"Response was: {result_text[:200]}...")
            # On JSON error, return original draft and fail
            return draft_content, "fail", {"issues": [f"JSON parsing error: {str(e)}"], "status": "fail"}
        except Exception as e:
            print(f"Error in fact-checking: {str(e)}")
            # On error, fail the check to trigger rewrite, but return the draft content
            return draft_content, "fail", {"issues": [f"Fact-check error: {str(e)}"], "status": "fail"}
    
    async def _fact_check_content_async(self, draft_content: str, research_data: Dict[str, Any]) -> tuple[str, Literal["pass", "fail"], Dict[str, Any]]:
        """
        Async version of fact-checking.
        
        Args:
            draft_content: Draft content to fact-check
            research_data: Research findings to verify against
            
        Returns:
            Tuple of (fact_checked_content, status, issues_dict)
        """
        if not self.async_client:
            # Fallback if async client not available
            return draft_content, "pass", {"issues": [], "note": "Fact-checker not available"}
        
        # Prepare research context for verification
        research_context = ""
        if research_data:
            findings = research_data.get("findings", [])
            key_points = research_data.get("key_points", [])
            
            research_context = "Research Findings for Verification:\n\n"
            if key_points:
                research_context += "Key Points:\n"
                for i, point in enumerate(key_points[:10], 1):
                    research_context += f"{i}. {point}\n"
            
            if findings:
                research_context += "\nDetailed Findings:\n"
                for i, finding in enumerate(findings[:10], 1):
                    research_context += f"{i}. {finding.get('title', '')}\n"
                    research_context += f"   {finding.get('snippet', '')}\n\n"
        
        # Construct fact-checking prompt
        prompt = f"""You are an expert fact-checker. Review the following blog post draft and verify all factual claims against the provided research data.

Blog Post Draft:
{draft_content}

{research_context}

Please:
1. Identify any factual claims, statistics, or statements in the draft
2. Verify each claim against the research data provided
3. Flag any claims that cannot be verified or contradict the research
4. Provide a corrected version of the content if issues are found
5. Determine if the content passes fact-checking (all verifiable claims are accurate) or fails (unverified or incorrect claims exist)

Respond in JSON format:
{{
    "status": "pass" or "fail",
    "issues": ["list of issues found"],
    "corrected_content": "corrected version of the content, or original if no changes needed",
    "verification_summary": "brief summary of what was checked"
}}"""

        try:
            # Check if model supports response_format (only newer models)
            model = os.getenv("LLM_MODEL", "gpt-4")
            supports_json_mode = any(x in model.lower() for x in [
                "gpt-4-turbo", "gpt-4-0125", "gpt-3.5-turbo-0125", 
                "gpt-4o", "gpt-4o-mini", "o1", "o3"
            ])
            
            # Build request parameters
            request_params = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a meticulous fact-checker. Always respond with valid JSON only, no additional text."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            # Only add response_format if model supports it
            if supports_json_mode:
                request_params["response_format"] = {"type": "json_object"}
            
            response = await self.async_client.chat.completions.create(**request_params)
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if response_format wasn't used
            if not supports_json_mode:
                # Try to find JSON in the response (might have extra text)
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(0)
            
            result = json.loads(result_text)
            
            status = result.get("status", "fail").lower()
            if status not in ["pass", "fail"]:
                status = "fail"
            
            fact_checked_content = result.get("corrected_content", draft_content)
            
            # Ensure we always return valid content
            if not fact_checked_content or fact_checked_content.strip() == "" or fact_checked_content == "N/A":
                fact_checked_content = draft_content
            
            issues = result.get("issues", [])
            
            return fact_checked_content, status, {
                "issues": issues,
                "verification_summary": result.get("verification_summary", ""),
                "status": status
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing fact-check JSON: {str(e)}")
            print(f"Response was: {result_text[:200]}...")
            # On JSON error, return original draft and fail
            return draft_content, "fail", {"issues": [f"JSON parsing error: {str(e)}"], "status": "fail"}
        except Exception as e:
            print(f"Error in fact-checking: {str(e)}")
            # On error, fail the check to trigger rewrite, but return the draft content
            return draft_content, "fail", {"issues": [f"Fact-check error: {str(e)}"], "status": "fail"}
    
    def _log_to_supabase(
        self,
        draft_content: str,
        fact_checked_content: str,
        status: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Log fact-checker outputs and metrics to Supabase.
        
        Schema: id (int8), agent (text), input (text), output (text), 
                timestamp (timestamptz), metadata (json)
        
        Args:
            draft_content: Original draft (input)
            fact_checked_content: Fact-checked content (output)
            status: Pass or fail status
            metrics: Performance metrics
        """
        if not self.supabase:
            return
        
        try:
            # Prepare log entry matching the schema
            log_entry = {
                "agent": "fact_checker",
                "input": draft_content[:5000] if len(draft_content) > 5000 else draft_content,
                "output": fact_checked_content[:10000] if len(fact_checked_content) > 10000 else fact_checked_content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "status": status,
                    "input_length": len(draft_content),
                    "output_length": len(fact_checked_content),
                    **metrics  # Include all metrics in metadata
                }
            }
            
            # Insert into Supabase agent_logs table
            response = self.supabase.table("agent_logs").insert(log_entry).execute()
            
            if response.data:
                print(f"Fact-checker logged to Supabase: {len(response.data)} record(s)")
        except Exception as e:
            print(f"Error logging to Supabase: {str(e)}")
            # Don't fail the fact-check if logging fails
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous fact-checking execution.
        
        Args:
            state: Current workflow state containing draft_content and research_data
            
        Returns:
            Updated state with fact_checked_content and fact_check_status
        """
        import time
        start_time = time.time()
        
        draft_content = state.get("draft_content", "")
        research_data = state.get("research_data", {})
        current_iterations = state.get("fact_check_iterations", 0)
        
        print(f"Fact-checking draft content (iteration {current_iterations + 1})...")
        
        # Perform fact-checking
        fact_checked_content, status, issues = self._fact_check_content(draft_content, research_data)
        
        # Update iteration count
        new_iterations = current_iterations + 1
        
        # Calculate metrics
        elapsed_time = time.time() - start_time
        metrics = {
            "execution_time_seconds": elapsed_time,
            "status": status,
            "issues_count": len(issues.get("issues", [])),
            "issues": issues.get("issues", []),
            "verification_summary": issues.get("verification_summary", ""),
            "iteration": new_iterations
        }
        
        # Log to Supabase
        self._log_to_supabase(draft_content, fact_checked_content, status, metrics)
        
        status_emoji = "✅" if status == "pass" else "❌"
        print(f"{status_emoji} Fact-check {status}: {len(issues.get('issues', []))} issues found, {elapsed_time:.2f}s")
        
        # Update state
        state["fact_checked_content"] = fact_checked_content
        state["fact_check_status"] = status
        state["fact_check_iterations"] = new_iterations
        
        return state
    
    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous fact-checking execution.
        
        Args:
            state: Current workflow state containing draft_content and research_data
            
        Returns:
            Updated state with fact_checked_content and fact_check_status
        """
        import asyncio
        import time
        start_time = time.time()
        
        draft_content = state.get("draft_content", "")
        research_data = state.get("research_data", {})
        current_iterations = state.get("fact_check_iterations", 0)
        
        print(f"Fact-checking draft content (iteration {current_iterations + 1})...")
        
        # Perform fact-checking
        fact_checked_content, status, issues = await self._fact_check_content_async(draft_content, research_data)
        
        # Update iteration count
        new_iterations = current_iterations + 1
        
        # Calculate metrics
        elapsed_time = time.time() - start_time
        metrics = {
            "execution_time_seconds": elapsed_time,
            "status": status,
            "issues_count": len(issues.get("issues", [])),
            "issues": issues.get("issues", []),
            "verification_summary": issues.get("verification_summary", ""),
            "iteration": new_iterations
        }
        
        # Log to Supabase (run in executor to avoid blocking)
        if self.supabase:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._log_to_supabase,
                draft_content,
                fact_checked_content,
                status,
                metrics
            )
        
        status_emoji = "✅" if status == "pass" else "❌"
        print(f"{status_emoji} Fact-check {status}: {len(issues.get('issues', []))} issues found, {elapsed_time:.2f}s")
        
        # Update state
        state["fact_checked_content"] = fact_checked_content
        state["fact_check_status"] = status
        state["fact_check_iterations"] = new_iterations
        
        return state

