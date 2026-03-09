export const dynamic = "force-dynamic";

import { LabelGenerator } from "@/components/labels/label-generator";

export default function LabelsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Etiketler</h1>
        <p className="text-muted-foreground">
          Pano etiket üretimi
        </p>
      </div>
      <LabelGenerator />
    </div>
  );
}
