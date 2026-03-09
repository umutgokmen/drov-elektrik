"use client";

import { useState } from "react";
import { Tag, Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function LabelGenerator() {
  const [panelName, setPanelName] = useState("");
  const [orderNo, setOrderNo] = useState("");
  const [project, setProject] = useState("");
  const [customer, setCustomer] = useState("");
  const [notes, setNotes] = useState("");
  const [pageSize, setPageSize] = useState("A4");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!panelName) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/generate/label", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          panel_name: panelName,
          order_no: orderNo || undefined,
          project: project || undefined,
          customer: customer || undefined,
          notes: notes || undefined,
          page_size: pageSize,
          date: new Date().toLocaleDateString("tr-TR"),
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: "Etiket oluşturulamadı" }));
        throw new Error(errData.detail || `Hata: ${res.status}`);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `etiket-${panelName.replace(/\s+/g, "-")}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Bilinmeyen hata");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl space-y-6">
      <div className="rounded-lg border p-6 space-y-4">
        <h3 className="font-semibold text-sm flex items-center gap-2">
          <Tag className="h-4 w-4" />
          Etiket Bilgileri
        </h3>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label className="text-xs">Pano Adı *</Label>
            <Input
              placeholder="Örn: Motor Kumanda Panosu"
              value={panelName}
              onChange={(e) => setPanelName(e.target.value)}
              className="h-9"
            />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Sipariş No</Label>
            <Input
              placeholder="Örn: SIP-2026-001"
              value={orderNo}
              onChange={(e) => setOrderNo(e.target.value)}
              className="h-9"
            />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Proje</Label>
            <Input
              placeholder="Proje adı"
              value={project}
              onChange={(e) => setProject(e.target.value)}
              className="h-9"
            />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Müşteri</Label>
            <Input
              placeholder="Müşteri adı"
              value={customer}
              onChange={(e) => setCustomer(e.target.value)}
              className="h-9"
            />
          </div>
          <div className="space-y-1.5 sm:col-span-2">
            <Label className="text-xs">Notlar</Label>
            <textarea
              placeholder="Ek notlar..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              rows={2}
            />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Sayfa Boyutu</Label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={pageSize}
              onChange={(e) => setPageSize(e.target.value)}
            >
              <option value="A4">A4</option>
              <option value="A5">A5</option>
              <option value="A6">A6</option>
            </select>
          </div>
        </div>

        <Button onClick={handleGenerate} disabled={!panelName || loading} className="w-full gap-2">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
          {loading ? "Oluşturuluyor..." : "Etiket PDF Oluştur"}
        </Button>

        {error && <p className="text-xs text-destructive">{error}</p>}
      </div>

      {/* Preview placeholder */}
      <div className="rounded-lg border p-6">
        <h3 className="font-semibold text-sm mb-3">Önizleme</h3>
        <div className="aspect-[1/1.414] bg-muted/30 rounded-md flex items-center justify-center border-2 border-dashed border-muted">
          <div className="text-center space-y-2 px-4">
            <Tag className="h-8 w-8 text-muted-foreground mx-auto" />
            <p className="text-sm font-medium">{panelName || "Pano Adı"}</p>
            {orderNo && <p className="text-xs text-muted-foreground">{orderNo}</p>}
            {customer && <p className="text-xs text-muted-foreground">{customer}</p>}
            <p className="text-xs text-muted-foreground">
              {new Date().toLocaleDateString("tr-TR")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
