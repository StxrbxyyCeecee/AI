import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// 1. Define your whitelist of approved domains
const ALLOWED_ORIGINS = [
  "https://tvedcvkeavrortfgnlrh.supabase.co", // Your Supabase Storage/Hosting URL
  "https://frank-virid.vercel.app/",        // Replace with your actual Vercel URL
  "http://localhost:5000",                   // Local development
  "http://127.0.0.1:5000"
];

serve(async (req) => {
  const origin = req.headers.get("origin") || "";

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { 
      headers: {
        'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      } 
    })
  }

  try {
    // 2. Reject requests from unauthorized origins immediately
    if (!origin || !ALLOWED_ORIGINS.includes(origin)) {
      throw new Error("Unauthorized: Access denied from this origin.");
    }

    const authHeader = req.headers.get('Authorization') || '';
    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Verify User Session
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error: authError } = await supabase.auth.getUser(token);

    if (authError || !user) {
        throw new Error("Unauthorized: Invalid session token.");
    }

    const { text } = await req.json()
    console.log(`[CHAT_FUNCTION] Auth verified for ${user.email}. Text: "${text}"`)

    const groqKey = Deno.env.get('GROQ_API_KEY')

    // 1. Record User Message in Logs (UI will update via Realtime)
    await supabase.table('logs').insert({ content: `You: ${text}`, type: 'user' })

    // 2. Call Groq API for the AI Response
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${groqKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        messages: [
          { role: "system", content: "Your name is Frank. Be polite, concise, and address the user as sir/madam." },
          { role: "user", content: text }
        ],
        max_tokens: 200,
      }),
    })

    const data = await response.json()
    console.log(`[GROQ_API] Response status: ${response.status}`)

    if (!response.ok) {
      console.error(`[GROQ_API] Error payload:`, JSON.stringify(data))
      throw new Error(`Groq API returned ${response.status}`)
    }

    const reply = data.choices[0].message.content.trim()
    console.log(`[CHAT_FUNCTION] Generated reply: "${reply.substring(0, 50)}..."`)

    // 3. Record AI Message in Logs
    await supabase.table('logs').insert({ content: `AI: ${reply}`, type: 'assistant' })

    return new Response(JSON.stringify({ reply }), {
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': origin 
      },
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0]
      },
    })
  }
})