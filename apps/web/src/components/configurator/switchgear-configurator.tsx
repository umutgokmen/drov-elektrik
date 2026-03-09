"use client";

import { useState } from "react";
import { Cpu, Plus, Trash2, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useConfiguration } from "@/hooks/useConfiguration";
import { SWITCHGEAR_CATALOG, type SwitchgearComponent } from "@drov/shared";

export function SwitchgearConfigurator() {
  const { selectedBox, switchgearItems, addSwitchgearItem, removeSwitchgearItem } = useConfiguration();
  const [selectedComponentId, setSelectedComponentId] = useState("");
  const [railIndex, setRailIndex] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [currentRating, setCurrentRating] = useState<number | undefined>();
  const [coilVoltage, setCoilVoltage] = useState<number | undefined>();

  if (!selectedBox) return null;

  const railCount = selectedBox.railCount || 1;
  const selectedComponent = SWITCHGEAR_CATALOG.find((c) => c.id === selectedComponentId);

  // Group catalog by category
  const categories = new Map<string, SwitchgearComponent[]>();
  for (const comp of SWITCHGEAR_CATALOG) {
    const list = categories.get(comp.category) || [];
    list.push(comp);
    categories.set(comp.category, list);
  }

  const categoryLabels: Record<string, string> = {
    fuse: "Sigortalar",
    mcb: "Otomatik Kesiciler",
    relay: "Röleler",
    contactor: "Kontaktörler",
    switch: "Şalterler",
    terminal: "Klemensler",
    surge_protector: "Parafudrlar",
    timer: "Zamanlayıcılar",
    power_supply: "Güç Kaynakları",
  };

  const handleAdd = () => {
    if (!selectedComponentId) return;
    addSwitchgearItem({
      componentId: selectedComponentId,
      railIndex,
      quantity,
      currentRating,
      coilVoltage,
    });
    setQuantity(1);
    setCurrentRating(undefined);
    setCoilVoltage(undefined);
  };

  // Calculate rail usage
  const railUsage = Array.from({ length: railCount }, (_, ri) => {
    const items = switchgearItems.filter((si) => si.railIndex === ri);
    let totalModules = 0;
    for (const item of items) {
      const comp = SWITCHGEAR_CATALOG.find((c) => c.id === item.componentId);
      if (comp) totalModules += comp.dinModules * item.quantity;
    }
    return totalModules;
  });

  const maxModulesPerRail = Math.floor((selectedBox.internalWidth - 40) / 17.5); // ~17.5mm per DIN module

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <h3 className="font-semibold text-sm flex items-center gap-2">
        <Cpu className="h-4 w-4" />
        Switchgear Konfigürasyonu
      </h3>

      {/* Component selector */}
      <div className="space-y-2">
        <Label className="text-xs">Bileşen Seç</Label>
        <select
          className="flex h-8 w-full rounded-md border border-input bg-background px-3 py-1 text-xs ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          value={selectedComponentId}
          onChange={(e) => {
            setSelectedComponentId(e.target.value);
            const comp = SWITCHGEAR_CATALOG.find((c) => c.id === e.target.value);
            if (comp?.currentRating?.length) setCurrentRating(comp.currentRating[0]);
            if (comp?.coilVoltage?.length) setCoilVoltage(comp.coilVoltage[0]);
          }}
        >
          <option value="">Bileşen seçin...</option>
          {Array.from(categories.entries()).map(([cat, comps]) => (
            <optgroup key={cat} label={categoryLabels[cat] || cat}>
              {comps.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.dinModules} modül)
                </option>
              ))}
            </optgroup>
          ))}
        </select>

        {selectedComponent && (
          <div className="grid grid-cols-3 gap-2">
            {/* Rail index */}
            <div className="space-y-1">
              <Label className="text-xs">Ray</Label>
              <select
                className="flex h-8 w-full rounded-md border border-input bg-background px-2 py-1 text-xs"
                value={railIndex}
                onChange={(e) => setRailIndex(Number(e.target.value))}
              >
                {Array.from({ length: railCount }, (_, i) => (
                  <option key={i} value={i}>R{i + 1}</option>
                ))}
              </select>
            </div>

            {/* Quantity */}
            <div className="space-y-1">
              <Label className="text-xs">Adet</Label>
              <Input
                type="number"
                min={1}
                max={20}
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                className="h-8 text-xs"
              />
            </div>

            {/* Current rating (if available) */}
            {selectedComponent.currentRating && selectedComponent.currentRating.length > 0 && (
              <div className="space-y-1">
                <Label className="text-xs">Akım (A)</Label>
                <select
                  className="flex h-8 w-full rounded-md border border-input bg-background px-2 py-1 text-xs"
                  value={currentRating || ""}
                  onChange={(e) => setCurrentRating(Number(e.target.value))}
                >
                  {selectedComponent.currentRating.map((r) => (
                    <option key={r} value={r}>{r}A</option>
                  ))}
                </select>
              </div>
            )}

            {/* Coil voltage (if available) */}
            {selectedComponent.coilVoltage && selectedComponent.coilVoltage.length > 0 && (
              <div className="space-y-1">
                <Label className="text-xs">Bobin (V)</Label>
                <select
                  className="flex h-8 w-full rounded-md border border-input bg-background px-2 py-1 text-xs"
                  value={coilVoltage || ""}
                  onChange={(e) => setCoilVoltage(Number(e.target.value))}
                >
                  {selectedComponent.coilVoltage.map((v) => (
                    <option key={v} value={v}>{v}V</option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}

        <Button size="sm" onClick={handleAdd} disabled={!selectedComponentId} className="w-full gap-1 text-xs">
          <Plus className="h-3 w-3" />
          Ekle
        </Button>
      </div>

      {/* Rail usage bars */}
      <div className="space-y-1">
        <Label className="text-xs">Ray Doluluk</Label>
        {railUsage.map((usage, ri) => {
          const pct = maxModulesPerRail > 0 ? (usage / maxModulesPerRail) * 100 : 0;
          return (
            <div key={ri} className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-6">R{ri + 1}</span>
              <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                  style={{ width: `${Math.min(pct, 100)}%` }}
                />
              </div>
              <span className="text-xs text-muted-foreground">{usage}/{maxModulesPerRail}</span>
            </div>
          );
        })}
      </div>

      {/* Items list */}
      {switchgearItems.length > 0 && (
        <div className="space-y-1">
          <Label className="text-xs">Eklenen Bileşenler</Label>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {switchgearItems.map((item, i) => {
              const comp = SWITCHGEAR_CATALOG.find((c) => c.id === item.componentId);
              return (
                <div key={i} className="flex items-center justify-between rounded-md border px-2 py-1.5 text-xs">
                  <div className="flex items-center gap-2">
                    <Zap className="h-3 w-3 text-muted-foreground" />
                    <span>{comp?.name || item.componentId}</span>
                    <Badge variant="outline" className="text-[10px] h-4">
                      R{item.railIndex + 1}
                    </Badge>
                    <span className="text-muted-foreground">x{item.quantity}</span>
                    {item.currentRating && (
                      <span className="text-muted-foreground">{item.currentRating}A</span>
                    )}
                  </div>
                  <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => removeSwitchgearItem(i)}>
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
