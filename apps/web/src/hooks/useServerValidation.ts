"use client";

import { useEffect, useRef, useState } from "react";
import { useConfiguration } from "./useConfiguration";

interface ServerValidationResult {
  is_valid: boolean;
  errors: { field: string; message: string }[];
  warnings: { field: string; message: string }[];
}

const PYTHON_API_URL = "/api/validate";
const DEBOUNCE_MS = 600;

export function useServerValidation() {
  const { selectedBox, selectedBoxId, terminals, holesTop, holesBottom, holesLeft, holesRight } =
    useConfiguration();
  const [serverResult, setServerResult] = useState<ServerValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!selectedBoxId || !selectedBox) {
      setServerResult(null);
      return;
    }

    if (timerRef.current) clearTimeout(timerRef.current);
    if (abortRef.current) abortRef.current.abort();

    timerRef.current = setTimeout(async () => {
      const controller = new AbortController();
      abortRef.current = controller;
      setIsValidating(true);

      try {
        const res = await fetch(PYTHON_API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
          body: JSON.stringify({
            box_id: selectedBoxId,
            terminals,
            holes_top: { count: holesTop.count, size: holesTop.size },
            holes_bottom: { count: holesBottom.count, size: holesBottom.size },
            holes_left: { count: holesLeft.count, size: holesLeft.size },
            holes_right: { count: holesRight.count, size: holesRight.size },
          }),
        });

        if (res.ok) {
          const data = await res.json();
          setServerResult(data);
        }
      } catch {
        // Aborted or network error - ignore
      } finally {
        setIsValidating(false);
      }
    }, DEBOUNCE_MS);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [selectedBoxId, selectedBox, terminals, holesTop, holesBottom, holesLeft, holesRight]);

  return { serverResult, isValidating };
}
