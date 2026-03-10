import { motion } from "framer-motion";
import { User, CreditCard, HelpCircle, LogOut, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useMiniappContent } from "@/hooks/useMiniappContent";
import { StatusIndicator } from "@/components/StatusIndicator";

export default function Profile() {
  const { data: content } = useMiniappContent();
  const telegramLink = content?.telegram_bot_link ?? "https://t.me/bellahasias_bot";
  const contactLink = content?.contact_link ?? "https://t.me/Bella_hasias";
  return (
    <div className="min-h-screen bg-background pb-20">
      <header className="sticky top-0 z-50 bg-background/90 backdrop-blur-md border-b border-border">
        <div className="flex items-center justify-center h-12">
          <span className="text-[10px] tracking-[0.2em] uppercase text-foreground">Профиль</span>
        </div>
      </header>

      <div className="px-5 py-6 space-y-5 max-w-[480px] mx-auto">
        {/* User info */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-3">
          <Avatar className="h-12 w-12">
            <AvatarFallback className="bg-secondary text-foreground">
              <User className="h-5 w-5" />
            </AvatarFallback>
          </Avatar>
          <div>
            <p className="text-sm font-medium">Пользователь</p>
            <p className="text-[11px] text-muted-foreground">@username</p>
          </div>
        </motion.div>

        {/* Subscription status */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-card rounded-xl p-4 shadow-card"
        >
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-[10px] tracking-[0.15em] uppercase text-muted-foreground">Подписка</p>
              <p className="text-sm font-medium">Базовая · 990 ₽/мес</p>
            </div>
            <StatusIndicator status="active" />
          </div>
          <div className="space-y-1.5 text-[12px] mb-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Следующее списание</span>
              <span>15 марта 2026</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Способ оплаты</span>
              <span>•••• 4242</span>
            </div>
          </div>
          <div className="h-1 bg-muted rounded-full overflow-hidden mb-3">
            <div className="h-full bg-foreground/30 rounded-full" style={{ width: "65%" }} />
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="flex-1 text-[11px] h-9" asChild>
              <a href={telegramLink} target="_blank" rel="noopener noreferrer">Управлять</a>
            </Button>
            <Button variant="ghost" size="sm" className="text-destructive text-[11px] h-9" asChild>
              <a href={telegramLink} target="_blank" rel="noopener noreferrer">Отменить</a>
            </Button>
          </div>
        </motion.div>

        {/* Menu items */}
        <div className="space-y-1.5">
          {[
            { icon: CreditCard, label: "История платежей", to: "/dashboard/subscription" },
            { icon: HelpCircle, label: "Поддержка", to: contactLink, external: true },
          ].map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.03 }}
            >
              {item.external ? (
                <a
                  href={item.to}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 bg-card rounded-xl p-3.5 shadow-card tap-highlight-none"
                >
                  <item.icon className="h-4 w-4 text-muted-foreground" />
                  <span className="text-[13px] flex-1">{item.label}</span>
                  <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
                </a>
              ) : (
                <Link
                  to={item.to}
                  className="flex items-center gap-3 bg-card rounded-xl p-3.5 shadow-card tap-highlight-none"
                >
                  <item.icon className="h-4 w-4 text-muted-foreground" />
                  <span className="text-[13px] flex-1">{item.label}</span>
                  <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
                </Link>
              )}
            </motion.div>
          ))}
        </div>

        <Button variant="outline" size="sm" className="w-full text-destructive border-destructive/20 hover:bg-destructive/5 text-[11px] h-9">
          <LogOut className="h-3.5 w-3.5 mr-1.5" /> Выйти
        </Button>
      </div>
    </div>
  );
}
