"use client";

import { useState, useCallback } from "react";
import { Eye, Maximize2, RotateCcw, Cuboid, PanelTop, ZoomIn, ZoomOut } from "lucide-react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { useConfiguration } from "@/hooks/useConfiguration";
import { DrawingCanvas } from "./drawing-canvas";
import { IsometricView } from "./isometric-view";
import { CoverLayoutCanvas } from "./cover-layout-canvas";

export function DrawingPreview() {
  const { activeView, setActiveView, selectedBox, layout, holesTop, holesBottom, holesLeft, holesRight, terminals, coverElements } =
    useConfiguration();
  const [zoom, setZoom] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleZoomIn = useCallback(() => setZoom((z) => Math.min(z + 25, 200)), []);
  const handleZoomOut = useCallback(() => setZoom((z) => Math.max(z - 25, 25)), []);
  const handleReset = useCallback(() => setZoom(100), []);

  const handleFullscreen = useCallback(() => {
    setIsFullscreen((f) => !f);
  }, []);

  const containerClass = isFullscreen
    ? "fixed inset-0 z-50 bg-background flex flex-col"
    : "rounded-lg border bg-card technical-frame";

  return (
    <div className={containerClass}>
      <div className="flex items-center justify-between border-b px-4 py-2">
        <h2 className="text-sm font-semibold font-mono text-primary tracking-wider uppercase">
          Teknik Çizim
        </h2>
        <div className="flex items-center gap-1">
          <span className="text-xs text-muted-foreground mr-2 font-mono">%{zoom}</span>
          <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-primary" title="Uzaklaştır" onClick={handleZoomOut}>
            <ZoomOut className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-primary" title="Yakınlaştır" onClick={handleZoomIn}>
            <ZoomIn className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-primary" title="Sıfırla" onClick={handleReset}>
            <RotateCcw className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-primary" title="Tam Ekran" onClick={handleFullscreen}>
            <Maximize2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      <Tabs value={activeView} onValueChange={(v) => setActiveView(v as "2d" | "3d" | "cover")}>
        <div className="border-b px-4">
          <TabsList className="h-8">
            <TabsTrigger value="2d" className="gap-1 text-xs h-7">
              <Eye className="h-3 w-3" />
              2D
            </TabsTrigger>
            <TabsTrigger value="3d" className="gap-1 text-xs h-7">
              <Cuboid className="h-3 w-3" />
              3D
            </TabsTrigger>
            <TabsTrigger value="cover" className="gap-1 text-xs h-7">
              <PanelTop className="h-3 w-3" />
              Kapak
            </TabsTrigger>
          </TabsList>
        </div>

        <div
          className="overflow-auto flex-1 blueprint-grid"
          style={{ minHeight: "500px", maxHeight: isFullscreen ? "calc(100vh - 90px)" : "75vh" }}
        >
          <div
            style={{ transform: `scale(${zoom / 100})`, transformOrigin: "top left", width: `${10000 / zoom}%` }}
          >
            <TabsContent value="2d" className="p-2">
              {selectedBox && layout ? (
                <DrawingCanvas
                  box={selectedBox}
                  terminals={terminals}
                  holesTop={layout.holesTop}
                  holesBottom={layout.holesBottom}
                  holesLeft={layout.holesLeft}
                  holesRight={layout.holesRight}
                  holeSizeTop={holesTop.size}
                  holeSizeBottom={holesBottom.size}
                  holeSizeLeft={holesLeft.size}
                  holeSizeRight={holesRight.size}
                  rails={layout.rails}
                />
              ) : (
                <div className="flex h-[400px] items-center justify-center text-sm text-muted-foreground font-mono">
                  Kutu modeli seçin
                </div>
              )}
            </TabsContent>
            <TabsContent value="3d" className="p-2">
              {selectedBox ? (
                <IsometricView
                  box={selectedBox}
                  holesTopCount={holesTop.count}
                  holesBottomCount={holesBottom.count}
                  holesLeftCount={holesLeft.count}
                  holesRightCount={holesRight.count}
                />
              ) : (
                <div className="flex h-[400px] items-center justify-center text-sm text-muted-foreground font-mono">
                  Kutu modeli seçin
                </div>
              )}
            </TabsContent>
            <TabsContent value="cover" className="p-2">
              {selectedBox ? (
                <CoverLayoutCanvas box={selectedBox} coverElements={coverElements} />
              ) : (
                <div className="flex h-[400px] items-center justify-center text-sm text-muted-foreground font-mono">
                  Kutu modeli seçin
                </div>
              )}
            </TabsContent>
          </div>
        </div>
      </Tabs>
    </div>
  );
}
