export const dynamic = "force-dynamic";

import { BoxSelector } from "@/components/configurator/box-selector";
import { HoleConfigurator } from "@/components/configurator/hole-configurator";
import { TerminalConfigurator } from "@/components/configurator/terminal-configurator";
import { SwitchgearConfigurator } from "@/components/configurator/switchgear-configurator";
import { CoverElementConfigurator } from "@/components/configurator/cover-element-configurator";
import { ValidationPanel } from "@/components/configurator/validation-panel";
import { BOMPanel } from "@/components/configurator/bom-panel";
import { MetadataPanel } from "@/components/configurator/metadata-panel";
import { GenerateButtons } from "@/components/configurator/generate-buttons";
import { DrawingPreview } from "@/components/drawing/drawing-preview";

export default function ConfiguratorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight font-mono">Konfigüratör</h1>
        <p className="text-muted-foreground">
          Ex-proof pano konfigürasyonu oluşturun
        </p>
      </div>

      <BoxSelector />
      <DrawingPreview />

      <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        <div className="space-y-4">
          <TerminalConfigurator />
          <CoverElementConfigurator />
        </div>
        <div className="space-y-4">
          <HoleConfigurator />
          <ValidationPanel />
          <GenerateButtons />
        </div>
        <div className="space-y-4">
          <SwitchgearConfigurator />
          <BOMPanel />
          <MetadataPanel />
        </div>
      </div>
    </div>
  );
}
