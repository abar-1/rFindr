"use client";
import React, { useState } from "react";
import { useMatch } from "../contexts/MatchContext";

const MatchForm = () => {
  const { matchResults, setMatchResults } = useMatch();
  const [interests, setInterests] = useState("");
  const [numMatches, setNumMatches] = useState(5);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Loading");
    setIsLoading(true);
    // Use a runtime-configurable API URL (set NEXT_PUBLIC_API_URL in .env.local) with a localhost fallback
    const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

    try {
        const res = await fetch(`${API_URL}/api/matches`, {
          method: "POST",
          credentials: "include", // send the httpOnly auth cookie
          headers: {
            "Content-Type": "application/json",
          },
          // Backend reads the user id from the auth cookie; body is { interests, num_matches }.
          body: JSON.stringify({
            interests: interests,
            num_matches: numMatches,
          }),
        });

        if (!res.ok) {
          const text = await res.text();
          console.error("API error response:", res.status, text);
          throw new Error(`API error ${res.status}`);
          
        }
        
        const data = await res.json();
        if (data) {
          console.log("Match results: ", data);
          setMatchResults(data);
        }
    } catch (err) {
      console.log("Error during match submission: ", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-lg text-black bg-white rounded-xl shadow-2xl p-8 transform transition-all hover:shadow-xl">
        
        <h2 className="text-3xl font-bold mb-8 text-indigo-700 text-center">
          Discover Your Research Matches 🚀
        </h2>

        <form
          onSubmit={handleSubmit}
          className="flex flex-col items-center space-y-6"
        >
          
          <div className="w-full">
            <label className="block text-gray-700 font-semibold mb-2 text-left text-sm">
              Your Research Interests
            </label>
            {/* 💡 CHANGE: Swapped <input> for <textarea> to enable multi-line input and wrapping/overflow control */}
            <textarea
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              placeholder="e.g. AI, Quantum Computing, Sustainability. Write more if you like!"
              className="w-full text-black px-4 py-3 h-24 border border-gray-300 rounded-lg focus:ring-3 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none text-base transition duration-200 ease-in-out resize-none overflow-hidden"
            />
          </div>

          <div className="w-full">
            <label className="block text-gray-700 font-semibold mb-2 text-left text-sm">
              Maximum Number of Matches
            </label>
            <div className="relative">
                <select
                value={numMatches}
                onChange={(e) => setNumMatches(Number(e.target.value))}
                className="appearance-none w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-3 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none text-base bg-white transition duration-200 ease-in-out cursor-pointer pr-10"
                >
                {[1, 3, 5, 10, 15, 20].map((n) => (
                    <option key={n} value={n}>
                    {n} Matches
                    </option>
                ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                </div>
            </div>
          </div>

          <button
            type="submit"
            className="w-full mt-4 bg-indigo-600 text-white font-bold text-lg px-8 py-3 rounded-xl hover:bg-indigo-700 transition duration-300 ease-in-out transform hover:scale-[1.01] shadow-lg shadow-indigo-500/50 focus:outline-none focus:ring-4 focus:ring-indigo-500 focus:ring-opacity-50"
          >
            Find Matches
          </button>
        </form>
      </div>
  );
};

export default MatchForm;
