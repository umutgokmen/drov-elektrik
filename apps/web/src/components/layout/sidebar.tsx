"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Box, ClipboardList, Tag, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  {
    name: "Konfigüratör",
    href: "/configurator",
    icon: Wrench,
  },
  {
    name: "Siparişler",
    href: "/orders",
    icon: ClipboardList,
  },
  {
    name: "Etiketler",
    href: "/labels",
    icon: Tag,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-56 shrink-0 border-r md:block">
      <nav className="flex flex-col gap-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
