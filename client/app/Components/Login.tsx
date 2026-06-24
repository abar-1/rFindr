"use client";

import { supabase } from "../lib/supabaseClient";
import { useState } from "react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin() {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      console.error(error.message);
      return;
    }

    window.location.href = "/dashboard";
  }

  return (
    <div>
      <input 
        type="email" 
        placeholder="Email"
        onChange={e => setEmail(e.target.value)}
      />
      <input 
        type="password" 
        placeholder="Password"
        onChange={e => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>Sign In</button>
    </div>
  );
}
