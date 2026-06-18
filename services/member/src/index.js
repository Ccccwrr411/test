// NekoCafé Member Service — Express.js
const express = require('express');
const { trace, context, SpanStatusCode } = require('@opentelemetry/api');

// OpenTelemetry setup (loaded first)
require('./telemetry');

const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());

// Request logging middleware (structured JSON)
app.use((req, res, next) => {
  const start = Date.now();
  const span = trace.getActiveSpan();
  const traceId = span?.spanContext()?.traceId || 'N/A';

  res.on('finish', () => {
    const log = {
      level: res.statusCode >= 500 ? 'ERROR' : res.statusCode >= 400 ? 'WARN' : 'INFO',
      timestamp: new Date().toISOString(),
      service: 'member',
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration_ms: Date.now() - start,
      traceId,
      userAgent: req.get('User-Agent')?.substring(0, 100) || 'N/A',
    };
    console.log(JSON.stringify(log));
  });
  next();
});

// Health check
app.get('/healthz', (req, res) => {
  res.json({ status: 'ok', service: 'member', timestamp: new Date().toISOString() });
});

// API: Member registration
app.post('/api/members/register', async (req, res) => {
  const span = trace.getTracer('member-service').startSpan('register_member');
  try {
    const { phone, nickname, password } = req.body;

    // Validate input
    if (!phone || !nickname || !password) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: 'Missing required fields' });
      return res.status(400).json({ error: 'phone, nickname, password are required' });
    }

    // TODO: Actual DB insert + password hashing
    const member = {
      id: `mem_${Date.now()}`,
      phone,
      nickname,
      level: 'BRONZE',
      points: 0,
      createdAt: new Date().toISOString(),
    };

    span.setAttribute('member.id', member.id);
    span.setAttribute('member.level', member.level);
    span.setStatus({ code: SpanStatusCode.OK });

    res.status(201).json(member);
  } catch (err) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
    res.status(500).json({ error: 'Internal server error' });
  } finally {
    span.end();
  }
});

// API: Member login (JWT)
app.post('/api/members/login', async (req, res) => {
  const span = trace.getTracer('member-service').startSpan('login_member');
  try {
    const { phone, password } = req.body;

    if (!phone || !password) {
      return res.status(400).json({ error: 'phone and password are required' });
    }

    // TODO: Verify credentials, issue JWT
    const token = `jwt_dev_${phone}_${Date.now()}`;
    span.setAttribute('member.phone', phone.substring(0, 3) + '***');

    res.json({
      token,
      expiresIn: 3600,
      tokenType: 'Bearer',
    });
  } catch (err) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
    res.status(500).json({ error: 'Internal server error' });
  } finally {
    span.end();
  }
});

// API: Get member profile
app.get('/api/members/:id', async (req, res) => {
  const span = trace.getTracer('member-service').startSpan('get_member');
  try {
    const { id } = req.params;

    // TODO: Fetch from DB
    const member = {
      id,
      phone: '138****1234',
      nickname: 'CatLover',
      level: 'GOLD',
      points: 2580,
      createdAt: '2026-01-15T10:30:00Z',
    };

    span.setAttribute('member.level', member.level);
    res.json(member);
  } catch (err) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
    res.status(500).json({ error: 'Internal server error' });
  } finally {
    span.end();
  }
});

// API: Get points balance
app.get('/api/members/:id/points', async (req, res) => {
  const span = trace.getTracer('member-service').startSpan('get_points');
  try {
    // TODO: Fetch from DB/Redis
    res.json({
      memberId: req.params.id,
      balance: 2580,
      level: 'GOLD',
      nextLevelPoints: 5000,
    });
  } catch (err) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
    res.status(500).json({ error: 'Internal server error' });
  } finally {
    span.end();
  }
});

// API: List member levels
app.get('/api/members/levels', (req, res) => {
  res.json([
    { level: 'BRONZE', minPoints: 0, discount: 0 },
    { level: 'SILVER', minPoints: 500, discount: 5 },
    { level: 'GOLD', minPoints: 2000, discount: 10 },
    { level: 'PLATINUM', minPoints: 5000, discount: 15 },
    { level: 'DIAMOND', minPoints: 10000, discount: 20 },
  ]);
});

// Start server
app.listen(PORT, () => {
  console.log(JSON.stringify({
    level: 'INFO',
    message: `Member service starting on port ${PORT}`,
    service: 'member',
    timestamp: new Date().toISOString(),
  }));
});

module.exports = app;
