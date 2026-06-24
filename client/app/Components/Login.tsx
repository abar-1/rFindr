"use client";

import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

export default function Login() {
  const { login, signup } = useAuth();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "signup") {
        await signup({ name, email, password });
      } else {
        await login(email, password);
      }
      // On success the AuthContext now holds the user; the cookie is set by the server.
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="w-full max-w-md text-black bg-white rounded-xl shadow-2xl p-8">
      <h2 className="text-3xl font-bold mb-6 text-indigo-700 text-center">
        {mode === "login" ? "Welcome back" : "Create your account"}
      </h2>

      <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
        {mode === "signup" && (
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-3 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none"
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-3 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-3 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none"
        />

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full mt-2 bg-indigo-600 text-white font-bold text-lg px-8 py-3 rounded-xl hover:bg-indigo-700 transition disabled:opacity-60"
        >
          {submitting ? "Please wait…" : mode === "login" ? "Sign In" : "Sign Up"}
        </button>
      </form>

      <p className="text-center text-sm text-gray-600 mt-4">
        {mode === "login" ? "No account yet?" : "Already have an account?"}{" "}
        <button
          type="button"
          onClick={() => {
            setError(null);
            setMode(mode === "login" ? "signup" : "login");
          }}
          className="text-indigo-600 font-semibold hover:underline"
        >
          {mode === "login" ? "Sign up" : "Sign in"}
        </button>
      </p>
    </div>
  );
}
