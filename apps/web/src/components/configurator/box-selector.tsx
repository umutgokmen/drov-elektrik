"use client";

import { Box, Check, Layers, Maximize2, Ruler } from "lucide-react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useConfiguration } from "@/hooks/useConfiguration";
import type { BoxModel } from "@drov/shared";

function BoxModelCard({
  model,
  isSelected,
  onSelect,
}: {
  model: BoxModel;
  isSelected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        "relative flex flex-col gap-2 rounded-lg border p-4 text-left transition-all hover:border-primary/50 hover:bg-accent/50",
        isSelected && "border-primary bg-accent ring-1 ring-primary"
      )}
    >
      {isSelected && (
        <div className="absolute right-2 top-2">
          <Check className="h-4 w-4 text-primary" />
        </div>
      )}
      <div className="flex items-center gap-2">
        <Box className="h-4 w-4 text-muted-foreground" />
        <span className="font-semibold">{model.name}</span>
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <Ruler className="h-3 w-3" />
          <span>
            {model.internalLength}x{model.internalWidth}x{model.internalDepth}mm
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Layers className="h-3 w-3" />
          <span>{model.railCount} ray</span>
        </div>
        <div className="flex items-center gap-1">
          <Maximize2 className="h-3 w-3" />
          <span>Maks. {model.maxTerminals} klemens</span>
        </div>
        <div>
          <span>
            Delik: {model.maxHolesLong}/{model.maxHolesShort}
          </span>
        </div>
      </div>
      {model.ipRating && (
        <Badge variant="outline" className="w-fit text-xs">
          {model.ipRating}
        </Badge>
      )}
    </button>
  );
}

export function BoxSelector() {
  const { selectedBoxId, selectedSeries, series, seriesModels, setSelectedBox, setSelectedSeries } =
    useConfiguration();

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Kutu Seçimi</h2>
        <p className="text-sm text-muted-foreground">
          Pano serisi ve modelini seçin
        </p>
      </div>

      <Tabs value={selectedSeries} onValueChange={setSelectedSeries}>
        <TabsList className="w-full justify-start">
          {series.map((s) => (
            <TabsTrigger key={s.id} value={s.id} className="text-xs">
              {s.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {series.map((s) => (
          <TabsContent key={s.id} value={s.id}>
            <div className="mb-2 text-xs text-muted-foreground">
              {s.description} — Kenar boşluğu: {s.edgeMargin}mm, Delik aralığı:{" "}
              {s.holeClearance}mm
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {seriesModels.map((model) => (
                <BoxModelCard
                  key={model.id}
                  model={model}
                  isSelected={selectedBoxId === model.id}
                  onSelect={() => setSelectedBox(model.id)}
                />
              ))}
            </div>
            {seriesModels.length === 0 && (
              <p className="py-8 text-center text-sm text-muted-foreground">
                Bu seride henüz model bulunmuyor.
              </p>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
