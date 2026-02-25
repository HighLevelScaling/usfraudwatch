import { NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';

// GET: Fetch stories with optional filters
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const state = searchParams.get('state');
    const fraudType = searchParams.get('type');
    const source = searchParams.get('source');
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = parseInt(searchParams.get('offset') || '0');

    const supabase = createServerClient();

    let query = supabase
      .from('stories')
      .select('*', { count: 'exact' })
      .order('published_at', { ascending: false })
      .range(offset, offset + limit - 1);

    if (state) {
      query = query.eq('state', state);
    }
    if (fraudType) {
      query = query.eq('fraud_type', fraudType);
    }
    if (source) {
      query = query.ilike('source_name', `%${source}%`);
    }

    const { data, count, error } = await query;

    if (error) {
      console.error('Error fetching stories:', error);
      return NextResponse.json(
        { error: 'Failed to fetch stories' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      stories: data || [],
      total: count || 0,
      limit,
      offset,
    });
  } catch (error) {
    console.error('Stories GET error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// POST: Add a new story (used by n8n automation)
export async function POST(request: Request) {
  try {
    // Verify API key for write operations
    const apiKey = request.headers.get('x-api-key');
    const expectedKey = process.env.INGESTION_API_KEY;

    if (!expectedKey || apiKey !== expectedKey) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();

    // Validate required fields
    if (!body.title || !body.source_url || !body.source_name) {
      return NextResponse.json(
        { error: 'Missing required fields: title, source_url, source_name' },
        { status: 400 }
      );
    }

    const supabase = createServerClient();

    // Check for duplicate by source_url
    const { data: existing } = await supabase
      .from('stories')
      .select('id')
      .eq('source_url', body.source_url)
      .single();

    if (existing) {
      return NextResponse.json({
        success: true,
        duplicate: true,
        id: existing.id,
      });
    }

    // Insert new story
    const { data, error } = await supabase
      .from('stories')
      .insert({
        title: body.title,
        source_url: body.source_url,
        source_name: body.source_name,
        published_at: body.published_at || null,
        summary: body.summary || null,
        fraud_type: body.fraud_type || null,
        entities: body.entities || {},
        state: body.state || null,
        city: body.city || null,
        importance_score: body.importance_score || 50,
        status: 'new',
      })
      .select()
      .single();

    if (error) {
      console.error('Error inserting story:', error);
      if (error.code === '23505') {
        // Unique violation on source_url
        return NextResponse.json({
          success: true,
          duplicate: true,
        });
      }
      return NextResponse.json(
        { error: 'Failed to insert story' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      id: data.id,
      story: data,
    });
  } catch (error) {
    console.error('Stories POST error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
