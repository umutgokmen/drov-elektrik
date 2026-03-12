"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, User, Zap, Wrench, ClipboardList, Tag } from "lucide-react";
import { Button } from "@/components/ui/button";
// import { useAuth } from "@/hooks/useAuth";
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

export function Header() {
  const user = null;
  const profile = null;
  const signOut = () => {};
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-12 items-center px-4">
        <div className="flex items-center gap-2 font-bold text-lg">
          <Zap className="h-5 w-5 text-primary" />
          <span className="font-mono">Drov Elektrik</span>
        </div>

        <nav className="ml-8 flex items-center gap-1">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "relative flex items-center gap-2 px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          {user && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span>{profile?.fullName || user.email}</span>
            </div>
          )}
          <Button variant="ghost" size="icon" onClick={signOut} title="Çıkış Yap">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
