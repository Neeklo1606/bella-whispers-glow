import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Check, Shield, CreditCard, Loader2 } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { useMiniappContent } from "@/hooks/useMiniappContent";
import {
  getTelegramInitData,
  authenticateTelegram,
  setUserToken,
  isUserAuthenticated,
  createPayment,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const API_BASE = import.meta.env.VITE_API_URL || "https://app.bellahasias.ru";

export default function Pricing() {
  const [searchParams] = useSearchParams();
  const paid = searchParams.get("paid") === "1";
  const { data: content, isLoading } = useMiniappContent();
  const { toast } = useToast();
  const [authLoading, setAuthLoading] = useState(true);
  const [payingPlanId, setPayingPlanId] = useState<string | null>(null);

  const miniappUrl = content?.miniapp_url || API_BASE;
  const returnUrl = `${miniappUrl.replace(/\/$/, "")}/pricing?paid=1`;
  const telegramLink = content?.telegram_bot_link ?? "https://t.me/bellahasias_bot";
  const planTitle = content?.plan_title ?? "Подписка на месяц";
  const priceNote = content?.price_note ?? "далее 1500 ₽/мес · отмена в любой момент";
  const features = content?.features ?? [
    "Ежемесячные капсулы",
    "Разборы трендов",
    "Персональные рекомендации",
    "Промокоды и находки",
  ];
  const plans = content?.plans ?? [];

  useEffect(() => {
    const initAuth = async () => {
      if (isUserAuthenticated()) {
        setAuthLoading(false);
        return;
      }
      const initData = getTelegramInitData();
      if (initData) {
        try {
          const response = await authenticateTelegram(initData);
          setUserToken(response.access_token);
        } catch (e) {
          console.error("Auth failed:", e);
          toast({
            title: "Ошибка авторизации",
            description: "Откройте страницу через Telegram‑бота",
            variant: "destructive",
          });
        }
      }
      setAuthLoading(false);
    };
    initAuth();
  }, [toast]);

  async function handlePay(planId: string) {
    if (!isUserAuthenticated()) {
      toast({
        title: "Войдите через Telegram",
        description: "Откройте эту страницу через бота",
        variant: "destructive",
      });
      return;
    }
    try {
      setPayingPlanId(planId);
      const res = await createPayment({
        plan_id: planId,
        return_url: returnUrl,
      });
      if (res.payment_url) {
        window.location.href = res.payment_url;
      } else {
        throw new Error("Не получена ссылка на оплату");
      }
    } catch (e) {
      setPayingPlanId(null);
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось создать платёж",
        variant: "destructive",
      });
    }
  }

  if (paid) {
    return (
      <div className="min-h-screen bg-background pb-20 flex flex-col items-center justify-center px-5">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-[400px] w-full text-center"
        >
          <div className="bg-success/10 text-success rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <Check className="h-8 w-8" />
          </div>
          <h1 className="text-xl font-bold mb-2">Оплата прошла успешно</h1>
          <p className="text-muted-foreground text-sm mb-6">
            Подписка активирована. Вернитесь в бот для доступа к контенту.
          </p>
          <a
            href={telegramLink}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity"
          >
            Вернуться в бот
          </a>
        </motion.div>
      </div>
    );
  }

  const defaultPlan = plans[0];
  const price = defaultPlan
    ? (defaultPlan.first_month_price ?? defaultPlan.price ?? 990)
    : 990;

  return (
    <div className="min-h-screen bg-background pb-20">
      <header className="sticky top-0 z-50 bg-background/90 backdrop-blur-md border-b border-border">
        <div className="flex items-center justify-center h-12">
          <span className="text-[10px] tracking-[0.2em] uppercase text-foreground">
            Тарифы
          </span>
        </div>
      </header>

      <div className="px-5 py-10">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-[400px] mx-auto"
        >
          {plans.length === 0 && !isLoading ? (
            <div className="bg-card rounded-2xl p-6 text-center text-muted-foreground">
              Тарифы временно недоступны
            </div>
          ) : (
            <>
              <div className="bg-card rounded-2xl p-6 shadow-card text-center mb-6">
                <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-1">
                  {planTitle}
                </p>
                <div className="flex items-baseline justify-center gap-1 mb-1">
                  <span className="text-5xl font-display font-bold tracking-tight">
                    {isLoading ? "..." : `${price} ₽`}
                  </span>
                  <span className="text-lg font-normal text-muted-foreground">
                    — первый месяц
                  </span>
                </div>
                <p className="text-[10px] text-muted-foreground mb-1">{priceNote}</p>
                <p className="text-[10px] text-muted-foreground/70 mb-6">
                  Доступ к чату через Telegram‑бота, сразу после оплаты
                </p>

                <ul className="space-y-3 mb-6 text-left">
                  {features.map((f: string) => (
                    <li key={f} className="flex items-start gap-2.5 text-[12px]">
                      <Check className="h-3.5 w-3.5 text-foreground/40 mt-0.5 shrink-0" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>

                {defaultPlan && (
                  <button
                    onClick={() => handlePay(defaultPlan.id)}
                    disabled={authLoading || !!payingPlanId}
                    className="block w-full py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {payingPlanId ? (
                      <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                    ) : (
                      "Оплатить (YooKassa)"
                    )}
                  </button>
                )}
              </div>

              <div className="flex justify-center gap-4 text-muted-foreground">
                <div className="flex items-center gap-1.5 text-[10px]">
                  <Shield className="h-3.5 w-3.5" /> Безопасная оплата
                </div>
                <div className="flex items-center gap-1.5 text-[10px]">
                  <CreditCard className="h-3.5 w-3.5" /> Visa / Mastercard / МИР
                </div>
              </div>
            </>
          )}
        </motion.div>
      </div>
    </div>
  );
}
