import { test, expect } from '@playwright/test';

/**
 * E2E Tests: STAT7 HTTP Authentication Server
 * 
 * Tests the FastAPI authentication server running on port 8000 with:
 * - Public endpoints: /api/auth/register, /api/auth/login, /api/auth/generate-qr
 * - Protected endpoints: /api/admin/audit-log, /api/admin/users
 * - Auth middleware and role-based access control
 * - Immutable audit logging
 * 
 * Server must be running: docker-compose up -d
 * 
 * TEST MODE:
 * For faster testing without registration flow, set environment variable:
 *   STAT7_TEST_MODE=true
 * 
 * Pre-seeded test accounts (when TEST MODE is enabled):
 *   - test-admin-001:  Full admin privileges (audit-log, users management)
 *   - test-public-001: Read-only public access
 *   - test-demo-001:   Sandbox admin (simulation control)
 */

const BASE_URL = 'http://localhost:8000';
const TEST_ADMIN_ID = 'test-admin-001';
const TEST_PUBLIC_ID = 'test-public-001';
const TEST_DEMO_ID = 'test-demo-001';

// Helper: Make HTTP request via fetch (since Playwright page context doesn't expose raw HTTP)
async function makeRequest(
  method: string,
  endpoint: string,
  body?: any,
  headers?: Record<string, string>
): Promise<{ status: number; data: any }> {
  const url = `${BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json().catch(() => null);
  return { status: response.status, data };
}

test.describe('STAT7 Authentication Server - HTTP API', () => {
  
  // ========================================================================
  // PUBLIC ENDPOINTS (No auth required)
  // ========================================================================

  test('GET / redirects to stat7_auth.html', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    // Should redirect or serve auth page
    await expect(page).toHaveTitle(/STAT7|Auth/i);
    expect(page.url()).toContain('auth');
  });

  test('POST /api/auth/generate-qr returns registration code', async () => {
    const response = await makeRequest('POST', '/api/auth/generate-qr', {});
    
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('code');
    expect(response.data).toHaveProperty('qr_data');
    expect(response.data).toHaveProperty('expires_at');
    expect(response.data).toHaveProperty('instructions');
    expect(response.data.code).toMatch(/^[A-Z0-9]{6,}$/); // Registration code format
  });

  test('POST /api/auth/register creates user with valid registration code', async () => {
    // Step 1: Generate a registration code
    const qrResponse = await makeRequest('POST', '/api/auth/generate-qr', {});
    const registrationCode = qrResponse.data.code;
    expect(registrationCode).toBeTruthy();

    // Step 2: Register a new user with that code
    const registerResponse = await makeRequest('POST', '/api/auth/register', {
      registration_code: registrationCode,
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
    });

    expect(registerResponse.status).toBe(201);
    expect(registerResponse.data).toHaveProperty('stat7_id');
    expect(registerResponse.data).toHaveProperty('username');
    expect(registerResponse.data).toHaveProperty('role');
    expect(registerResponse.data.stat7_id).toMatch(/^stat7-/); // STAT7.ID format
    expect(registerResponse.data.role).toMatch(/^(public|demo_admin|admin)$/);
  });

  test('POST /api/auth/register rejects invalid registration code', async () => {
    const response = await makeRequest('POST', '/api/auth/register', {
      registration_code: 'INVALID_CODE_FAKE_12345',
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
    });

    expect(response.status).toBe(400);
    expect(response.data.error).toBeTruthy();
    expect(response.data.reason).toBe('INVALID_CODE_OR_CONFLICT');
  });

  test('POST /api/auth/register rejects missing fields', async () => {
    const response = await makeRequest('POST', '/api/auth/register', {
      registration_code: 'CODE123',
      // Missing username and email
    });

    expect(response.status).toBe(400);
    expect(response.data.error).toContain('Missing required fields');
  });

  test('POST /api/auth/login creates token for existing user', async () => {
    // Step 1: Create a user first
    const qrResponse = await makeRequest('POST', '/api/auth/generate-qr', {});
    const registrationCode = qrResponse.data.code;

    const registerResponse = await makeRequest('POST', '/api/auth/register', {
      registration_code: registrationCode,
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
    });

    const stat7Id = registerResponse.data.stat7_id;
    expect(stat7Id).toBeTruthy();

    // Step 2: Login with that STAT7.ID
    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: stat7Id,
    });

    expect(loginResponse.status).toBe(200);
    expect(loginResponse.data).toHaveProperty('token');
    expect(loginResponse.data).toHaveProperty('stat7_id');
    expect(loginResponse.data.status).toBe('success');
    expect(loginResponse.data.token).toMatch(/^eyJ/); // JWT format (starts with eyJ)
  });

  test('POST /api/auth/login rejects non-existent STAT7.ID', async () => {
    const response = await makeRequest('POST', '/api/auth/login', {
      stat7_id: 'stat7-nonexistent-fake-id-12345',
    });

    expect(response.status).toBe(401);
    expect(response.data.error).toContain('not found');
    expect(response.data.reason).toBe('LOGIN_FAILED');
  });

  test('POST /api/auth/login requires stat7_id', async () => {
    const response = await makeRequest('POST', '/api/auth/login', {});

    expect(response.status).toBe(400);
    expect(response.data.error).toContain('Missing stat7_id');
  });

  // ========================================================================
  // SECURITY HEADERS
  // ========================================================================

  test('All responses include security headers', async () => {
    const response = await fetch(`${BASE_URL}/api/auth/generate-qr`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });

    // Check for security headers
    expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
    expect(response.headers.get('X-Frame-Options')).toBe('DENY');
    expect(response.headers.get('X-XSS-Protection')).toContain('1');
  });

  // ========================================================================
  // PROTECTED ENDPOINTS (Auth required)
  // ========================================================================

  test('POST /api/admin/audit-log requires authentication', async () => {
    const response = await makeRequest('POST', '/api/admin/audit-log', {
      limit: 10,
    });

    // No auth header provided
    expect(response.status).toBe(401);
    expect(response.data.error).toBeTruthy();
  });

  test('POST /api/admin/users requires authentication', async () => {
    const response = await makeRequest('POST', '/api/admin/users', {
      username: 'newadmin',
      email: 'admin@example.com',
      role: 'admin',
    });

    expect(response.status).toBe(401);
    expect(response.data.error).toBeTruthy();
  });

  test('Protected endpoints reject invalid token', async () => {
    const invalidToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid';

    const response = await makeRequest(
      'POST',
      '/api/admin/audit-log',
      { limit: 10 },
      { Authorization: `Bearer ${invalidToken}` }
    );

    expect(response.status).toBe(401);
    expect(response.data.error).toBeTruthy();
  });

  test('Admin endpoint enforces admin:audit:read permission', async () => {
    // Step 1: Create a user and get a token
    const qrResponse = await makeRequest('POST', '/api/auth/generate-qr', {});
    const registrationCode = qrResponse.data.code;

    const registerResponse = await makeRequest('POST', '/api/auth/register', {
      registration_code: registrationCode,
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
    });

    const stat7Id = registerResponse.data.stat7_id;

    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: stat7Id,
    });

    const token = loginResponse.data.token;
    expect(token).toBeTruthy();

    // Step 2: Try to access audit-log with a public user token
    // (public users should NOT have admin:audit:read permission)
    const auditResponse = await makeRequest(
      'POST',
      '/api/admin/audit-log',
      { limit: 10 },
      { Authorization: `Bearer ${token}` }
    );

    // Should be denied due to insufficient permissions
    expect(auditResponse.status).toBe(403);
    expect(auditResponse.data.error).toContain('Permission denied');
  });

  test('Admin endpoint enforces admin:user:manage permission', async () => {
    // Create a public user and try to use admin endpoint
    const qrResponse = await makeRequest('POST', '/api/auth/generate-qr', {});
    const registrationCode = qrResponse.data.code;

    const registerResponse = await makeRequest('POST', '/api/auth/register', {
      registration_code: registrationCode,
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
    });

    const stat7Id = registerResponse.data.stat7_id;

    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: stat7Id,
    });

    const token = loginResponse.data.token;

    // Try to create a new user (admin:user:manage permission required)
    const createUserResponse = await makeRequest(
      'POST',
      '/api/admin/users',
      {
        username: `admin_${Date.now()}`,
        email: `admin_${Date.now()}@example.com`,
        role: 'admin',
      },
      { Authorization: `Bearer ${token}` }
    );

    expect(createUserResponse.status).toBe(403);
    expect(createUserResponse.data.error).toContain('Permission denied');
  });

  // ========================================================================
  // RESPONSE STATUS CODES
  // ========================================================================

  test('Unknown endpoints return 404', async () => {
    const response = await makeRequest('POST', '/api/unknown/endpoint', {});

    expect(response.status).toBe(404);
    expect(response.data.error).toContain('Not found');
  });

  test('Registration returns 201 Created', async () => {
    const qrResponse = await makeRequest('POST', '/api/auth/generate-qr', {});
    const registrationCode = qrResponse.data.code;

    const registerResponse = await makeRequest('POST', '/api/auth/register', {
      registration_code: registrationCode,
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
    });

    expect(registerResponse.status).toBe(201);
  });

  test('Login returns 200 OK', async () => {
    const qrResponse = await makeRequest('POST', '/api/auth/generate-qr', {});
    const registrationCode = qrResponse.data.code;

    const registerResponse = await makeRequest('POST', '/api/auth/register', {
      registration_code: registrationCode,
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
    });

    const stat7Id = registerResponse.data.stat7_id;

    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: stat7Id,
    });

    expect(loginResponse.status).toBe(200);
  });

  // ========================================================================
  // ERROR HANDLING
  // ========================================================================

  test('Server handles malformed JSON gracefully', async () => {
    const response = await fetch(`${BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: 'not valid json',
    });

    expect(response.status).toBeGreaterThanOrEqual(400);
  });

  test('Error responses do not leak sensitive information', async () => {
    const response = await makeRequest('POST', '/api/auth/login', {
      stat7_id: 'fake',
    });

    const errorMsg = JSON.stringify(response.data);
    // Should not contain SQL, file paths, or internal details
    expect(errorMsg).not.toMatch(/SELECT|INSERT|DROP|\/home|\/root|\.py|\.sql/i);
  });

  // ========================================================================
  // CONTENT-TYPE & ENCODING
  // ========================================================================

  test('All responses return JSON with correct Content-Type', async () => {
    const response = await fetch(`${BASE_URL}/api/auth/generate-qr`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });

    expect(response.headers.get('Content-Type')).toContain('application/json');
  });

  // ========================================================================
  // FULL FLOW: REGISTER → LOGIN → ACCESS PROTECTED ENDPOINT
  // ========================================================================

  test('Complete user flow: register, login, then access protected endpoint', async () => {
    // 1. Generate QR / registration code
    const qrResponse = await makeRequest('POST', '/api/auth/generate-qr', {});
    expect(qrResponse.status).toBe(200);
    const registrationCode = qrResponse.data.code;

    // 2. Register
    const registerResponse = await makeRequest('POST', '/api/auth/register', {
      registration_code: registrationCode,
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
    });
    expect(registerResponse.status).toBe(201);
    const stat7Id = registerResponse.data.stat7_id;

    // 3. Login
    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: stat7Id,
    });
    expect(loginResponse.status).toBe(200);
    const token = loginResponse.data.token;

    // 4. Try to access protected endpoint with token
    // (Should fail with 403 Permission Denied, not 401 Unauthorized)
    const protectedResponse = await makeRequest(
      'POST',
      '/api/admin/audit-log',
      { limit: 10 },
      { Authorization: `Bearer ${token}` }
    );

    // Public user should NOT have admin permission, so expect 403
    expect(protectedResponse.status).toBe(403);
    expect(protectedResponse.data.error).toContain('Permission denied');
  });

  // ========================================================================
  // TEST MODE: Pre-seeded test credentials (when STAT7_TEST_MODE=true)
  // ========================================================================
  // These tests use pre-seeded test accounts for faster E2E testing
  // Enable with: STAT7_TEST_MODE=true (or skip if not available)

  test.skip('TEST MODE: Admin can access audit-log endpoint', async () => {
    // LOGIN as test admin
    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: TEST_ADMIN_ID,
    });

    // Skip if test account not available
    if (loginResponse.status === 401) {
      test.skip();
    }

    expect(loginResponse.status).toBe(200);
    expect(loginResponse.data).toHaveProperty('token');
    const token = loginResponse.data.token;

    // ACCESS audit-log as admin
    const auditResponse = await makeRequest(
      'POST',
      '/api/admin/audit-log',
      { limit: 5 },
      { Authorization: `Bearer ${token}` }
    );

    expect(auditResponse.status).toBe(200);
    expect(auditResponse.data).toHaveProperty('logs');
    expect(auditResponse.data).toHaveProperty('count');
    expect(Array.isArray(auditResponse.data.logs)).toBe(true);
  });

  test.skip('TEST MODE: Admin can create new users', async () => {
    // LOGIN as test admin
    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: TEST_ADMIN_ID,
    });

    // Skip if test account not available
    if (loginResponse.status === 401) {
      test.skip();
    }

    expect(loginResponse.status).toBe(200);
    const token = loginResponse.data.token;

    // CREATE a new user as admin
    const createUserResponse = await makeRequest(
      'POST',
      '/api/admin/users',
      {
        username: `e2e_test_user_${Date.now()}`,
        email: `e2e_${Date.now()}@test.local`,
        role: 'demo_admin',
      },
      { Authorization: `Bearer ${token}` }
    );

    expect(createUserResponse.status).toBe(201);
    expect(createUserResponse.data).toHaveProperty('stat7_id');
    expect(createUserResponse.data).toHaveProperty('username');
    expect(createUserResponse.data).toHaveProperty('role');
    expect(createUserResponse.data.role).toBe('demo_admin');
  });

  test.skip('TEST MODE: Public account cannot access admin endpoints', async () => {
    // LOGIN as test public user
    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: TEST_PUBLIC_ID,
    });

    // Skip if test account not available
    if (loginResponse.status === 401) {
      test.skip();
    }

    expect(loginResponse.status).toBe(200);
    const token = loginResponse.data.token;

    // TRY to access audit-log as public user (should fail)
    const auditResponse = await makeRequest(
      'POST',
      '/api/admin/audit-log',
      { limit: 5 },
      { Authorization: `Bearer ${token}` }
    );

    expect(auditResponse.status).toBe(403);
    expect(auditResponse.data.error).toContain('Permission denied');
  });

  test.skip('TEST MODE: Demo admin has restricted permissions', async () => {
    // LOGIN as test demo admin
    const loginResponse = await makeRequest('POST', '/api/auth/login', {
      stat7_id: TEST_DEMO_ID,
    });

    // Skip if test account not available
    if (loginResponse.status === 401) {
      test.skip();
    }

    expect(loginResponse.status).toBe(200);
    const token = loginResponse.data.token;

    // Demo admin should NOT be able to access audit-log (no admin:audit:read)
    const auditResponse = await makeRequest(
      'POST',
      '/api/admin/audit-log',
      { limit: 5 },
      { Authorization: `Bearer ${token}` }
    );

    expect(auditResponse.status).toBe(403);
    expect(auditResponse.data.error).toContain('Permission denied');

    // Demo admin should NOT be able to create users (no admin:user:manage)
    const createUserResponse = await makeRequest(
      'POST',
      '/api/admin/users',
      {
        username: `test_user_${Date.now()}`,
        email: `test_${Date.now()}@test.local`,
      },
      { Authorization: `Bearer ${token}` }
    );

    expect(createUserResponse.status).toBe(403);
    expect(createUserResponse.data.error).toContain('Permission denied');
  });
});