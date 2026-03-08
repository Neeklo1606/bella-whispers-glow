import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Loader2, MessageCircle, CreditCard } from "lucide-react";
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
import { useToast } from "@/hooks/use-toast";
import {
  getAdminSettings,
  updateAdminSetting,
  testTelegram,
  testPayment,
  type AdminSetting,
} from "@/lib/api";

const EDITABLE_KEYS = [
  { key: "TELEGRAM_BOT_TOKEN", label: "Bot Token", type: "password" as const, placeholder: "123456:ABC-DEF..." },
  { key: "TELEGRAM_CHANNEL_ID", label: "Channel ID", type: "text" as const, placeholder: "@channel or -1001234567890" },
  { key: "BOT_API_SECRET", label: "Bot API Secret", type: "password" as const, placeholder: "Optional" },
  { key: "YOOKASSA_SHOP_ID", label: "Shop ID", type: "text" as const, placeholder: "123456" },
  { key: "YOOKASSA_SECRET_KEY", label: "Secret Key", type: "password" as const, placeholder: "..." },
];

function getSettingValue(settings: Record<string, AdminSetting>, key: string): string {
  const s = settings[key];
  if (!s || s.value == null) return "";
  return String(s.value);
}

export default function AdminSettings() {
  const [settings, setSettings] = useState<Record<string, AdminSetting>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [values, setValues] = useState<Record<string, string>>({});
  const [testTgLoading, setTestTgLoading] = useState(false);
  const [testPayLoading, setTestPayLoading] = useState(false);
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
      EDITABLE_KEYS.forEach((def) => {
        initial[def.key] = getSettingValue(data, def.key);
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
    try {
      setSaving((prev) => ({ ...prev, [key]: true }));
      const res = await updateAdminSetting(key, values[key] ?? "");
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

  async function handleTestTelegram() {
    try {
      setTestTgLoading(true);
      const res = await testTelegram();
      if (res.ok) {
        toast({
          title: "Telegram: OK",
          description: res.channel ? "Bot и канал проверены" : "Bot проверен (канал не задан)",
        });
      } else {
        toast({
          title: "Telegram: ошибка",
          description: res.error || res.channel_error || "Неизвестная ошибка",
          variant: "destructive",
        });
      }
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось проверить",
        variant: "destructive",
      });
    } finally {
      setTestTgLoading(false);
    }
  }

  async function handleTestPayment() {
    try {
      setTestPayLoading(true);
      const res = await testPayment();
      if (res.ok) {
        toast({ title: "YooKassa: OK", description: res.message || "Конфигурация проверена" });
      } else {
        toast({
          title: "YooKassa: ошибка",
          description: res.error || "Конфигурация некорректна",
          variant: "destructive",
        });
      }
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось проверить",
        variant: "destructive",
      });
    } finally {
      setTestPayLoading(false);
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
      <h1 className="text-2xl font-bold">Настройки</h1>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader>
            <CardTitle>Параметры</CardTitle>
            <CardDescription>Редактируемые настройки (TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, BOT_API_SECRET, YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {EDITABLE_KEYS.map((def) => (
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
            <CardTitle>Проверка подключений</CardTitle>
            <CardDescription>Проверить Telegram бот и YooKassa</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-4">
            <Button
              variant="outline"
              onClick={handleTestTelegram}
              disabled={testTgLoading}
            >
              {testTgLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <MessageCircle className="h-4 w-4 mr-2" />
              )}
              Test Telegram Bot
            </Button>
            <Button
              variant="outline"
              onClick={handleTestPayment}
              disabled={testPayLoading}
            >
              {testPayLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <CreditCard className="h-4 w-4 mr-2" />
              )}
              Test YooKassa
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
