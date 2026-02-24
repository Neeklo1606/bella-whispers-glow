import { useState } from "react";
import { motion } from "framer-motion";
import { Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";

export default function Consent() {
  const [dataConsent, setDataConsent] = useState(false);
  const [termsConsent, setTermsConsent] = useState(false);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md bg-card rounded-2xl p-6 shadow-elevated"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
            <Shield className="h-5 w-5 text-foreground" />
          </div>
          <h1 className="text-xl font-bold">Защита персональных данных</h1>
        </div>

        <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
          Для использования сервиса нам необходимо ваше согласие на обработку данных в соответствии с действующим законодательством.
        </p>

        <div className="space-y-4 mb-6">
          <label className="flex items-start gap-3 cursor-pointer tap-highlight-none">
            <Checkbox checked={dataConsent} onCheckedChange={(v) => setDataConsent(v === true)} className="mt-0.5" />
            <span className="text-sm">
              Я согласен(а) с обработкой персональных данных согласно{" "}
              <a href="/privacy" className="text-primary underline">Политике конфиденциальности</a>
            </span>
          </label>
          <label className="flex items-start gap-3 cursor-pointer tap-highlight-none">
            <Checkbox checked={termsConsent} onCheckedChange={(v) => setTermsConsent(v === true)} className="mt-0.5" />
            <span className="text-sm">
              Я принимаю{" "}
              <a href="/terms" className="text-primary underline">Условия использования</a>
            </span>
          </label>
        </div>

        <Button
          variant="gold"
          size="lg"
          className="w-full"
          disabled={!dataConsent || !termsConsent}
        >
          Принять и продолжить
        </Button>

        <p className="mt-4 text-[11px] text-muted-foreground text-center">
          Мы ценим вашу конфиденциальность и обрабатываем данные согласно GDPR
        </p>
      </motion.div>
    </div>
  );
}
