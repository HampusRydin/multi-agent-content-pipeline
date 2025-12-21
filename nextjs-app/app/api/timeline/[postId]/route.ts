import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_KEY || process.env.SUPABASE_KEY;

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ postId: string }> }
) {
  try {
    const { postId } = await params;
    
    if (!SUPABASE_URL || !SUPABASE_KEY) {
      return NextResponse.json(
        { error: 'Supabase credentials not configured' },
        { status: 500 }
      );
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

    // Fetch the post
    const { data: post, error: postError } = await supabase
      .from('posts')
      .select('*')
      .eq('id', postId)
      .single();

    if (postError || !post) {
      return NextResponse.json(
        { error: 'Post not found' },
        { status: 404 }
      );
    }

    // Fetch all agent_logs
    // Since there's no direct post_id link, we'll match logs by:
    // 1. Finding writer logs where input matches the PRD
    // 2. Then finding all logs within a time window of those writer logs
    const { data: allLogs, error: logsError } = await supabase
      .from('agent_logs')
      .select('*')
      .order('timestamp', { ascending: true });

    if (logsError) {
      return NextResponse.json(
        { error: 'Failed to fetch agent logs' },
        { status: 500 }
      );
    }

    // Find writer logs that match this post's PRD
    const postPRD = post.prd.trim();
    const matchingWriterLogs = allLogs?.filter((log) => {
      if (log.agent === 'writer') {
        const logInput = log.input.trim();
        // Match if PRD and input are very similar
        // Check for exact match or significant overlap
        if (logInput === postPRD) return true;
        // Check if they share a significant portion (at least 50 chars overlap)
        const minLength = Math.min(logInput.length, postPRD.length);
        if (minLength < 50) return logInput === postPRD;
        // Check if one contains a substantial portion of the other
        return logInput.includes(postPRD.substring(0, Math.min(200, postPRD.length))) ||
               postPRD.includes(logInput.substring(0, Math.min(200, logInput.length)));
      }
      return false;
    }) || [];

    if (matchingWriterLogs.length === 0) {
      // If no exact match, try to find logs by timestamp proximity
      // This is a fallback - ideally we'd have a post_id in agent_logs
      return NextResponse.json({
        post,
        logs: [],
        groupedLogs: [],
        warning: 'No matching agent logs found for this post'
      });
    }

    // Get the time range of matching writer logs
    const timestamps = matchingWriterLogs.map(log => new Date(log.timestamp).getTime());
    const minTime = Math.min(...timestamps);
    const maxTime = Math.max(...timestamps);
    // Include logs within 30 minutes before and after the writer logs
    const timeWindow = 30 * 60 * 1000; // 30 minutes in milliseconds

    // Filter logs that are within the time window
    const relatedLogs = allLogs?.filter((log) => {
      const logTime = new Date(log.timestamp).getTime();
      return logTime >= (minTime - timeWindow) && logTime <= (maxTime + timeWindow);
    }) || [];

    // Sort by timestamp and group by agent type
    const sortedLogs = relatedLogs.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    // Group consecutive logs by the same agent (for iterations)
    const groupedLogs: Array<{
      agent: string;
      logs: typeof sortedLogs;
      iteration?: number;
    }> = [];
    
    let currentGroup: typeof sortedLogs = [];
    let currentAgent = '';
    
    sortedLogs.forEach((log, index) => {
      if (log.agent !== currentAgent && currentGroup.length > 0) {
        groupedLogs.push({
          agent: currentAgent,
          logs: [...currentGroup],
          iteration: currentAgent === 'fact_checker' || currentAgent === 'writer' ? groupedLogs.filter(g => g.agent === currentAgent).length + 1 : undefined
        });
        currentGroup = [];
      }
      currentAgent = log.agent;
      currentGroup.push(log);
    });
    
    if (currentGroup.length > 0) {
      groupedLogs.push({
        agent: currentAgent,
        logs: [...currentGroup],
        iteration: currentAgent === 'fact_checker' || currentAgent === 'writer' ? groupedLogs.filter(g => g.agent === currentAgent).length + 1 : undefined
      });
    }

    return NextResponse.json({
      post,
      logs: sortedLogs,
      groupedLogs
    });
  } catch (error) {
    console.error('Error fetching timeline:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

