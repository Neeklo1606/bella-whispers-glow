import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Check, Shield, CreditCard } from "lucide-react";
import { Button } from "@/components/ui/button";

const TELEGRAM_LINK = "https://t.me/bellahasias_bot";

const features = [
  "Полная библиотека контента",
  "Доступ к комьюнити",
  "Ежемесячные капсулы",
  "Разборы трендов",
  "Персональные рекомендации",
  "Промокоды и находки",
];

export default function Pricing() {
  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/90 backdrop-blur-md border-b border-border">
        <div className="flex items-center justify-center h-12">
          <span className="text-[10px] tracking-[0.2em] uppercase text-foreground">Тарифы</span>
        </div>
      </header>

      <div className="px-5 py-10">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-[400px] mx-auto"
        >
          {/* Single plan card */}
          <div className="bg-card rounded-2xl p-6 shadow-card text-center mb-6">
            <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-1">
              Подписка на месяц
            </p>
            <div className="flex items-baseline justify-center gap-1 mb-1">
              <span className="text-4xl font-extralight tracking-tight">990 ₽</span>
            </div>
            <p className="text-[10px] text-muted-foreground mb-6">
              отмена в любой момент
            </p>

            <ul className="space-y-3 mb-6 text-left">
              {features.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-[12px]">
                  <Check className="h-3.5 w-3.5 text-foreground/40 mt-0.5 shrink-0" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>

            <a
              href={TELEGRAM_LINK}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity"
            >
              Вступить в чат
            </a>
          </div>

          {/* Payment info */}
          <div className="flex items-center justify-center gap-4 text-muted-foreground">
            <div className="flex items-center gap-1.5 text-[10px]">
              <Shield className="h-3.5 w-3.5" /> Безопасная оплата
            </div>
            <div className="flex items-center gap-1.5 text-[10px]">
              <CreditCard className="h-3.5 w-3.5" /> Visa / Mastercard
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
