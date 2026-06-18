const request = require('supertest');
const app = require('../src/index');

describe('Member Service', () => {
  test('GET /healthz returns ok', async () => {
    const res = await request(app).get('/healthz');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.service).toBe('member');
  });

  test('POST /api/members/register creates member', async () => {
    const res = await request(app)
      .post('/api/members/register')
      .send({ phone: '13800000001', nickname: 'TestCat', password: '123456' });
    expect(res.statusCode).toBe(201);
    expect(res.body.level).toBe('BRONZE');
    expect(res.body.id).toBeDefined();
  });

  test('POST /api/members/login returns token', async () => {
    const res = await request(app)
      .post('/api/members/login')
      .send({ phone: '13800000001', password: '123456' });
    expect(res.statusCode).toBe(200);
    expect(res.body.token).toBeDefined();
  });

  test('GET /api/members/:id returns profile', async () => {
    const res = await request(app).get('/api/members/mem_001');
    expect(res.statusCode).toBe(200);
    expect(res.body.level).toBe('GOLD');
  });

  test('GET /api/members/:id/points returns balance', async () => {
    const res = await request(app).get('/api/members/mem_001/points');
    expect(res.statusCode).toBe(200);
    expect(res.body.balance).toBeDefined();
  });

  test('GET /api/members/levels returns 5 levels', async () => {
    const res = await request(app).get('/api/members/levels');
    expect(res.statusCode).toBe(200);
    expect(res.body.length).toBe(5);
  });
});
