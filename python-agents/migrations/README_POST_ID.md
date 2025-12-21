# Post ID Linking Migration

## Overview

This migration adds a `post_id` column to the `agent_logs` table to properly link agent logs to their corresponding posts. This replaces the previous method of matching logs by PRD content and timestamp proximity.

## Migration Steps

1. **Run the migration in Supabase SQL Editor:**
   - Go to your Supabase Dashboard
   - Navigate to SQL Editor
   - Run the migration file: `003_add_post_id_to_agent_logs.sql`

2. **What the migration does:**
   - Adds a nullable `post_id` column to `agent_logs` table
   - Creates an index on `post_id` for faster queries
   - The column is nullable to maintain backward compatibility with existing logs

## How It Works

### Before (Old Behavior)
- Agent logs were not linked to posts
- Timeline API had to match logs by:
  - Finding writer logs where input matched the PRD
  - Finding all logs within a 30-minute time window
  - This was unreliable and could match logs to wrong posts

### After (New Behavior)
- When a workflow starts, a post entry is created first (with empty `final_post`)
- The `post_id` is passed through the workflow state
- All agents log with the `post_id`
- After workflow completes, the post is updated with the final content
- Timeline API simply queries logs by `post_id`

## Code Changes

1. **Workflow State**: Added `post_id` field
2. **main.py**: Creates post first, passes `post_id` through workflow, updates post at end
3. **All Agents**: Updated to accept and use `post_id` when logging
4. **Timeline API**: Simplified to query by `post_id` directly

## Backward Compatibility

- Existing logs (created before this migration) will have `post_id = NULL`
- These logs will not appear in timeline views for new posts
- Old posts may show a warning message if no logs are found
- You can optionally backfill `post_id` for old logs if needed

## Testing

After running the migration:
1. Generate a new post using the API
2. Check that the post is created in Supabase
3. Check that all agent logs have the correct `post_id`
4. View the timeline - it should show all logs for that post

