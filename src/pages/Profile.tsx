import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { User, Palette, Bell, CreditCard, FileText, Shield, HelpCircle, LogOut, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const sections = [
  { icon: Palette, label: "Стиль-профиль", desc: "Цветотип, фигура, бюджет", to: "/dashboard/onboarding" },
  { icon: Bell, label: "Уведомления", desc: "Настроить оповещения", to: "#" },
  { icon: CreditCard, label: "Управлять подпиской", desc: "Базовая • 990₽/мес", to: "/dashboard/subscription" },
  { icon: Shield, label: "Конфиденциальность", desc: "Политика обработки данных", to: "/privacy" },
  { icon: FileText, label: "Условия использования", desc: "Правила сервиса", to: "/terms" },
  { icon: HelpCircle, label: "Поддержка", desc: "Связаться с нами", to: "#" },
];

export default function Profile() {
  return (
    <div className="container py-6 space-y-6">
      {/* User info */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4">
        <Avatar className="h-16 w-16">
          <AvatarFallback className="gradient-gold text-primary-foreground text-xl font-bold">
            <User className="h-7 w-7" />
          </AvatarFallback>
        </Avatar>
        <div>
          <h1 className="text-xl font-bold">Пользователь</h1>
          <p className="text-sm text-muted-foreground">@username</p>
        </div>
      </motion.div>

      {/* Menu */}
      <div className="space-y-2">
        {sections.map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
            <Link
              to={s.to}
              className="flex items-center gap-3 bg-card rounded-xl p-4 shadow-card hover:shadow-elevated transition-shadow tap-highlight-none"
            >
              <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center">
                <s.icon className="h-4.5 w-4.5 text-muted-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{s.label}</p>
                <p className="text-xs text-muted-foreground truncate">{s.desc}</p>
              </div>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </Link>
          </motion.div>
        ))}
      </div>

      <Button variant="outline" className="w-full text-destructive border-destructive/20 hover:bg-destructive/5">
        <LogOut className="h-4 w-4 mr-2" /> Выйти
      </Button>
    </div>
  );
}
