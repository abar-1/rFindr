"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

// Runtime-configurable API URL (set NEXT_PUBLIC_API_URL in .env.local), localhost fallback.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---- Types ----
export interface User {
  id: number;
  name: string | null;
  email: string;
  research_interests: string | null;
  major: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface SignupInput {
  name: string;
  email: string;
  password: string;
  research_interests?: string;
  major?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean; // true while the initial /me hydration is in flight
  login: (email: string, password: string) => Promise<User>;
  signup: (input: SignupInput) => Promise<User>;
  logout: () => Promise<void>;
}

// ---- Context ----
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ---- Helpers ----
async function parseError(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
  } catch {
    /* response had no JSON body */
  }
  return fallback;
}

// ---- Provider ----
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Hydrate auth state from the httpOnly cookie on mount. The token isn't
  // readable from JS by design, so the backend's /me is the source of truth.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/auth/me`, {
          credentials: "include",
        });
        if (!cancelled && res.ok) {
          const data = await res.json();
          setUser(data.user);
        }
      } catch {
        /* network error -> treat as logged out */
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function login(email: string, password: string): Promise<User> {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      throw new Error(await parseError(res, "Login failed."));
    }
    const data = await res.json();
    setUser(data.user);
    return data.user;
  }

  async function signup(input: SignupInput): Promise<User> {
    const res = await fetch(`${API_URL}/api/auth/signup`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    if (!res.ok) {
      throw new Error(await parseError(res, "Signup failed."));
    }
    const data = await res.json();
    setUser(data.user);
    return data.user;
  }

  async function logout(): Promise<void> {
    try {
      await fetch(`${API_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } finally {
      setUser(null);
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// ---- Hook ----
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used in AuthProvider");
  return context;
}
