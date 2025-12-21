import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_KEY || process.env.SUPABASE_KEY;

export async function GET(request: NextRequest) {
  try {
    if (!SUPABASE_URL || !SUPABASE_KEY) {
      return NextResponse.json(
        { error: 'Supabase credentials not configured' },
        { status: 500 }
      );
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

    // Fetch all posts
    const { data: posts, error } = await supabase
      .from('posts')
      .select('id, prd, final_post')
      .order('id', { ascending: false })
      .limit(100);

    if (error) {
      return NextResponse.json(
        { error: 'Failed to fetch posts' },
        { status: 500 }
      );
    }

    // Return posts with truncated previews
    const postsWithPreview = posts?.map(post => ({
      id: post.id,
      prd_preview: post.prd.substring(0, 200) + (post.prd.length > 200 ? '...' : ''),
      final_post_preview: post.final_post.substring(0, 200) + (post.final_post.length > 200 ? '...' : ''),
      prd_length: post.prd.length,
      final_post_length: post.final_post.length
    })) || [];

    return NextResponse.json({ posts: postsWithPreview });
  } catch (error) {
    console.error('Error fetching posts:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

