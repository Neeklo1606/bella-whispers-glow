import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Check, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusIndicator } from "@/components/StatusIndicator";

const payments = [
  { date: "15 фев 2026", amount: "990₽", status: "Оплачен" },
  { date: "15 янв 2026", amount: "990₽", status: "Оплачен" },
  { date: "15 дек 2025", amount: "990₽", status: "Оплачен" },
];

export default function SubscriptionManagement() {
  return (
    <div className="container py-4 space-y-6">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/dashboard"><ArrowLeft className="h-5 w-5" /></Link>
        </Button>
        <h1 className="text-xl font-bold">Подписка</h1>
      </div>

      {/* Current plan */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-card rounded-2xl p-5 shadow-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-muted-foreground">Текущий план</p>
            <p className="text-lg font-bold">Премиум</p>
          </div>
          <StatusIndicator status="active" />
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-muted-foreground">Стоимость</span><span className="font-medium">1 500₽/мес</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Следующее списание</span><span className="font-medium">15 мар 2026</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Способ оплаты</span><span className="font-medium">•••• 4242</span></div>
        </div>
        <div className="flex gap-2 mt-4">
          <Button variant="outline" size="sm" className="flex-1">Изменить план</Button>
          <Button variant="ghost" size="sm" className="text-destructive">Отменить</Button>
        </div>
      </motion.div>

      {/* Billing history */}
      <div>
        <h2 className="text-base font-semibold mb-3">История платежей</h2>
        <div className="space-y-2">
          {payments.map((p, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}
              className="flex items-center justify-between bg-card rounded-xl p-4 shadow-card"
            >
              <div>
                <p className="text-sm font-medium">{p.amount}</p>
                <p className="text-xs text-muted-foreground">{p.date}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 text-xs text-success"><Check className="h-3 w-3" />{p.status}</span>
                <Button variant="ghost" size="icon" className="h-8 w-8"><Download className="h-3.5 w-3.5" /></Button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
