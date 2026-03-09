"use client";

import { useState } from "react";
import { PanelTop, Plus, Trash2, Move } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useConfiguration } from "@/hooks/useConfiguration";
import { COVER_ELEMENTS_CATALOG, type CoverElementSpec } from "@drov/shared";

export function CoverElementConfigurator() {
  const { selectedBox, coverElements, addCoverElement, removeCoverElement, updateCoverElement } =
    useConfiguration();
  const [selectedElementId, setSelectedElementId] = useState("");
  const [posX, setPosX] = useState(0);
  const [posY, setPosY] = useState(0);

  if (!selectedBox) return null;

  const plateW = selectedBox.mountingPlateX || 0;
  const plateH = selectedBox.mountingPlateY || 0;

  if (!plateW || !plateH) {
    return (
      <div className="rounded-lg border p-4">
        <h3 className="font-semibold text-sm flex items-center gap-2 text-muted-foreground">
          <PanelTop className="h-4 w-4" />
          Kapak Elemanları — Bu model için kullanılamaz
        </h3>
      </div>
    );
  }

  // Group by category
  const categories = new Map<string, CoverElementSpec[]>();
  for (const el of COVER_ELEMENTS_CATALOG) {
    const list = categories.get(el.category) || [];
    list.push(el);
    categories.set(el.category, list);
  }

  const categoryLabels: Record<string, string> = {
    pushbutton: "Butonlar",
    selector_switch: "Seçici Şalterler",
    indicator_lamp: "Sinyal Lambaları",
    emergency_stop: "Acil Stop",
    ammeter: "Ampermetreler",
    voltmeter: "Voltmetreler",
  };

  const handleAdd = () => {
    if (!selectedElementId) return;
    addCoverElement({
      elementId: selectedElementId,
      x: posX || plateW / 2,
      y: posY || plateH / 2,
    });
  };

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <h3 className="font-semibold text-sm flex items-center gap-2">
        <PanelTop className="h-4 w-4" />
        Kapak Elemanları
      </h3>

      {/* Element selector */}
      <div className="space-y-2">
        <Label className="text-xs">Eleman Seç</Label>
        <select
          className="flex h-8 w-full rounded-md border border-input bg-background px-3 py-1 text-xs ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          value={selectedElementId}
          onChange={(e) => setSelectedElementId(e.target.value)}
        >
          <option value="">Eleman seçin...</option>
          {Array.from(categories.entries()).map(([cat, elements]) => (
            <optgroup key={cat} label={categoryLabels[cat] || cat}>
              {elements.map((el) => (
                <option key={el.id} value={el.id}>
                  {el.name} ({el.cutoutWidth}x{el.cutoutHeight}mm)
                </option>
              ))}
            </optgroup>
          ))}
        </select>

        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label className="text-xs">X (mm)</Label>
            <Input
              type="number"
              min={0}
              max={plateW}
              value={posX || ""}
              onChange={(e) => setPosX(Number(e.target.value))}
              placeholder={String(Math.round(plateW / 2))}
              className="h-8 text-xs"
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Y (mm)</Label>
            <Input
              type="number"
              min={0}
              max={plateH}
              value={posY || ""}
              onChange={(e) => setPosY(Number(e.target.value))}
              placeholder={String(Math.round(plateH / 2))}
              className="h-8 text-xs"
            />
          </div>
        </div>

        <Button size="sm" onClick={handleAdd} disabled={!selectedElementId} className="w-full gap-1 text-xs">
          <Plus className="h-3 w-3" />
          Ekle
        </Button>
      </div>

      {/* Plate info */}
      <div className="text-xs text-muted-foreground">
        Montaj plakası: {plateW} x {plateH} mm
      </div>

      {/* Elements list */}
      {coverElements.length > 0 && (
        <div className="space-y-1">
          <Label className="text-xs">Eklenen Elemanlar</Label>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {coverElements.map((el, i) => {
              const spec = COVER_ELEMENTS_CATALOG.find((c) => c.id === el.elementId);
              return (
                <div key={i} className="flex items-center gap-2 rounded-md border px-2 py-1.5 text-xs">
                  <Move className="h-3 w-3 text-muted-foreground shrink-0" />
                  <span className="flex-1 truncate">{spec?.name || el.elementId}</span>
                  <div className="flex items-center gap-1">
                    <Input
                      type="number"
                      min={0}
                      max={plateW}
                      value={el.x}
                      onChange={(e) => updateCoverElement(i, { x: Number(e.target.value) })}
                      className="h-6 w-14 text-[10px] px-1"
                    />
                    <Input
                      type="number"
                      min={0}
                      max={plateH}
                      value={el.y}
                      onChange={(e) => updateCoverElement(i, { y: Number(e.target.value) })}
                      className="h-6 w-14 text-[10px] px-1"
                    />
                  </div>
                  <Button variant="ghost" size="icon" className="h-5 w-5 shrink-0" onClick={() => removeCoverElement(i)}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
