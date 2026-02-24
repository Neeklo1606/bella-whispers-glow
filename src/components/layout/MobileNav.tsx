import { NavLink } from "react-router-dom";
import { Home, Newspaper, Heart, User } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/dashboard", icon: Home, label: "Главная" },
  { to: "/dashboard/feed", icon: Newspaper, label: "Контент" },
  { to: "/dashboard/favorites", icon: Heart, label: "Избранное" },
  { to: "/dashboard/profile", icon: User, label: "Профиль" },
];

export function MobileNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-card/95 backdrop-blur-lg safe-area-bottom">
      <div className="flex items-center justify-around px-2 py-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/dashboard"}
            className={({ isActive }) =>
              cn(
                "flex flex-col items-center gap-0.5 px-3 py-2 rounded-xl transition-colors duration-200 tap-highlight-none min-w-[60px]",
                isActive ? "text-primary" : "text-muted-foreground"
              )
            }
          >
            <item.icon className="h-5 w-5" />
            <span className="text-[11px] font-medium">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
