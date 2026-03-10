import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Loader2, FileText } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { getAdminSettings, updateAdminSetting, type AdminSetting } from "@/lib/api";

const CONTENT_KEYS = [
  { key: "TELEGRAM_BOT_LINK", label: "Ссылка на бота", type: "text" as const, placeholder: "https://t.me/bellahasias_bot" },
  { key: "CONTACT_LINK", label: "Ссылка для связи", type: "text" as const, placeholder: "https://t.me/Bella_hasias" },
  { key: "OFFER_URL", label: "URL оферты", type: "text" as const, placeholder: "https://bellahasias.ru/privacy" },
  { key: "MINIAPP_URL", label: "URL MiniApp", type: "text" as const, placeholder: "https://app.bellahasias.ru" },
  { key: "SUPPORT_USERNAME", label: "Поддержка (username)", type: "text" as const, placeholder: "@bellahasias_bot" },
  { key: "PLAN_TITLE", label: "Заголовок тарифа", type: "text" as const, placeholder: "Подписка на месяц" },
  { key: "PRICE_NOTE", label: "Примечание о цене", type: "text" as const, placeholder: "далее 1500 ₽/мес · отмена в любой момент" },
  { key: "PRICE_AFTER", label: "Цена после первого месяца", type: "text" as const, placeholder: "1500" },
];

function getSettingValue(settings: Record<string, AdminSetting>, key: string): string {
  const s = settings[key];
  if (!s || s.value == null) return "";
  if (typeof s.value === "string") return s.value;
  if (Array.isArray(s.value) || typeof s.value === "object") return JSON.stringify(s.value, null, 2);
  return String(s.value);
}

export default function AdminContent() {
  const [settings, setSettings] = useState<Record<string, AdminSetting>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [values, setValues] = useState<Record<string, string>>({});
  const { toast } = useToast();

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    try {
      setLoading(true);
      const data = await getAdminSettings();
      setSettings(data);
      const initial: Record<string, string> = {};
      ;[...CONTENT_KEYS, { key: "FEATURES" }, { key: "FAQ_ITEMS" }].forEach((def) => {
        const key = typeof def === "object" && "key" in def ? def.key : def;
        initial[key] = getSettingValue(data, key);
      });
      setValues(initial);
    } catch (e) {
      toast({
        title: "Ошибка загрузки",
        description: e instanceof Error ? e.message : "Не удалось загрузить настройки",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  function setValue(key: string, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function saveSetting(key: string) {
    let value: unknown = values[key] ?? "";
    if (key === "FEATURES" || key === "FAQ_ITEMS") {
      try {
        value = JSON.parse(String(value));
      } catch {
        toast({
          title: "Ошибка",
          description: "Некорректный JSON",
          variant: "destructive",
        });
        return;
      }
    }
    try {
      setSaving((prev) => ({ ...prev, [key]: true }));
      const res = await updateAdminSetting(key, value);
      setSettings((prev) => ({ ...prev, [key]: res }));
      toast({ title: "Сохранено", description: `${key} обновлён` });
    } catch (e) {
      toast({
        title: "Ошибка сохранения",
        description: e instanceof Error ? e.message : "Не удалось сохранить",
        variant: "destructive",
      });
    } finally {
      setSaving((prev) => ({ ...prev, [key]: false }));
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Контент MiniApp</h1>
      <p className="text-muted-foreground text-sm">
        Всё содержимое MiniApp загружается из этих настроек. Изменения применяются сразу.
      </p>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Ссылки и тексты
            </CardTitle>
            <CardDescription>
              Ссылки на бота, контакты, оферту. Тексты тарифов и цен.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {CONTENT_KEYS.map((def) => (
              <div key={def.key} className="space-y-2">
                <Label htmlFor={def.key}>{def.label}</Label>
                <div className="flex gap-2">
                  <Input
                    id={def.key}
                    type={def.type}
                    placeholder={def.placeholder}
                    value={values[def.key] ?? ""}
                    onChange={(e) => setValue(def.key, e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => saveSetting(def.key)}
                    disabled={saving[def.key]}
                  >
                    {saving[def.key] ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
        <Card>
          <CardHeader>
            <CardTitle>Преимущества (FEATURES)</CardTitle>
            <CardDescription>Массив строк в формате JSON. Пример: ["Пункт 1", "Пункт 2"]</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Textarea
              id="FEATURES"
              placeholder='["Ежемесячные капсулы","Разборы трендов","Персональные рекомендации","Промокоды и находки"]'
              value={values.FEATURES ?? ""}
              onChange={(e) => setValue("FEATURES", e.target.value)}
              rows={4}
              className="font-mono text-sm"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => saveSetting("FEATURES")}
              disabled={saving.FEATURES}
            >
              {saving.FEATURES ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
              Сохранить
            </Button>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card>
          <CardHeader>
            <CardTitle>FAQ (FAQ_ITEMS)</CardTitle>
            <CardDescription>
              Массив объектов {"{q, a}"} в формате JSON. q — вопрос, a — ответ.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Textarea
              id="FAQ_ITEMS"
              placeholder='[{"q":"Вопрос 1?","a":"Ответ 1"},{"q":"Вопрос 2?","a":"Ответ 2"}]'
              value={values.FAQ_ITEMS ?? ""}
              onChange={(e) => setValue("FAQ_ITEMS", e.target.value)}
              rows={12}
              className="font-mono text-sm"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => saveSetting("FAQ_ITEMS")}
              disabled={saving.FAQ_ITEMS}
            >
              {saving.FAQ_ITEMS ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
              Сохранить
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
