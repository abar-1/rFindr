"use client";
import React, { useState } from "react";
import { useMatch } from "../contexts/MatchContext";
import { useToast } from "../contexts/ToastContext";

// Reject prompts too short to be a meaningful research interest; saves compute
// on the embedding + vector search for useless/redundant queries.
const MIN_INTERESTS_LENGTH = 30;

// Pull a human-readable message out of an error response (FastAPI sends { detail }).
async function parseErrorDetail(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
  } catch {
    /* no JSON body */
  }
  return fallback;
}

const MatchForm = () => {
  const { matchResults, setMatchResults } = useMatch();
  const { showToast } = useToast();
  const [interests, setInterests] = useState("");
  const [numMatches, setNumMatches] = useState(5);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // ---- Client-side validation: keep junk prompts off the backend ----
    const trimmed = interests.trim();
    if (!trimmed) {
      showToast("Please enter your research interests first.", "error");
      return;
    }
    if (trimmed.length < MIN_INTERESTS_LENGTH) {
      showToast(
        `Please add a bit more detail (at least ${MIN_INTERESTS_LENGTH} characters).`,
        "error"
      );
      return;
    }

    setIsLoading(true);
    // Use a runtime-configurable API URL (set NEXT_PUBLIC_API_URL in .env.local) with a localhost fallback
    const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

    try {
        const res = await fetch(`${API_URL}/api/rag/matches`, {
          method: "POST",
          credentials: "include", // send the httpOnly auth cookie
          headers: {
            "Content-Type": "application/json",
          },
          // Backend reads the user id from the auth cookie; body is { interests, num_matches }.
          body: JSON.stringify({
            interests: trimmed,
            num_matches: numMatches,
          }),
        });

        if (!res.ok) {
          const detail = await parseErrorDetail(
            res,
            res.status === 401
              ? "Your session expired. Please log in again."
              : "Something went wrong finding matches. Please try again."
          );
          console.error("API error response:", res.status, detail);
          throw new Error(detail);
        }

        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          console.log("Match results: ", data);
          setMatchResults(data);
          showToast(`Found ${data.length} match${data.length === 1 ? "" : "es"}!`, "success");
        } else {
          setMatchResults([]);
          showToast("No matches found. Try broadening your interests.", "info");
        }
    } catch (err) {
      console.log("Error during match submission: ", err);
      const message =
        err instanceof TypeError
          ? "Can't reach the server. Check your connection and try again."
          : err instanceof Error
            ? err.message
            : "Something went wrong. Please try again.";
      showToast(message, "error");
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
              placeholder="e.g. AI, Quantum Computing, Sustainability. Write as much as you can!"
              className="w-full text-black px-4 py-3 h-24 border border-gray-300 rounded-lg focus:ring-3 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none text-base transition duration-200 ease-in-out resize-none overflow-hidden"
            />
            <p className="mt-1 text-right text-xs text-gray-400">
              {interests.trim().length < MIN_INTERESTS_LENGTH
                ? `${MIN_INTERESTS_LENGTH - interests.trim().length} more characters needed`
                : "Looks good"}
            </p>
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
            disabled={isLoading}
            className="w-full mt-4 bg-indigo-600 text-white font-bold text-lg px-8 py-3 rounded-xl hover:bg-indigo-700 transition duration-300 ease-in-out transform hover:scale-[1.01] shadow-lg shadow-indigo-500/50 focus:outline-none focus:ring-4 focus:ring-indigo-500 focus:ring-opacity-50 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none"
          >
            {isLoading ? "Finding Matches…" : "Find Matches"}
          </button>
        </form>
      </div>
  );
};

export default MatchForm;
