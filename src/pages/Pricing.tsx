import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Check, ArrowLeft, Shield, CreditCard, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const plans = [
  {
    name: "Пробная",
    price: "Бесплатно",
    period: "7 дней",
    features: ["Ограниченный доступ к контенту (10%)", "Просмотр примеров капсул", "Стиль-анкета"],
    cta: "Попробовать",
    variant: "gold-outline" as const,
    badge: null,
  },
  {
    name: "Базовая",
    price: "990₽",
    period: "/месяц",
    features: ["Полная библиотека контента", "Доступ к комьюнити", "Ежемесячные капсулы", "Разборы трендов", "Персональные рекомендации"],
    cta: "Выбрать план",
    variant: "gold" as const,
    badge: "Популярный выбор",
  },
  {
    name: "Премиум",
    price: "1 500₽",
    period: "/месяц",
    features: ["Всё из Базовой", "Персональная консультация (1×/мес)", "Ранний доступ к контенту", "VIP поддержка", "Эксклюзивные материалы"],
    cta: "Выбрать план",
    variant: "gold" as const,
    badge: "Лучшее предложение",
  },
];

const faqItems = [
  { q: "Как отменить подписку?", a: "Вы можете отменить подписку в любой момент в разделе «Управление подпиской». Доступ сохранится до конца оплаченного периода." },
  { q: "Можно ли вернуть деньги?", a: "Мы предоставляем возврат в течение 3 дней после оплаты, если вы не удовлетворены сервисом." },
  { q: "Какие способы оплаты доступны?", a: "Мы принимаем банковские карты (Visa/Mastercard), СБП, Telegram Stars и криптовалюту." },
  { q: "Что если не продлилась подписка?", a: "Свяжитесь с нашей поддержкой, и мы поможем решить вопрос в кратчайшие сроки." },
];

export default function Pricing() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/90 backdrop-blur-md border-b border-border">
        <div className="container flex items-center h-14">
          <Button variant="ghost" size="icon" asChild>
            <Link to="/"><ArrowLeft className="h-5 w-5" /></Link>
          </Button>
          <span className="ml-2 font-semibold">Тарифы</span>
        </div>
      </header>

      <div className="container py-10 md:py-16">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold mb-3">Выберите ваш план</h1>
          <p className="text-muted-foreground">Начните с бесплатного пробного периода</p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-3 max-w-4xl mx-auto">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`relative bg-card rounded-2xl p-6 shadow-card flex flex-col ${i === 1 ? "ring-2 ring-primary" : ""}`}
            >
              {plan.badge && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 gradient-gold text-primary-foreground text-xs font-medium px-3 py-1 rounded-full whitespace-nowrap">
                  {plan.badge}
                </span>
              )}
              <h3 className="text-lg font-semibold mb-1">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mb-4">
                <span className="text-3xl font-bold">{plan.price}</span>
                <span className="text-sm text-muted-foreground">{plan.period}</span>
              </div>
              <ul className="space-y-2.5 mb-6 flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <Check className="h-4 w-4 text-success mt-0.5 shrink-0" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <Button variant={plan.variant} size="lg" className="w-full">
                {plan.cta}
              </Button>
            </motion.div>
          ))}
        </div>

        {/* Payment methods */}
        <div className="flex items-center justify-center gap-4 mt-10 text-muted-foreground">
          <div className="flex items-center gap-1.5 text-xs">
            <Shield className="h-4 w-4" /> Безопасная оплата
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <CreditCard className="h-4 w-4" /> Visa / Mastercard
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <Star className="h-4 w-4" /> Telegram Stars
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-2xl mx-auto mt-16">
          <h2 className="text-2xl font-bold text-center mb-8">Частые вопросы</h2>
          <div className="space-y-3">
            {faqItems.map((item, i) => (
              <div key={i} className="bg-card rounded-xl overflow-hidden shadow-card">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full text-left px-5 py-4 flex items-center justify-between text-sm font-medium tap-highlight-none"
                >
                  {item.q}
                  <span className={`transition-transform duration-200 ${openFaq === i ? "rotate-180" : ""}`}>▾</span>
                </button>
                {openFaq === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    className="px-5 pb-4 text-sm text-muted-foreground"
                  >
                    {item.a}
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
