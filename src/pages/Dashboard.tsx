import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { BookOpen, Heart, Target, ChevronRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusIndicator } from "@/components/StatusIndicator";

const stats = [
  { icon: BookOpen, label: "Просмотрено", value: "24 образа" },
  { icon: Heart, label: "Избранное", value: "12 капсул" },
  { icon: Target, label: "Выполнено", value: "3 челленджа" },
];

const recommendations = [
  { title: "Капсула: Деловой стиль", tag: "Персональная рекомендация" },
  { title: "Тренды весны 2026", tag: "Новое" },
  { title: "Базовая обувь на каждый день", tag: "Для вас" },
];

export default function Dashboard() {
  return (
    <div className="container py-6 space-y-6">
      {/* Greeting */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold">Привет! 👋</h1>
        <p className="text-sm text-muted-foreground">Ваш стильный день начинается здесь</p>
      </motion.div>

      {/* Subscription Card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card rounded-2xl p-5 shadow-card"
      >
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-xs text-muted-foreground">Подписка</p>
            <p className="font-semibold">Премиум</p>
          </div>
          <StatusIndicator status="active" />
        </div>
        <div className="mb-3">
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>Следующее списание</span>
            <span>15 марта 2026</span>
          </div>
          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <div className="h-full gradient-gold rounded-full" style={{ width: "65%" }} />
          </div>
        </div>
        <Button variant="outline" size="sm" className="w-full" asChild>
          <Link to="/dashboard/subscription">Управлять подпиской <ChevronRight className="h-4 w-4" /></Link>
        </Button>
      </motion.div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.05 }}
            className="bg-card rounded-xl p-3 shadow-card text-center"
          >
            <s.icon className="h-5 w-5 text-primary mx-auto mb-1" />
            <p className="text-sm font-semibold">{s.value}</p>
            <p className="text-[11px] text-muted-foreground">{s.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Recommendations */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold flex items-center gap-1.5">
            <Sparkles className="h-4 w-4 text-primary" /> Для вас сегодня
          </h2>
        </div>
        <div className="space-y-3">
          {recommendations.map((r, i) => (
            <motion.div
              key={r.title}
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + i * 0.05 }}
            >
              <Link to="/dashboard/feed" className="flex items-center gap-4 bg-card rounded-xl p-4 shadow-card hover:shadow-elevated transition-shadow tap-highlight-none">
                <div className="w-14 h-14 rounded-lg bg-secondary shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{r.title}</p>
                  <span className="text-[11px] text-primary font-medium">{r.tag}</span>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Upsell */}
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="gradient-gold rounded-2xl p-5 text-primary-foreground"
      >
        <h3 className="font-semibold mb-1">Не заполнили стиль-анкету?</h3>
        <p className="text-sm opacity-90 mb-3">Получите персональные рекомендации под ваш стиль</p>
        <Button variant="secondary" size="sm">Пройти анкету</Button>
      </motion.div>
    </div>
  );
}
