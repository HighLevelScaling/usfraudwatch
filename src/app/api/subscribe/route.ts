import { NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, interested_states } = body;

    // Validate email
    if (!email || typeof email !== 'string') {
      return NextResponse.json({ error: 'Email is required' }, { status: 400 });
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: 'Invalid email format' }, { status: 400 });
    }

    const supabase = createServerClient();

    // Check if already subscribed
    const { data: existing } = await supabase
      .from('subscribers')
      .select('id, unsubscribed_at')
      .eq('email', email.toLowerCase())
      .single();

    if (existing) {
      if (existing.unsubscribed_at) {
        // Resubscribe
        const { error } = await supabase
          .from('subscribers')
          .update({
            unsubscribed_at: null,
            interested_states: interested_states || null,
            subscribed_at: new Date().toISOString(),
          })
          .eq('id', existing.id);

        if (error) {
          console.error('Error resubscribing:', error);
          return NextResponse.json(
            { error: 'Failed to resubscribe' },
            { status: 500 }
          );
        }

        return NextResponse.json({ success: true, resubscribed: true });
      } else {
        // Already subscribed
        return NextResponse.json({ success: true, alreadySubscribed: true });
      }
    }

    // New subscriber
    const { error } = await supabase.from('subscribers').insert({
      email: email.toLowerCase(),
      tier: 'free',
      interested_states: interested_states || null,
      email_frequency: 'daily',
    });

    if (error) {
      console.error('Error subscribing:', error);
      if (error.code === '23505') {
        // Unique violation - race condition
        return NextResponse.json({ success: true, alreadySubscribed: true });
      }
      return NextResponse.json({ error: 'Failed to subscribe' }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Subscribe error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
