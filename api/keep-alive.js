const BACKEND_HEALTH = 'https://payroll-backend-5od7.onrender.com/api/v1/health';

export default async function handler(req, res) {
  try {
    const upstream = await fetch(BACKEND_HEALTH, {
      signal: AbortSignal.timeout(25_000),
    });
    res.status(200).json({ ok: upstream.ok, upstream_status: upstream.status });
  } catch (err) {
    // Return 200 so Vercel doesn't flag cold-start timeouts as cron failures
    res.status(200).json({ ok: false, error: err.message });
  }
}
