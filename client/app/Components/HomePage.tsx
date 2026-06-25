"use client";
import { useState } from "react";
import MatchForm from "./MatchForm";
import MatchResults from "./MatchResults";
import Navbar from "./Navbar";
import Login from "./Login";
import ChatHistory from "./ChatHistory";
import { useAuth } from "../contexts/AuthContext";


export default function HomePage() {
  const { user, loading } = useAuth();
  const [historyOpen, setHistoryOpen] = useState(false);

  return (
    <div>
        <Navbar onOpenHistory={() => setHistoryOpen(true)} />
        <div className="min-h-screen bg-gray-50 ps-8 flex gap-10 flex-row justify-center pt-28 pb-10 align-top">

            {/* Show the match flow only when signed in; otherwise prompt to log in. */}
            <main className="flex flex-grow justify-center items-center p-4">
                {loading ? null : user ? <MatchForm /> : <Login />}
            </main>

        </div>
        {user ? <MatchResults /> : null}

        {/* Full-screen chat-history overlay, opened from the Navbar. */}
        {user ? (
          <ChatHistory open={historyOpen} onClose={() => setHistoryOpen(false)} />
        ) : null}
    </div>
  );
}