export const dynamic = "force-dynamic";

import { OrdersList } from "@/components/orders/orders-list";

export default function OrdersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Siparişler</h1>
        <p className="text-muted-foreground">
          Kayıtlı konfigürasyonlar ve sipariş geçmişi
        </p>
      </div>
      <OrdersList />
    </div>
  );
}
