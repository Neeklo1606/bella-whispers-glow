import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Users, CreditCard, TrendingUp, Percent, Loader2 } from "lucide-react";
import { getAdminDashboard, type AdminDashboard } from "@/lib/api";

const kpiConfig = [
  { key: "users_count" as const, icon: Users, label: "Пользователи" },
  { key: "active_subscriptions" as const, icon: CreditCard, label: "Активных подписок" },
  { key: "revenue_today" as const, icon: TrendingUp, label: "Выручка сегодня" },
  { key: "revenue_total" as const, icon: TrendingUp, label: "Всего выручка" },
  { key: "churn_rate" as const, icon: Percent, label: "Churn Rate" },
];

function formatValue(key: string, val: number): string {
  if (key === "revenue_today" || key === "revenue_total") {
    return `${val.toLocaleString("ru-RU")} ₽`;
  }
  if (key === "churn_rate") {
    return `${val}%`;
  }
  return String(val);
}

export default function AdminDashboard() {
  const [data, setData] = useState<AdminDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminDashboard()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        Не удалось загрузить дашборд
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Дашборд</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {kpiConfig.map(({ key, icon: Icon, label }, i) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="bg-card rounded-xl p-4 shadow-card"
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Icon className="h-4 w-4 text-primary" />
              </div>
            </div>
            <p className="text-2xl font-bold">{formatValue(key, data[key] ?? 0)}</p>
            <p className="text-xs text-muted-foreground">{label}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
