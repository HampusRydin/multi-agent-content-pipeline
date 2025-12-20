import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { topic, target_length, style } = body;

    // Call the Python FastAPI server
    const response = await fetch(`${FASTAPI_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic,
        target_length,
        style,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: `FastAPI server error: ${error}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error calling FastAPI server:', error);
    return NextResponse.json(
      { error: 'Failed to connect to FastAPI server' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({ 
    message: 'Generate endpoint - use POST to generate content',
    fastapi_url: FASTAPI_URL 
  });
}

