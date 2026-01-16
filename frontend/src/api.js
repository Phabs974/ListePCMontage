const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export function getToken() {
  return localStorage.getItem("token");
}

export function setToken(token) {
  if (token) {
    localStorage.setItem("token", token);
  } else {
    localStorage.removeItem("token");
  }
}

async function request(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Erreur API");
  }
  return response.json();
}

export async function login(username, password) {
  const res = await request("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  setToken(res.access_token);
  return res;
}

export function getMe() {
  return request("/auth/me");
}

export function listOrders(params = {}) {
  const search = new URLSearchParams(params).toString();
  return request(`/orders?${search}`);
}

export function createOrder(payload) {
  return request("/orders", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function updateOrder(id, payload) {
  return request(`/orders/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function deleteOrder(id) {
  return request(`/orders/${id}`, { method: "DELETE" });
}

export function importInvoice(file) {
  const form = new FormData();
  form.append("file", file);
  return request("/import/invoice", {
    method: "POST",
    body: form,
  });
}

export function listUsers() {
  return request("/users");
}

export function createUser(payload) {
  return request("/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function updateUser(id, payload) {
  return request(`/users/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function deleteUser(id) {
  return request(`/users/${id}`, { method: "DELETE" });
}
