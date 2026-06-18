// NekoCafe Member Service — Express.js
const express = require('express');

const app = express();
const PORT = process.env.PORT || 8081;

app.use(express.json());

// Structured JSON request logging
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const log = {
      level: res.statusCode >= 500 ? 'ERROR' : res.statusCode >= 400 ? 'WARN' : 'INFO',
      timestamp: new Date().toISOString(),
      service: 'member',
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration_ms: Date.now() - start,
    };
    console.log(JSON.stringify(log));
  });
  next();
});

// Health check
app.get('/healthz', (req, res) => {
  res.json({ status: 'ok', service: 'member', timestamp: new Date().toISOString() });
});

// Member registration
app.post('/api/members/register', (req, res) => {
  const { phone, nickname, password } = req.body;
  if (!phone || !nickname || !password) {
    return res.status(400).json({ error: 'phone, nickname, password are required' });
  }
  const member = {
    id: `mem_${Date.now()}`,
    phone,
    nickname,
    level: 'BRONZE',
    points: 0,
    createdAt: new Date().toISOString(),
  };
  res.status(201).json(member);
});

// Member login
app.post('/api/members/login', (req, res) => {
  const { phone, password } = req.body;
  if (!phone || !password) {
    return res.status(400).json({ error: 'phone and password are required' });
  }
  res.json({ token: `jwt_dev_${Date.now()}`, expiresIn: 3600, tokenType: 'Bearer' });
});

// Get member profile
app.get('/api/members/:id', (req, res) => {
  res.json({
    id: req.params.id,
    phone: '138****1234',
    nickname: 'CatLover',
    level: 'GOLD',
    points: 2580,
    createdAt: '2026-01-15T10:30:00Z',
  });
});

// Get points balance
app.get('/api/members/:id/points', (req, res) => {
  res.json({ memberId: req.params.id, balance: 2580, level: 'GOLD', nextLevelPoints: 5000 });
});

// List member levels
app.get('/api/members/levels', (req, res) => {
  res.json([
    { level: 'BRONZE', minPoints: 0, discount: 0 },
    { level: 'SILVER', minPoints: 500, discount: 5 },
    { level: 'GOLD', minPoints: 2000, discount: 10 },
    { level: 'PLATINUM', minPoints: 5000, discount: 15 },
    { level: 'DIAMOND', minPoints: 10000, discount: 20 },
  ]);
});

// Only listen when run directly (not in tests)
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(JSON.stringify({
      level: 'INFO',
      message: `Member service starting on port ${PORT}`,
      service: 'member',
      timestamp: new Date().toISOString(),
    }));
  });
}

module.exports = app;
