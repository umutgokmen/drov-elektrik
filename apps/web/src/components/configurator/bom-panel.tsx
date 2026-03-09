"use client";

import { Package } from "lucide-react";
import { useConfiguration } from "@/hooks/useConfiguration";
import { SALT_MALZEME, HOLE_SIZES, COMPONENTS } from "@drov/shared";

interface BOMLine {
  partName: string;
  partCode: string;
  quantity: number;
  isSaltMalzeme: boolean;
}

function calculateBOM(config: ReturnType<typeof useConfiguration>): BOMLine[] {
  const items: BOMLine[] = [];
  const { selectedBox, terminals, holesTop, holesBottom, holesLeft, holesRight } = config;

  if (!selectedBox) return items;

  // Salt malzeme (standard components)
  for (const sm of SALT_MALZEME) {
    const qty =
      sm.partCode === "pnl_302203_CLIPFIX-35-5"
        ? selectedBox.railCount * 2
        : sm.quantity;
    items.push({
      partName: sm.partName,
      partCode: sm.partCode,
      quantity: qty,
      isSaltMalzeme: true,
    });
  }

  // DIN Rails
  if (selectedBox.railCount > 0) {
    items.push({
      partName: "DIN Ray NS 35",
      partCode: "DIN-NS35",
      quantity: selectedBox.railCount,
      isSaltMalzeme: false,
    });
  }

  // Terminals
  if (terminals > 0) {
    items.push({
      partName: "UT 2,5 Klemens",
      partCode: "pnl_UT2.5",
      quantity: terminals,
      isSaltMalzeme: false,
    });
  }

  // Holes per side
  const holeSides = [
    { config: holesTop, label: "Üst" },
    { config: holesBottom, label: "Alt" },
    { config: holesLeft, label: "Sol" },
    { config: holesRight, label: "Sağ" },
  ];

  // Aggregate holes by size
  const holeTotals: Record<string, number> = {};
  for (const side of holeSides) {
    if (side.config.count > 0) {
      holeTotals[side.config.size] =
        (holeTotals[side.config.size] || 0) + side.config.count;
    }
  }

  for (const [sizeId, count] of Object.entries(holeTotals)) {
    const sizeSpec = HOLE_SIZES.find((h) => h.id === sizeId);
    if (sizeSpec) {
      items.push({
        partName: `${sizeId} Kablo Rakorü`,
        partCode: sizeSpec.code,
        quantity: count,
        isSaltMalzeme: false,
      });
    }
  }

  // Blind plugs for unused holes (same size as cable glands)
  for (const [sizeId, count] of Object.entries(holeTotals)) {
    items.push({
      partName: `${sizeId} Kör Tapa`,
      partCode: `${sizeId}-BP`,
      quantity: 0, // no blind plugs by default - all holes used
      isSaltMalzeme: false,
    });
  }

  return items.filter((item) => item.quantity > 0);
}

export function BOMPanel() {
  const config = useConfiguration();
  const { selectedBox } = config;

  if (!selectedBox) {
    return null;
  }

  const bomItems = calculateBOM(config);
  const totalParts = bomItems.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm flex items-center gap-2">
          <Package className="h-4 w-4" />
          Malzeme Listesi (BOM)
        </h3>
        <span className="text-xs text-muted-foreground">
          {totalParts} parça
        </span>
      </div>

      <div className="overflow-hidden rounded-md border">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-2 py-1.5 text-left font-medium">#</th>
              <th className="px-2 py-1.5 text-left font-medium">Parça</th>
              <th className="px-2 py-1.5 text-left font-medium">Kod</th>
              <th className="px-2 py-1.5 text-right font-medium">Adet</th>
            </tr>
          </thead>
          <tbody>
            {bomItems.map((item, i) => (
              <tr
                key={i}
                className="border-b last:border-0 hover:bg-muted/30"
              >
                <td className="px-2 py-1.5 text-muted-foreground">
                  {i + 1}
                </td>
                <td className="px-2 py-1.5">
                  {item.partName}
                  {item.isSaltMalzeme && (
                    <span className="ml-1 text-[10px] text-muted-foreground">
                      (sabit)
                    </span>
                  )}
                </td>
                <td className="px-2 py-1.5 font-mono text-muted-foreground">
                  {item.partCode}
                </td>
                <td className="px-2 py-1.5 text-right font-medium">
                  {item.quantity}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
