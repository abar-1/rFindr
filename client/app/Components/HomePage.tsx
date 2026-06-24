"use client";
import MatchForm from "./MatchForm";
import MatchResults from "./MatchResults";
import Navbar from "./Navbar";


export default function HomePage() {
  
  // Placeholder function for MatchForm submission

  return (
    <div>
        <Navbar />
        <div className="min-h-screen bg-gray-50 ps-8 flex gap-10 flex-row justify-center py-10 align-top">
            
            {/* 2. Main content container: flex-grow fills remaining space. 
                3. justify-center and items-center centers the content vertically and horizontally. */}
            <main className="flex flex-grow justify-center items-center p-4">
                <MatchForm />
            </main>

        </div>
        <MatchResults />
    </div>
  );
}