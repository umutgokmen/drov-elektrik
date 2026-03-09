"use client";

import { useState } from "react";
import { Download, FileText, FileCode, Cuboid, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useConfiguration } from "@/hooks/useConfiguration";

type Format = "pdf" | "dxf" | "step";

export function GenerateButtons() {
  const { selectedBox, selectedBoxId, validation, terminals, holesTop, holesBottom, holesLeft, holesRight, switchgearItems, coverElements } =
    useConfiguration();
  const [loading, setLoading] = useState<Format | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canGenerate = selectedBox && validation?.isValid;

  const handleGenerate = async (format: Format) => {
    if (!canGenerate || !selectedBoxId) return;
    setLoading(format);
    setError(null);

    try {
      const payload = {
        box_id: selectedBoxId,
        terminals,
        holes_top: { count: holesTop.count, size: holesTop.size },
        holes_bottom: { count: holesBottom.count, size: holesBottom.size },
        holes_left: { count: holesLeft.count, size: holesLeft.size },
        holes_right: { count: holesRight.count, size: holesRight.size },
        switchgear: switchgearItems,
        cover_elements: coverElements,
      };

      const endpoint =
        format === "step" ? "/api/generate/step" : format === "dxf" ? "/api/generate/dxf" : "/api/generate/pdf";

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: "Dosya oluşturulamadı" }));
        throw new Error(errData.detail || `Hata: ${res.status}`);
      }

      // Download the file
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      const ext = format === "step" ? "step" : format;
      a.download = `${selectedBoxId}.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Bilinmeyen hata");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="rounded-lg border p-4 space-y-2">
      <h3 className="font-semibold text-sm flex items-center gap-2">
        <Download className="h-4 w-4" />
        Dosya Üretimi
      </h3>
      <div className="grid grid-cols-3 gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={!canGenerate || loading !== null}
          onClick={() => handleGenerate("pdf")}
          className="gap-1 text-xs"
        >
          {loading === "pdf" ? <Loader2 className="h-3 w-3 animate-spin" /> : <FileText className="h-3 w-3" />}
          PDF
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!canGenerate || loading !== null}
          onClick={() => handleGenerate("dxf")}
          className="gap-1 text-xs"
        >
          {loading === "dxf" ? <Loader2 className="h-3 w-3 animate-spin" /> : <FileCode className="h-3 w-3" />}
          DXF
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!canGenerate || loading !== null}
          onClick={() => handleGenerate("step")}
          className="gap-1 text-xs"
        >
          {loading === "step" ? <Loader2 className="h-3 w-3 animate-spin" /> : <Cuboid className="h-3 w-3" />}
          STEP
        </Button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
