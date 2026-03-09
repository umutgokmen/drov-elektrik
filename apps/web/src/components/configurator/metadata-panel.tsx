"use client";

import { Save, FileText } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useConfiguration } from "@/hooks/useConfiguration";
import { useSaveConfiguration } from "@/hooks/useOrders";

export function MetadataPanel() {
  const { selectedBox, selectedBoxId, terminals, holesTop, holesBottom, holesLeft, holesRight, configName, notes, setConfigName, setNotes, validation } =
    useConfiguration();
  const saveConfig = useSaveConfiguration();

  if (!selectedBox) return null;

  const handleSave = () => {
    if (!selectedBoxId || !validation?.isValid) return;
    saveConfig.mutate({
      boxModelId: selectedBoxId,
      name: configName || undefined,
      terminals,
      holesTop,
      holesBottom,
      holesLeft,
      holesRight,
      notes: notes || undefined,
    });
  };

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <h3 className="font-semibold text-sm flex items-center gap-2">
        <FileText className="h-4 w-4" />
        Konfigürasyon Bilgileri
      </h3>

      <div className="space-y-2">
        <div className="space-y-1">
          <Label className="text-xs">Konfigürasyon Adı</Label>
          <Input
            placeholder="Örn: Motor Kumanda Panosu"
            value={configName}
            onChange={(e) => setConfigName(e.target.value)}
            className="h-8 text-xs"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Notlar</Label>
          <textarea
            placeholder="Ek notlar..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-xs ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            rows={2}
          />
        </div>
      </div>

      <Button
        onClick={handleSave}
        disabled={!validation?.isValid || saveConfig.isPending}
        className="w-full gap-2"
        size="sm"
      >
        <Save className="h-3.5 w-3.5" />
        {saveConfig.isPending ? "Kaydediliyor..." : "Konfigürasyonu Kaydet"}
      </Button>

      {saveConfig.isSuccess && (
        <p className="text-xs text-green-400">Konfigürasyon kaydedildi.</p>
      )}
      {saveConfig.isError && (
        <p className="text-xs text-destructive">
          Kaydetme başarısız: {saveConfig.error?.message}
        </p>
      )}
    </div>
  );
}
