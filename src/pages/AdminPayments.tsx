import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Loader2, TrendingUp, CreditCard, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  getAdminPayments,
  getAdminPaymentStats,
  syncAdminPaymentStatus,
  type AdminPayment,
  type AdminPaymentStats,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const statusColors: Record<string, string> = {
  completed: "bg-success/10 text-success",
  pending: "bg-primary/10 text-primary",
  failed: "bg-destructive/10 text-destructive",
  refunded: "bg-muted text-muted-foreground",
};

function formatMoney(amount: number, currency = "RUB"): string {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function AdminPayments() {
  const [payments, setPayments] = useState<AdminPayment[]>([]);
  const [stats, setStats] = useState<AdminPaymentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const { toast } = useToast();

  async function load() {
    setLoading(true);
    try {
      const [list, s] = await Promise.all([getAdminPayments(), getAdminPaymentStats()]);
      const pendingCount = (s?.by_status?.pending ?? 0) || list.filter((p) => p.status === "pending").length;
      if (pendingCount > 0) {
        try {
          await syncAdminPaymentStatus();
        } catch {
          /* ignore sync errors on load */
        }
      }
      const [list2, s2] = await Promise.all([getAdminPayments(), getAdminPaymentStats()]);
      setPayments(list2);
      setStats(s2);
    } catch {
      setPayments([]);
      setStats(null);
      toast({
        title: "Ошибка загрузки",
        description: "Не удалось загрузить платежи",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSyncStatus() {
    setSyncing(true);
    try {
      const res = await syncAdminPaymentStatus();
      load();
      if (res.updated > 0) {
        toast({ title: "Обновлено", description: `Статус обновлён для ${res.updated} платежей` });
      } else if (res.total === 0) {
        toast({ title: "Нет ожидающих", description: "Нет pending-платежей для синхронизации" });
      } else {
        toast({ title: "Без изменений", description: `Проверено ${res.total} платежей, статусы актуальны` });
      }
      if (res.errors?.length) {
        toast({ title: "Ошибки синхронизации", description: res.errors.map((e) => e.error).join("; "), variant: "destructive" });
      }
    } catch (e) {
      toast({ title: "Ошибка", description: e instanceof Error ? e.message : "Не удалось синхронизировать", variant: "destructive" });
    } finally {
      setSyncing(false);
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
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <h1 className="text-2xl font-bold">Статистика оплат</h1>
        <Button variant="outline" onClick={handleSyncStatus} disabled={syncing}>
          {syncing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
          Обновить статусы из YooKassa
        </Button>
      </div>

      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0 }}>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Общая выручка
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatMoney(stats.total_revenue)}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.total_payments} платежей всего
                </p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Сегодня
                </CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatMoney(stats.revenue_today)}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.payments_today} платежей
                </p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  За неделю
                </CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatMoney(stats.revenue_week)}</div>
                <p className="text-xs text-muted-foreground">За последние 7 дней</p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  За месяц
                </CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatMoney(stats.revenue_month)}</div>
                <p className="text-xs text-muted-foreground">За последние 30 дней</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      )}

      {stats && stats.by_status && Object.keys(stats.by_status).length > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardHeader>
              <CardTitle>По статусам</CardTitle>
              <CardDescription>Количество платежей в каждом статусе</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {Object.entries(stats.by_status).map(([status, count]) => (
                  <Badge key={status} variant="secondary" className="text-sm">
                    {status}: {count}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
        <Card>
          <CardHeader>
            <CardTitle>Последние платежи</CardTitle>
            <CardDescription>Список всех платежей (последние сверху)</CardDescription>
          </CardHeader>
          <CardContent>
            {payments.length === 0 ? (
              <p className="text-muted-foreground py-8 text-center">Нет платежей</p>
            ) : (
              <div className="space-y-2">
                {payments.map((p, i) => (
                  <div
                    key={p.id}
                    className="flex flex-wrap items-center gap-3 rounded-lg border p-3"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">
                        {formatMoney(p.amount, p.currency)} — {p.id.slice(0, 8)}…
                        {p.provider_payment_id && (
                          <span className="text-muted-foreground font-normal ml-1">({p.provider_payment_id.slice(0, 8)}…)</span>
                        )}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        User: {p.user_id.slice(0, 8)}… · {new Date(p.created_at).toLocaleString("ru")}
                        {p.paid_at && ` · Оплачен: ${new Date(p.paid_at).toLocaleString("ru")}`}
                      </p>
                    </div>
                    <Badge className={statusColors[p.status] || "bg-muted"}>
                      {p.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
