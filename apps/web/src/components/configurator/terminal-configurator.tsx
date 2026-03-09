"use client";

import { Minus, Plus } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useConfiguration } from "@/hooks/useConfiguration";
import { COMPONENTS } from "@drov/shared";

export function TerminalConfigurator() {
  const { selectedBox, terminals, setTerminals, validation, layout } =
    useConfiguration();

  if (!selectedBox) {
    return (
      <div className="rounded-lg border p-4">
        <h3 className="font-semibold text-sm mb-2">Klemens Konfigürasyonu</h3>
        <p className="text-xs text-muted-foreground">
          Önce bir kutu modeli seçin.
        </p>
      </div>
    );
  }

  const terminalError = validation?.errors.find(
    (e) => e.field === "terminals"
  );
  const terminalWarning = validation?.warnings.find(
    (e) => e.field === "terminals"
  );

  const maxTerminals = selectedBox.maxTerminals;
  const pct = Math.min(100, (terminals / maxTerminals) * 100);

  const railMargin = 20;
  const termWidth = COMPONENTS.TERMINAL_2_5.width;
  const availablePerRail = Math.floor(
    (selectedBox.internalWidth - 2 * railMargin) / termWidth
  );
  const physicalMax = availablePerRail * selectedBox.railCount;

  return (
    <div className="rounded-lg border p-4 space-y-4">
      <div>
        <h3 className="font-semibold text-sm">Klemens Konfigürasyonu</h3>
        <p className="text-xs text-muted-foreground">
          {selectedBox.railCount} ray, ray başına maks. {availablePerRail}{" "}
          klemens
        </p>
      </div>

      <div className="flex items-center gap-3">
        <Button
          variant="outline"
          size="icon"
          className="h-8 w-8"
          onClick={() => setTerminals(Math.max(0, terminals - 1))}
          disabled={terminals <= 0}
        >
          <Minus className="h-3 w-3" />
        </Button>
        <Input
          type="number"
          min={0}
          max={maxTerminals}
          value={terminals}
          onChange={(e) =>
            setTerminals(Math.max(0, parseInt(e.target.value) || 0))
          }
          className={cn(
            "h-8 w-20 text-center text-sm",
            terminalError && "border-destructive"
          )}
        />
        <Button
          variant="outline"
          size="icon"
          className="h-8 w-8"
          onClick={() => setTerminals(terminals + 1)}
          disabled={terminals >= maxTerminals}
        >
          <Plus className="h-3 w-3" />
        </Button>
        <span className="text-xs text-muted-foreground">
          / {maxTerminals}
        </span>
      </div>

      {/* Capacity bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-[10px] text-muted-foreground">
          <span>Kapasite</span>
          <span>{Math.round(pct)}%</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className={cn(
              "h-full rounded-full transition-all",
              pct < 70
                ? "bg-green-500"
                : pct < 90
                  ? "bg-yellow-500"
                  : "bg-red-500"
            )}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Rail distribution */}
      {layout && layout.rails.length > 0 && (
        <div className="space-y-1">
          <span className="text-[10px] text-muted-foreground">
            Ray dağılımı:
          </span>
          <div className="flex gap-2">
            {layout.rails.map((rail, i) => (
              <div
                key={rail.id}
                className="flex-1 rounded border p-1.5 text-center"
              >
                <div className="text-[10px] text-muted-foreground">
                  Ray {i + 1}
                </div>
                <div className="text-sm font-medium">
                  {rail.terminalCount}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {terminalError && (
        <p className="text-xs text-destructive">{terminalError.message}</p>
      )}
      {terminalWarning && !terminalError && (
        <div className="flex items-center gap-1">
          <Badge variant="warning" className="text-[10px]">
            Uyarı
          </Badge>
          <span className="text-xs text-yellow-400">
            {terminalWarning.message}
          </span>
        </div>
      )}
    </div>
  );
}
