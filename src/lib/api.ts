/**
 * API utilities for admin and user authentication and requests.
 */

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "https://app.bellahasias.ru";

// Telegram WebApp types
declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        initDataUnsafe: {
          user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
            photo_url?: string;
          };
          auth_date: number;
          hash: string;
        };
        ready: () => void;
        expand: () => void;
        close: () => void;
        version: string;
        platform: string;
      };
    };
  }
}

export interface AdminLoginRequest {
  email: string;
  password: string;
}

export interface AdminLoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
    [key: string]: any;
  };
}

const ADMIN_TOKEN_KEY = "access_token";

/**
 * Get admin token from localStorage.
 * Uses access_token so admin API requests send Authorization automatically.
 */
export function getAdminToken(): string | null {
  return localStorage.getItem(ADMIN_TOKEN_KEY);
}

/**
 * Set admin token in localStorage.
 */
export function setAdminToken(token: string): void {
  localStorage.setItem(ADMIN_TOKEN_KEY, token);
}

/**
 * Remove admin token from localStorage.
 */
export function removeAdminToken(): void {
  localStorage.removeItem(ADMIN_TOKEN_KEY);
}

/**
 * Check if admin is authenticated.
 */
export function isAdminAuthenticated(): boolean {
  return getAdminToken() !== null;
}

/**
 * Admin login API request.
 */
export async function adminLogin(
  credentials: AdminLoginRequest
): Promise<AdminLoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/admin/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(error.detail || "Invalid email or password");
  }

  return response.json();
}

/**
 * Validate admin token by making a request to dashboard.
 */
export async function validateAdminToken(): Promise<boolean> {
  const token = getAdminToken();
  if (!token) {
    return false;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/admin/dashboard`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 401 || response.status === 403) {
      removeAdminToken();
      return false;
    }

    return response.ok;
  } catch (error) {
    removeAdminToken();
    return false;
  }
}

export interface AdminSetting {
  key: string;
  value: unknown;
  description?: string | null;
}

/**
 * Get all admin settings.
 */
export async function getAdminSettings(): Promise<Record<string, AdminSetting>> {
  return adminApiRequest<Record<string, AdminSetting>>("/api/admin/settings");
}

/**
 * Update admin setting by key.
 */
export async function updateAdminSetting(
  key: string,
  value: unknown
): Promise<AdminSetting> {
  return adminApiRequest<AdminSetting>(`/api/admin/settings/${key}`, {
    method: "PUT",
    body: JSON.stringify({ value }),
  });
}

export interface AdminDashboard {
  users_count: number;
  active_subscriptions: number;
  revenue_today: number;
  revenue_total: number;
  churn_rate: number;
}

export async function getAdminDashboard(): Promise<AdminDashboard> {
  return adminApiRequest<AdminDashboard>("/api/admin/dashboard");
}

export interface AdminUser {
  id: string;
  telegram_id?: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  role: string;
  is_admin: boolean;
  created_at: string;
}

export async function getAdminUsers(skip = 0, limit = 100): Promise<AdminUser[]> {
  return adminApiRequest<AdminUser[]>(`/api/admin/users?skip=${skip}&limit=${limit}`);
}

export interface AdminSubscription {
  id: string;
  user_id: string;
  plan_id: string;
  status: string;
  start_date: string;
  end_date: string;
  auto_renew: boolean;
  created_at: string;
}

export async function getAdminSubscriptions(skip = 0, limit = 100): Promise<AdminSubscription[]> {
  return adminApiRequest<AdminSubscription[]>(`/api/admin/subscriptions?skip=${skip}&limit=${limit}`);
}

export async function banUser(userId: string): Promise<{ success: boolean; message: string }> {
  return adminApiRequest(`/api/admin/users/${userId}/ban`, { method: "POST" });
}

export async function extendSubscription(
  subscriptionId: string,
  days: number
): Promise<AdminSubscription> {
  return adminApiRequest<AdminSubscription>(
    `/api/admin/subscriptions/${subscriptionId}/extend?days=${days}`,
    { method: "POST" }
  );
}

export async function revokeSubscription(
  subscriptionId: string
): Promise<AdminSubscription> {
  return adminApiRequest<AdminSubscription>(
    `/api/admin/subscriptions/${subscriptionId}/revoke`,
    { method: "POST" }
  );
}

export async function getUserSubscriptions(userId: string): Promise<AdminSubscription[]> {
  return adminApiRequest<AdminSubscription[]>(`/api/admin/users/${userId}/subscriptions`);
}

export interface AdminPlan {
  id: string;
  name: string;
  description?: string;
  price: number;
  first_month_price?: number;
  duration_days: number;
  features?: string[];
  currency: string;
  is_active: boolean;
}

export async function getAdminPlans(): Promise<AdminPlan[]> {
  return adminApiRequest<AdminPlan[]>("/api/admin/plans");
}

export async function createAdminPlan(data: Partial<AdminPlan>): Promise<AdminPlan> {
  return adminApiRequest<AdminPlan>("/api/admin/plans", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAdminPlan(planId: string, data: Partial<AdminPlan>): Promise<AdminPlan> {
  return adminApiRequest<AdminPlan>(`/api/admin/plans/${planId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteAdminPlan(planId: string): Promise<void> {
  return adminApiRequest(`/api/admin/plans/${planId}`, { method: "DELETE" });
}

export interface BroadcastSendRequest {
  text: string;
  media_type?: "photo" | "video";
  media_url?: string;
  target: "all" | "selected";
  user_ids?: string[];
}

export interface BroadcastSendResponse {
  sent: number;
  failed: number;
  total: number;
  errors: string[];
}

export async function sendBroadcast(data: BroadcastSendRequest): Promise<BroadcastSendResponse> {
  return adminApiRequest<BroadcastSendResponse>("/api/admin/broadcasts/send", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export interface TestTelegramResult {
  ok: boolean;
  bot?: unknown;
  channel?: unknown;
  channel_error?: string;
  error?: string;
}

export async function testTelegram(): Promise<TestTelegramResult> {
  return adminApiRequest<TestTelegramResult>("/api/admin/test/telegram", {
    method: "POST",
  });
}

export interface TestPaymentResult {
  ok: boolean;
  message?: string;
  error?: string;
}

export async function testPayment(): Promise<TestPaymentResult> {
  return adminApiRequest<TestPaymentResult>("/api/admin/test/payment", {
    method: "POST",
  });
}

/** MiniApp content from API (public, no auth) */
export interface MiniappContent {
  plans: Array<{
    id: string;
    name: string;
    price: number;
    first_month_price?: number;
    duration_days: number;
    currency: string;
    features?: string[];
    is_active: boolean;
    [key: string]: unknown;
  }>;
  telegram_bot_link: string;
  contact_link: string;
  offer_url: string;
  miniapp_url: string;
  support_username: string;
  price_note: string;
  price_after: string;
  plan_title: string;
  features: string[];
  faq_items: Array<{ q: string; a: string }>;
}

/** Get MiniApp content (public endpoint) */
export async function getMiniappContent(): Promise<MiniappContent> {
  const response = await fetch(`${API_BASE_URL}/api/miniapp/content`);
  if (!response.ok) {
    throw new Error("Не удалось загрузить контент");
  }
  return response.json();
}

/**
 * Make authenticated admin API request.
 */
export async function adminApiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAdminToken();
  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    removeAdminToken();
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

/**
 * Telegram authentication types and utilities.
 */
export interface TelegramAuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    telegram_id: number;
    username?: string;
    first_name: string;
    last_name?: string;
    avatar_url?: string;
    role: string;
    [key: string]: any;
  };
}

/**
 * Get user token from localStorage.
 */
export function getUserToken(): string | null {
  return localStorage.getItem("user_token");
}

/**
 * Set user token in localStorage.
 */
export function setUserToken(token: string): void {
  localStorage.setItem("user_token", token);
}

/**
 * Remove user token from localStorage.
 */
export function removeUserToken(): void {
  localStorage.removeItem("user_token");
}

/**
 * Check if user is authenticated.
 */
export function isUserAuthenticated(): boolean {
  return getUserToken() !== null;
}

/**
 * Get Telegram WebApp initData.
 */
export function getTelegramInitData(): string | null {
  if (typeof window !== "undefined" && window.Telegram?.WebApp) {
    return window.Telegram.WebApp.initData;
  }
  return null;
}

/**
 * Authenticate with Telegram WebApp initData.
 */
export async function authenticateTelegram(
  initData: string
): Promise<TelegramAuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/telegram`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ initData }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Authentication failed" }));
    throw new Error(error.detail || "Invalid Telegram authentication data");
  }

  return response.json();
}

/**
 * Make authenticated user API request.
 */
export async function userApiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getUserToken();
  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    removeUserToken();
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}
