
export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:4000/api"
).replace(/\/+$/, "");
const TOKEN_KEY = "enersense_access_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function saveSession(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export type AuthUser = {
  id: number;
  email: string;
  full_name: string;
  role: string;
};

export async function validateSession(): Promise<AuthUser | null> {
  const token = getAccessToken();

  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 401 || response.status === 403) {
      clearSession();
      return null;
    }

    if (!response.ok) {
      throw new Error(`Session verification failed with status ${response.status}.`);
    }

    return (await response.json()) as AuthUser;
  } catch {
    // Keep the token if the server is temporarily unreachable.
    // A network failure does not prove that the token is invalid.
    throw new Error("Unable to verify your session. Please try again.");
  }
}

export function clearSession(): void {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(TOKEN_KEY);
  }
}
