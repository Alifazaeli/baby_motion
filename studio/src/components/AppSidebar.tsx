"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BookOpen,
  LayoutGrid,
  Globe,
  Type,
  BarChart3,
  LogOut,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { logout } from "@/lib/api";

const NAV_ITEMS = [
  { href: "/stories",    label: "Stories",    icon: BookOpen },
  { href: "/categories", label: "Categories", icon: LayoutGrid },
  { href: "/languages",  label: "Languages",  icon: Globe },
  { href: "/ui-strings", label: "UI Strings", icon: Type },
  { href: "/analytics",  label: "Analytics",  icon: BarChart3 },
];

export function AppSidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    logout();
    document.cookie = "studio_access_token=; path=/; max-age=0";
    router.push("/login");
  }

  return (
    <aside className="flex h-screen w-60 flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border">
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sidebar-primary">
          <Sparkles className="h-4 w-4 text-sidebar-primary-foreground" />
        </div>
        <div>
          <p className="text-sm font-semibold leading-none">Content Studio</p>
          <p className="text-xs text-sidebar-foreground/50 mt-0.5">BabyMotion</p>
        </div>
      </div>

      <Separator className="bg-sidebar-border" />

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-3">
        <nav className="space-y-0.5">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link key={href} href={href}>
                <div
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                    active
                      ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {label}
                </div>
              </Link>
            );
          })}
        </nav>
      </ScrollArea>

      <Separator className="bg-sidebar-border" />

      {/* Footer */}
      <div className="px-3 py-3">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-sidebar-foreground/50 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground transition-colors"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
