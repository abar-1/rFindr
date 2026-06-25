"use client";

import {
  createContext,
  useContext,
  useCallback,
  useState,
  ReactNode,
} from "react";

// ---- Types ----
type ToastType = "success" | "error" | "info";

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

// ---- Context ----
const ToastContext = createContext<ToastContextType | undefined>(undefined);

const AUTO_DISMISS_MS = 4000;

const STYLES: Record<ToastType, string> = {
  success: "bg-green-600",
  error: "bg-red-600",
  info: "bg-indigo-600",
};

const ICONS: Record<ToastType, string> = {
  success: "✓",
  error: "✕",
  info: "i",
};

// ---- Provider ----
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback(
    (message: string, type: ToastType = "info") => {
      // Date.now() collisions are unlikely for human-paced toasts; add a salt to be safe.
      const id = Date.now() + Math.random();
      setToasts((prev) => [...prev, { id, message, type }]);
      setTimeout(() => dismiss(id), AUTO_DISMISS_MS);
    },
    [dismiss]
  );

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      {/* Toast viewport: top-right, stacked, above the history overlay (z-50). */}
      <div className="pointer-events-none fixed top-4 right-4 z-[100] flex flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="alert"
            onClick={() => dismiss(toast.id)}
            className={`pointer-events-auto flex items-center gap-3 rounded-lg px-4 py-3 text-white shadow-lg cursor-pointer max-w-sm animate-[toast-in_0.2s_ease-out] ${STYLES[toast.type]}`}
          >
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/25 text-xs font-bold">
              {ICONS[toast.type]}
            </span>
            <p className="text-sm font-medium">{toast.message}</p>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

// ---- Hook ----
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast must be used in ToastProvider");
  return context;
}
