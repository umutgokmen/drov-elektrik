"use client";

import { useState } from "react";
import { Package, Trash2, Eye, Send, CheckCircle, Factory, Clock, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useConfigurations, useUpdateConfigurationStatus, useDeleteConfiguration } from "@/hooks/useOrders";

const statusLabels: Record<string, { label: string; variant: "default" | "warning" | "success" | "destructive" }> = {
  draft: { label: "Taslak", variant: "default" },
  submitted: { label: "Gönderildi", variant: "warning" },
  approved: { label: "Onaylandı", variant: "success" },
  production: { label: "Üretimde", variant: "success" },
};

const statusIcons: Record<string, React.ReactNode> = {
  draft: <Clock className="h-3 w-3" />,
  submitted: <Send className="h-3 w-3" />,
  approved: <CheckCircle className="h-3 w-3" />,
  production: <Factory className="h-3 w-3" />,
};

export function OrdersList() {
  const { data: configurations, isLoading, error } = useConfigurations();
  const updateStatus = useUpdateConfigurationStatus();
  const deleteConfig = useDeleteConfiguration();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="rounded-lg border p-4 animate-pulse">
            <div className="h-4 w-48 bg-muted rounded mb-2" />
            <div className="h-3 w-32 bg-muted rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border p-6 text-center text-sm text-destructive">
        Siparişler yüklenirken hata: {error.message}
      </div>
    );
  }

  const filtered = (configurations || []).filter((c: Record<string, unknown>) => {
    const matchSearch =
      !search ||
      (c.name as string || "").toLowerCase().includes(search.toLowerCase()) ||
      (c.drawing_number as string || "").toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "all" || c.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Ara (isim, çizim no...)"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8 h-9"
          />
        </div>
        <select
          className="h-9 rounded-md border border-input bg-background px-3 text-sm"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">Tüm Durumlar</option>
          <option value="draft">Taslak</option>
          <option value="submitted">Gönderildi</option>
          <option value="approved">Onaylandı</option>
          <option value="production">Üretimde</option>
        </select>
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <div className="rounded-lg border p-6 text-center text-sm text-muted-foreground">
          {configurations?.length === 0 ? "Henüz konfigürasyon kaydedilmedi." : "Aramayla eşleşen sonuç yok."}
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((config: Record<string, unknown>) => {
            const id = config.id as string;
            const name = config.name as string | null;
            const drawingNumber = config.drawing_number as string | null;
            const status = config.status as string;
            const terminalCount = config.terminals as number;
            const createdAt = config.created_at as string;
            const statusInfo = statusLabels[status] || statusLabels.draft;
            const boxInfo = config.box_models as Record<string, unknown> | null;

            return (
              <div key={id} className="rounded-lg border p-4 hover:bg-muted/30 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Package className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium text-sm">
                        {name || drawingNumber || "İsimsiz Konfigürasyon"}
                      </span>
                      <Badge variant={statusInfo.variant} className="gap-1 text-[10px]">
                        {statusIcons[status]}
                        {statusInfo.label}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      {drawingNumber && <span className="font-mono">{drawingNumber}</span>}
                      {boxInfo && <span>{boxInfo.name as string}</span>}
                      <span>{terminalCount} klemens</span>
                      <span>
                        {new Date(createdAt).toLocaleDateString("tr-TR", {
                          day: "numeric",
                          month: "short",
                          year: "numeric",
                        })}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1">
                    {status === "draft" && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-xs gap-1 h-7"
                        onClick={() => updateStatus.mutate({ id, status: "submitted" })}
                        disabled={updateStatus.isPending}
                      >
                        <Send className="h-3 w-3" />
                        Gönder
                      </Button>
                    )}
                    {status === "submitted" && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-xs gap-1 h-7"
                        onClick={() => updateStatus.mutate({ id, status: "approved" })}
                        disabled={updateStatus.isPending}
                      >
                        <CheckCircle className="h-3 w-3" />
                        Onayla
                      </Button>
                    )}
                    {status === "approved" && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-xs gap-1 h-7"
                        onClick={() => updateStatus.mutate({ id, status: "production" })}
                        disabled={updateStatus.isPending}
                      >
                        <Factory className="h-3 w-3" />
                        Üretime Al
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() => {
                        if (confirm("Bu konfigürasyonu silmek istediğinize emin misiniz?")) {
                          deleteConfig.mutate(id);
                        }
                      }}
                      disabled={deleteConfig.isPending}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
