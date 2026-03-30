/**
 * 统一 HTTP 请求封装
 * 负责 Token 管理、请求发送、错误处理和自动重试
 */

export interface TokenInfo {
  token: string;
  obtainedAt: number;
  nickname: string;
  username: string;
  userId: string;
}

export interface HttpClientConfig {
  baseUrl: string;
  username: string;
  password: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message: string;
}

const TOKEN_VALIDITY_MS = 25 * 60 * 1000; // 25分钟，比30分钟有效期提前刷新

let cachedToken: TokenInfo | null = null;

function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.replace(/\/+$/, '');
}

/** BOM/空白或非 application/json 但正文为 JSON 时的兼容解析 */
function parseResponseJson(text: string): unknown {
  const trimmed = text.replace(/^\uFEFF/, '').trim();
  if (!trimmed) return {};
  return JSON.parse(trimmed);
}

function isTokenExpired(): boolean {
  if (!cachedToken) return true;
  return Date.now() - cachedToken.obtainedAt > TOKEN_VALIDITY_MS;
}

export async function obtainToken(config: HttpClientConfig): Promise<TokenInfo> {
  const url = `${normalizeBaseUrl(config.baseUrl)}/magicflu/jwt`;
  const body = `j_username=${encodeURIComponent(config.username)}&j_password=${encodeURIComponent(config.password)}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });

  if (!response.ok) {
    throw new Error(`Token 获取失败: HTTP ${response.status}`);
  }

  const raw = await response.text();
  let data: Record<string, any>;
  try {
    data = parseResponseJson(raw) as Record<string, any>;
  } catch {
    const preview = raw.length > 160 ? `${raw.slice(0, 160)}…` : raw;
    throw new Error(`Token 获取失败: 响应非 JSON。${preview.replace(/\s+/g, ' ')}`);
  }
  if (!data.token) {
    throw new Error(`Token 获取失败: ${JSON.stringify(data)}`);
  }

  cachedToken = {
    token: data.token as string,
    obtainedAt: Date.now(),
    nickname: (data.nickname as string) || '',
    username: (data.username as string) || '',
    userId: (data.id as string) || '',
  };

  return cachedToken;
}

export async function getToken(config: HttpClientConfig): Promise<string> {
  if (isTokenExpired()) {
    await obtainToken(config);
  }
  return cachedToken!.token;
}

export function clearTokenCache(): void {
  cachedToken = null;
}

export function getTokenInfo(): TokenInfo | null {
  return cachedToken;
}

export async function apiRequest<T = any>(
  config: HttpClientConfig,
  method: string,
  path: string,
  body?: any,
  isRetry = false
): Promise<ApiResponse<T>> {
  const token = await getToken(config);
  const url = `${normalizeBaseUrl(config.baseUrl)}${path.startsWith('/') ? path : `/${path}`}`;

  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
  };

  if (body !== undefined && (method === 'POST' || method === 'PUT')) {
    headers['Content-Type'] = 'application/json';
  }

  const fetchOptions: RequestInit = { method, headers };
  if (body !== undefined && (method === 'POST' || method === 'PUT')) {
    fetchOptions.body = JSON.stringify(body);
  }

  let response: Response;
  try {
    response = await fetch(url, fetchOptions);
  } catch (err: any) {
    return { success: false, message: `网络请求失败: ${err.message}` };
  }

  if (response.status === 500 && !isRetry) {
    clearTokenCache();
    return apiRequest<T>(config, method, path, body, true);
  }

  const raw = await response.text();
  let data: any;
  try {
    data = parseResponseJson(raw);
  } catch {
    const preview = raw.length > 160 ? `${raw.slice(0, 160)}…` : raw;
    return {
      success: false,
      message: `响应解析失败: HTTP ${response.status}，正文非合法 JSON。片段: ${preview.replace(/\s+/g, ' ')}`,
    };
  }

  if (!response.ok) {
    const errMsg = data?.errmsg || data?.message || `HTTP ${response.status}`;
    return { success: false, message: `请求失败: ${errMsg}`, data };
  }

  return { success: true, data, message: 'ok' };
}
