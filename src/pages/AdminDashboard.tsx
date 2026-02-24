import { motion } from "framer-motion";
import { Users, CreditCard, TrendingUp, Percent } from "lucide-react";

const kpis = [
  { icon: Users, label: "Пользователи", value: "547", change: "+12 за неделю", up: true },
  { icon: CreditCard, label: "Активных подписок", value: "423", change: "77% retention", up: true },
  { icon: TrendingUp, label: "MRR", value: "520 350₽", change: "+5.2%", up: true },
  { icon: Percent, label: "Churn Rate", value: "8.3%", change: "−1.2%", up: false },
];

const activity = [
  { text: "Новый пользователь: @anna_style", time: "2 мин назад" },
  { text: "Оплата подписки: Premium — 1500₽", time: "15 мин назад" },
  { text: "Создан пост: «Капсула весна 2026»", time: "1 час назад" },
  { text: "Отменена подписка: user_382", time: "3 часа назад" },
  { text: "Новый пользователь: @marina_k", time: "5 часов назад" },
];

export default function AdminDashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Дашборд</h1>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, i) => (
          <motion.div
            key={kpi.label}
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="bg-card rounded-xl p-4 shadow-card"
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <kpi.icon className="h-4 w-4 text-primary" />
              </div>
            </div>
            <p className="text-2xl font-bold">{kpi.value}</p>
            <p className="text-xs text-muted-foreground">{kpi.label}</p>
            <p className={`text-xs font-medium mt-1 ${kpi.up ? "text-success" : "text-destructive"}`}>{kpi.change}</p>
          </motion.div>
        ))}
      </div>

      {/* Revenue chart placeholder */}
      <div className="bg-card rounded-xl p-5 shadow-card">
        <h2 className="text-base font-semibold mb-4">Выручка (6 месяцев)</h2>
        <div className="h-48 flex items-end gap-2">
          {[65, 72, 58, 80, 88, 95].map((h, i) => (
            <motion.div
              key={i}
              initial={{ height: 0 }} animate={{ height: `${h}%` }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              className="flex-1 bg-primary rounded-t-md"
            />
          ))}
        </div>
        <div className="flex justify-between mt-2 text-[10px] text-muted-foreground">
          {["Сен", "Окт", "Ноя", "Дек", "Янв", "Фев"].map(m => <span key={m}>{m}</span>)}
        </div>
      </div>

      {/* Activity */}
      <div className="bg-card rounded-xl p-5 shadow-card">
        <h2 className="text-base font-semibold mb-3">Последняя активность</h2>
        <div className="space-y-3">
          {activity.map((a, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              transition={{ delay: 0.3 + i * 0.05 }}
              className="flex items-center justify-between text-sm"
            >
              <span>{a.text}</span>
              <span className="text-xs text-muted-foreground whitespace-nowrap ml-3">{a.time}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
