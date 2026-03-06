import { NavLink } from "react-router-dom";
import { Home, CreditCard, User, MessageCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", icon: Home, label: "Главная" },
  { to: "/pricing", icon: CreditCard, label: "Тарифы" },
  { to: "/dashboard/profile", icon: User, label: "Профиль" },
];

const TELEGRAM_LINK = "https://t.me/Bella_hasias";

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-background/95 backdrop-blur-md">
      <div className="flex items-center justify-around px-2 py-1.5 pb-[calc(0.375rem+env(safe-area-inset-bottom))]">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-colors tap-highlight-none min-w-[56px]",
                isActive ? "text-foreground" : "text-muted-foreground"
              )
            }
          >
            <item.icon className="h-[18px] w-[18px]" />
            <span className="text-[9px] tracking-[0.05em]">{item.label}</span>
          </NavLink>
        ))}
        <a
          href={TELEGRAM_LINK}
          target="_blank"
          rel="noopener noreferrer"
          className="flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl text-muted-foreground hover:text-foreground transition-colors tap-highlight-none min-w-[56px]"
        >
          <MessageCircle className="h-[18px] w-[18px]" />
          <span className="text-[9px] tracking-[0.05em]">Чат</span>
        </a>
      </div>
    </nav>
  );
}
