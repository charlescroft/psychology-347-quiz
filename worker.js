/**
 * Cloudflare Worker for Psychology 347 Quiz System
 * - Serves Static Assets for Frontend SPA
 * - Provides KV-backed multi-device cloud synchronization API (/api/user/sync)
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
        JSON.stringify({ success: false, isNewUser: true, message: '未找到该用户的云端记录，首次登录可直接上传同步' }),
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

      if (rawRecord) {
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
        payload: finalPayload,
        updatedAt: Date.now(),
      };

      await env.PSYCH_KV.put(key, JSON.stringify(recordToSave));

      return new Response(
        JSON.stringify({
          success: true,
          message: rawRecord ? '云端数据双向合并同步成功' : '新用户初始化注册与同步成功',
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
  // Merge userAnswers (keep answer with newer timestamp)
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

  // Union of Sets for stars, wrongs, mastered
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
