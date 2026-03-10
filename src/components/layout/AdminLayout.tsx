import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BarChart3, Users, CreditCard, Settings, FileText, ArrowLeft, LogOut, Receipt, Send, Banknote } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { removeAdminToken } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const adminNav = [
  { to: "/admin", icon: BarChart3, label: "Дашборд", end: true },
  { to: "/admin/users", icon: Users, label: "Пользователи" },
  { to: "/admin/subscriptions", icon: CreditCard, label: "Подписки" },
  { to: "/admin/payments", icon: Banknote, label: "Оплаты" },
  { to: "/admin/plans", icon: Receipt, label: "Тарифы" },
  { to: "/admin/broadcasts", icon: Send, label: "Рассылки" },
  { to: "/admin/content", icon: FileText, label: "Контент MiniApp" },
  { to: "/admin/settings", icon: Settings, label: "Настройки" },
];

export function AdminLayout() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleLogout = () => {
    removeAdminToken();
    toast({
      title: "Выход выполнен",
      description: "Вы успешно вышли из админ-панели",
    });
    navigate("/admin/login");
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="hidden md:flex w-64 flex-col border-r border-border bg-card p-4 gap-1">
        <NavLink to="/" className="flex items-center gap-2 px-3 py-2 mb-4 text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="h-4 w-4" />
          <span className="text-sm">На сайт</span>
        </NavLink>
        <h2 className="px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Админ-панель</h2>
        {adminNav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
        <div className="mt-auto pt-4 border-t border-border">
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start text-muted-foreground hover:text-foreground"
            onClick={handleLogout}
          >
            <LogOut className="h-4 w-4 mr-3" />
            Выйти
          </Button>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="flex-1 flex flex-col">
        <header className="md:hidden flex items-center justify-between gap-3 px-4 py-3 border-b border-border bg-card">
          <div className="flex items-center gap-3">
            <NavLink to="/" className="text-muted-foreground"><ArrowLeft className="h-5 w-5" /></NavLink>
            <h1 className="text-base font-semibold">Админ-панель</h1>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            className="text-muted-foreground"
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </header>

        {/* Mobile nav */}
        <div className="md:hidden flex overflow-x-auto gap-1 px-4 py-2 border-b border-border bg-card">
          {adminNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors",
                  isActive ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                )
              }
            >
              <item.icon className="h-3.5 w-3.5" />
              {item.label}
            </NavLink>
          ))}
        </div>

        <main className="flex-1 p-4 md:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
