"use client";

import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useConfiguration } from "@/hooks/useConfiguration";
import { HOLE_SIZES } from "@drov/shared";

const SIDES = [
  { key: "top" as const, label: "Üst", icon: ArrowUp, storeKey: "holesTop" as const },
  { key: "bottom" as const, label: "Alt", icon: ArrowDown, storeKey: "holesBottom" as const },
  { key: "left" as const, label: "Sol", icon: ArrowLeft, storeKey: "holesLeft" as const },
  { key: "right" as const, label: "Sağ", icon: ArrowRight, storeKey: "holesRight" as const },
] as const;

export function HoleConfigurator() {
  const config = useConfiguration();
  const { selectedBox, validation, setHoles } = config;

  if (!selectedBox) {
    return (
      <div className="rounded-lg border p-4">
        <h3 className="font-semibold text-sm mb-2">Delik Konfigürasyonu</h3>
        <p className="text-xs text-muted-foreground">Önce bir kutu modeli seçin.</p>
      </div>
    );
  }

  const getMaxHoles = (side: "top" | "bottom" | "left" | "right") => {
    if (side === "top" || side === "bottom") return selectedBox.maxHolesShort;
    return selectedBox.maxHolesLong;
  };

  const getSideLength = (side: "top" | "bottom" | "left" | "right") => {
    if (side === "top" || side === "bottom") return selectedBox.internalWidth;
    return selectedBox.internalLength;
  };

  const getFieldError = (field: string) =>
    validation?.errors.find((e) => e.field === field);

  return (
    <div className="rounded-lg border p-4 space-y-4">
      <div>
        <h3 className="font-semibold text-sm">Delik Konfigürasyonu</h3>
        <p className="text-xs text-muted-foreground">
          Her kenara delik sayısı ve boyutu belirleyin
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {SIDES.map(({ key, label, icon: Icon, storeKey }) => {
          const holeConfig = config[storeKey];
          const error = getFieldError(storeKey);
          const maxHoles = getMaxHoles(key);
          const sideLength = getSideLength(key);

          return (
            <div
              key={key}
              className="space-y-2 rounded-md border p-3"
            >
              <div className="flex items-center gap-2">
                <Icon className="h-3.5 w-3.5 text-muted-foreground" />
                <Label className="text-xs font-medium">{label}</Label>
                <span className="ml-auto text-[10px] text-muted-foreground">
                  {sideLength}mm
                </span>
              </div>

              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  min={0}
                  max={maxHoles}
                  value={holeConfig.count}
                  onChange={(e) =>
                    setHoles(key, {
                      ...holeConfig,
                      count: Math.max(0, parseInt(e.target.value) || 0),
                    })
                  }
                  className={`h-8 w-16 text-xs ${error ? "border-destructive" : ""}`}
                />
                <select
                  value={holeConfig.size}
                  onChange={(e) =>
                    setHoles(key, { ...holeConfig, size: e.target.value })
                  }
                  className="h-8 rounded-md border bg-background px-2 text-xs"
                >
                  {HOLE_SIZES.map((hs) => (
                    <option key={hs.id} value={hs.id}>
                      {hs.id} ({hs.diameter}mm)
                    </option>
                  ))}
                </select>
              </div>

              {error && (
                <p className="text-[10px] text-destructive">{error.message}</p>
              )}

              <div className="flex items-center justify-between">
                <span className="text-[10px] text-muted-foreground">
                  Maks: {maxHoles}
                </span>
                {holeConfig.count > 0 && !error && (
                  <Badge variant="success" className="text-[10px] px-1.5 py-0">
                    OK
                  </Badge>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex justify-between text-xs text-muted-foreground border-t pt-2">
        <span>
          Toplam delik:{" "}
          {config.holesTop.count +
            config.holesBottom.count +
            config.holesLeft.count +
            config.holesRight.count}
        </span>
        <span>
          Maks toplam:{" "}
          {selectedBox.maxHolesLong * 2 + selectedBox.maxHolesShort * 2}
        </span>
      </div>
    </div>
  );
}
