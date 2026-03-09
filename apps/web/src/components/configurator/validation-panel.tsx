"use client";

import { AlertCircle, AlertTriangle, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useConfiguration } from "@/hooks/useConfiguration";

export function ValidationPanel() {
  const { selectedBox, validation } = useConfiguration();

  if (!selectedBox) {
    return null;
  }

  if (!validation) {
    return null;
  }

  const { errors, warnings, isValid } = validation;

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm">Doğrulama</h3>
        {isValid ? (
          <Badge variant="success" className="gap-1">
            <CheckCircle2 className="h-3 w-3" />
            Geçerli
          </Badge>
        ) : (
          <Badge variant="destructive" className="gap-1">
            <AlertCircle className="h-3 w-3" />
            {errors.length} hata
          </Badge>
        )}
      </div>

      {errors.length > 0 && (
        <div className="space-y-1.5">
          {errors.map((error, i) => (
            <div
              key={i}
              className="flex items-start gap-2 rounded-md bg-destructive/10 p-2"
            >
              <AlertCircle className="h-3.5 w-3.5 mt-0.5 text-destructive shrink-0" />
              <div className="text-xs">
                <span className="font-medium text-destructive">
                  {error.field}:
                </span>{" "}
                <span className="text-destructive/80">{error.message}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="space-y-1.5">
          {warnings.map((warning, i) => (
            <div
              key={i}
              className="flex items-start gap-2 rounded-md bg-yellow-500/10 p-2"
            >
              <AlertTriangle className="h-3.5 w-3.5 mt-0.5 text-yellow-500 shrink-0" />
              <div className="text-xs">
                <span className="font-medium text-yellow-500">
                  {warning.field}:
                </span>{" "}
                <span className="text-yellow-500/80">{warning.message}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {isValid && errors.length === 0 && warnings.length === 0 && (
        <p className="text-xs text-muted-foreground">
          Tüm kontroller başarılı. Konfigürasyon geçerli.
        </p>
      )}
    </div>
  );
}
