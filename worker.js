/**
 * Cloudflare Worker for Psychology 347 Quiz System
 * - Serves Static Assets for Frontend SPA
 * - Provides KV-backed multi-device cloud synchronization API (/api/user/sync)
 * - Protected by Admin Authorization / Invite Code (AUTH_CODES) to prevent KV storage abuse
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    // API Routes for Multi-Device Cloud Sync
    if (url.pathname === '/api/user/sync' || url.pathname === '/api/sync') {
      return handleSyncApi(request, env, url);
    }

    // Default: Serve frontend static assets (HTML, CSS, JS)
    return env.ASSETS.fetch(request);
  },
};

function isAuthCodeValid(env, inputCode) {
  const raw = env.AUTH_CODES || env.AUTH_CODE || '';
  const allowed = raw
    .split(',')
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);

  // If no auth code configured in environment, allow by default
  if (allowed.length === 0) return true;

  const given = (inputCode || '').trim().toLowerCase();
  return allowed.includes(given);
}

async function handleSyncApi(request, env, url) {
  const corsHeaders = {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
  };

  if (!env.PSYCH_KV) {
    return new Response(
      JSON.stringify({ success: false, message: 'Cloudflare KV (PSYCH_KV) binding not found on server' }),
      { status: 500, headers: corsHeaders }
    );
  }

  // 1. GET: Fetch user cloud state
  if (request.method === 'GET') {
    const username = (url.searchParams.get('username') || '').trim().toLowerCase();
    const password = (url.searchParams.get('password') || '').trim();
    const authCode = (url.searchParams.get('authCode') || url.searchParams.get('inviteCode') || '').trim();

    if (!username) {
      return new Response(
        JSON.stringify({ success: false, message: '请提供用户名参数' }),
        { status: 400, headers: corsHeaders }
      );
    }

    const key = `user:${username}`;
    const rawRecord = await env.PSYCH_KV.get(key);

    if (!rawRecord) {
      return new Response(
        JSON.stringify({
          success: false,
          isNewUser: true,
          message: '未找到该用户的云端记录，首次绑定请输入管理员分发的授权认证码',
        }),
        { status: 404, headers: corsHeaders }
      );
    }

    try {
      const record = JSON.parse(rawRecord);
      if (record.password && record.password !== password) {
        return new Response(
          JSON.stringify({ success: false, message: '同步密码错误，请核对后重试' }),
          { status: 401, headers: corsHeaders }
        );
      }

      return new Response(
        JSON.stringify({ success: true, payload: record.payload, updatedAt: record.updatedAt }),
        { status: 200, headers: corsHeaders }
      );
    } catch (e) {
      return new Response(
        JSON.stringify({ success: false, message: '读取云端数据失败: ' + e.message }),
        { status: 500, headers: corsHeaders }
      );
    }
  }

  // 2. POST: Save / Merge user cloud state
  if (request.method === 'POST') {
    try {
      const body = await request.json();
      const username = (body.username || '').trim().toLowerCase();
      const password = (body.password || '').trim();
      const authCode = (body.authCode || body.inviteCode || '').trim();
      const clientPayload = body.payload || {};

      if (!username) {
        return new Response(
          JSON.stringify({ success: false, message: '用户名不能为空' }),
          { status: 400, headers: corsHeaders }
        );
      }

      const key = `user:${username}`;
      const rawRecord = await env.PSYCH_KV.get(key);

      let finalPayload = clientPayload;

      if (!rawRecord) {
        // New user registration -> Must supply valid authorization code!
        if (!isAuthCodeValid(env, authCode)) {
          return new Response(
            JSON.stringify({
              success: false,
              code: 'INVALID_AUTH_CODE',
              message: '授权认证码无效或未提供。为防止云端存储滥用，首次创建或绑定多端同步需向管理员索取有效授权码。',
            }),
            { status: 403, headers: corsHeaders }
          );
        }
      } else {
        // Existing user -> verify password and optional re-auth
        const record = JSON.parse(rawRecord);
        if (record.password && record.password !== password) {
          return new Response(
            JSON.stringify({ success: false, message: '同步密码错误，无法覆盖云端记录' }),
            { status: 401, headers: corsHeaders }
          );
        }

        // Two-way merge logic
        finalPayload = mergePayloads(record.payload || {}, clientPayload);
      }

      // Save to KV
      const recordToSave = {
        username: username,
        password: password,
        authCode: authCode || 'authorized',
        payload: finalPayload,
        updatedAt: Date.now(),
      };

      await env.PSYCH_KV.put(key, JSON.stringify(recordToSave));

      return new Response(
        JSON.stringify({
          success: true,
          message: rawRecord ? '云端数据双向合并同步成功' : '授权认证成功，新用户档案已创建',
          payload: finalPayload,
          updatedAt: recordToSave.updatedAt,
        }),
        { status: 200, headers: corsHeaders }
      );
    } catch (e) {
      return new Response(
        JSON.stringify({ success: false, message: '同步处理异常: ' + e.message }),
        { status: 500, headers: corsHeaders }
      );
    }
  }

  return new Response(JSON.stringify({ error: 'Method Not Allowed' }), {
    status: 405,
    headers: corsHeaders,
  });
}

/**
 * Intelligent Two-Way Payload Merge
 */
function mergePayloads(cloud, client) {
  const mergedAnswers = { ...(cloud.answers || {}) };
  const clientAnswers = client.answers || {};

  Object.keys(clientAnswers).forEach((qId) => {
    const clientAns = clientAnswers[qId];
    const cloudAns = mergedAnswers[qId];
    if (!cloudAns) {
      mergedAnswers[qId] = clientAns;
    } else {
      const clientTime = clientAns.timestamp || 0;
      const cloudTime = cloudAns.timestamp || 0;
      if (clientTime >= cloudTime) {
        mergedAnswers[qId] = clientAns;
      }
    }
  });

  const mergedStars = Array.from(new Set([...(cloud.stars || []), ...(client.stars || [])]));
  const mergedWrongs = Array.from(new Set([...(cloud.wrongs || []), ...(client.wrongs || [])]));
  const mergedMastered = Array.from(new Set([...(cloud.mastered || []), ...(client.mastered || [])]));

  return {
    answers: mergedAnswers,
    stars: mergedStars,
    wrongs: mergedWrongs,
    mastered: mergedMastered,
    lastSyncTime: Date.now(),
  };
}
