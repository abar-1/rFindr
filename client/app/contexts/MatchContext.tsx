"use client";

import {
  createContext,
  useContext,
  useState,
  ReactNode,
  Dispatch,
  SetStateAction,
} from "react";

// ---- Types ----
export interface MatchResult {
  department: string | null;
  email: string;
  name: string;
  professor_id: number;
  research_areas: string;
  similarity: number;
  score?: number;
  [key: string]: any;
}

interface MatchContextType {
  matchResults: MatchResult[];
  setMatchResults: Dispatch<SetStateAction<MatchResult[]>>;
}

// ---- Create context ----
const MatchContext = createContext<MatchContextType | undefined>(undefined);

// ---- Provider ----
export function MatchProvider({ children }: { children: ReactNode }) {
  const [matchResults, setMatchResults] = useState<MatchResult[]>([]);

  return (
    <MatchContext.Provider value={{ matchResults, setMatchResults }}>
        {children}
    </MatchContext.Provider>
  )
  
}

// ---- Hook ----
export function useMatch() {
  const context = useContext(MatchContext);
  if (!context) throw new Error("useMatch must be used in MatchProvider");
  return context;
}
