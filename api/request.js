// POST /api/request — "made with Vigil" submissions and feature requests from the home page (#wild).
// Vercel serverless function, no build step, no dependencies.
// Mirrors the vigil-icons endpoint so both sites share one delivery setup.
//
// Configure on the Vercel project (Settings → Environment Variables):
//   REQUEST_WEBHOOK_URL          any URL accepting a JSON POST — GoHighLevel, Zapier, Make, Slack…
//   RESEND_API_KEY + REQUEST_TO  email via https://resend.com. REQUEST_FROM optional; the default
//                                sender (onboarding@resend.dev) only delivers to the Resend account address.
// Either or both. With neither set the endpoint answers 503 and the form falls back to thinkkeno.com/#contact.
// Every accepted submission is also written to the function log as one JSON line.

const MAX = { what: 120, link: 300, note: 400, email: 120, kind: 20, referer: 200 };
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

async function readBody(req) {
  if (req.body !== undefined) return req.body;
  const chunks = [];
  for await (const c of req) chunks.push(c);
  return Buffer.concat(chunks).toString('utf8');
}
function parseBody(body, contentType) {
  if (body && typeof body === 'object') return body;
  if (typeof body !== 'string' || !body) return {};
  if (contentType.includes('application/json')) { try { return JSON.parse(body); } catch (e) { return {}; } }
  return Object.fromEntries(new URLSearchParams(body));
}
const clean = (v, n) => String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, n);
const wantsHtml = (req) => {
  const a = String(req.headers.accept || '');
  return a.includes('text/html') && !a.includes('application/json');
};
function json(res, status, obj) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.end(JSON.stringify(obj));
}
// The query string must come BEFORE the fragment. "/#wild?sent=1" puts sent=1
// inside the hash, where location.search can't see it and the no-JS confirmation
// never renders. Correct shape is "/?sent=1#wild".
function reply(req, res, status, ok, message, back) {
  if (wantsHtml(req)) {
    const hash = back.indexOf('#');
    const path = hash === -1 ? back : back.slice(0, hash) || '/';
    const frag = hash === -1 ? '' : back.slice(hash);
    const query = ok ? '?sent=1' : '?error=' + encodeURIComponent(message);
    res.statusCode = 303;
    res.setHeader('Location', path + query + frag);
    return res.end();
  }
  return json(res, status, ok ? { ok: true } : { ok: false, error: message });
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return json(res, 405, { ok: false, error: 'POST only' }); }

  const raw = parseBody(await readBody(req), String(req.headers['content-type'] || ''));
  const kind = clean(raw.kind, MAX.kind) === 'request' ? 'request' : 'wild';
  const back = '/#wild';
  const what = clean(raw.what, MAX.what);
  const link = clean(raw.link, MAX.link);
  const note = clean(raw.note, MAX.note);
  const email = clean(raw.email, MAX.email).toLowerCase();

  // Honeypot: "website" is visually hidden. People never fill it, bots do. Pretend it worked.
  if (clean(raw.website, 200)) return reply(req, res, 200, true, '', back);
  if (!what) return reply(req, res, 400, false, 'Tell us what you set in Vigil.', back);
  if (!EMAIL.test(email)) return reply(req, res, 400, false, 'Enter an email we can reply to.', back);

  const payload = { kind, what, link, note, email, page: clean(req.headers.referer, MAX.referer), at: new Date().toISOString() };
  console.log(JSON.stringify({ event: 'vigil-font-' + kind, ...payload }));

  const jobs = [];
  if (process.env.REQUEST_WEBHOOK_URL) {
    jobs.push(fetch(process.env.REQUEST_WEBHOOK_URL, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    }).then((r) => { if (!r.ok) throw new Error('webhook ' + r.status); }));
  }
  if (process.env.RESEND_API_KEY && process.env.REQUEST_TO) {
    const lines = [
      (kind === 'request' ? 'Feature request' : 'Made with Vigil') + ' from vigilfont.com',
      '', 'What: ' + what, 'Link: ' + (link || '—'), 'Note: ' + (note || '—'),
      'Email: ' + email, 'Page: ' + (payload.page || '—'), 'At: ' + payload.at,
    ];
    jobs.push(fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + process.env.RESEND_API_KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: process.env.REQUEST_FROM || 'Vigil <onboarding@resend.dev>',
        to: [process.env.REQUEST_TO], reply_to: email,
        subject: '[Vigil] ' + kind + ': ' + what, text: lines.join('\n'),
      }),
    }).then((r) => { if (!r.ok) throw new Error('resend ' + r.status); }));
  }
  if (!jobs.length) return reply(req, res, 503, false, 'unconfigured', back);

  try { await Promise.all(jobs); }
  catch (e) { console.error(e); return reply(req, res, 502, false, 'Could not send just now. Try again in a minute.', back); }
  return reply(req, res, 200, true, '', back);
};
