import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Loader2, Plus, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  getAdminSubscriptions,
  extendSubscription,
  revokeSubscription,
  type AdminSubscription,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const statusColors: Record<string, string> = {
  active: "bg-success/10 text-success",
  expired: "bg-destructive/10 text-destructive",
  cancelled: "bg-muted text-muted-foreground",
  pending: "bg-primary/10 text-primary",
};

export default function AdminSubscriptions() {
  const [subscriptions, setSubscriptions] = useState<AdminSubscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [extendModal, setExtendModal] = useState<AdminSubscription | null>(null);
  const [extendDays, setExtendDays] = useState(30);
  const [extending, setExtending] = useState(false);
  const [revokingId, setRevokingId] = useState<string | null>(null);
  const { toast } = useToast();

  function load() {
    setLoading(true);
    getAdminSubscriptions()
      .then(setSubscriptions)
      .catch(() => setSubscriptions([]))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  async function handleExtend() {
    if (!extendModal || extendDays < 1) return;
    try {
      setExtending(true);
      await extendSubscription(extendModal.id, extendDays);
      setExtendModal(null);
      load();
      toast({ title: "Подписка продлена" });
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось продлить",
        variant: "destructive",
      });
    } finally {
      setExtending(false);
    }
  }

  async function handleRevoke(sub: AdminSubscription) {
    try {
      setRevokingId(sub.id);
      await revokeSubscription(sub.id);
      load();
      toast({ title: "Подписка отменена" });
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось отменить",
        variant: "destructive",
      });
    } finally {
      setRevokingId(null);
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
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Подписки</h1>
        <span className="text-sm text-muted-foreground">{subscriptions.length} всего</span>
      </div>

      <div className="space-y-2">
        {subscriptions.map((s, i) => (
          <motion.div
            key={s.id}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: i * 0.03 }}
            className="flex flex-wrap items-center gap-3 bg-card rounded-xl p-4 shadow-card"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">User: {s.user_id.slice(0, 8)}…</p>
              <p className="text-xs text-muted-foreground">
                до {s.end_date ? new Date(s.end_date).toLocaleDateString("ru") : "—"}
              </p>
            </div>
            <Badge className={statusColors[s.status] || "bg-muted"}>{s.status}</Badge>
            <div className="flex gap-2">
              {s.status === "active" && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setExtendModal(s);
                      setExtendDays(30);
                    }}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Продлить
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleRevoke(s)}
                    disabled={revokingId === s.id}
                  >
                    {revokingId === s.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <XCircle className="h-4 w-4 mr-1" />
                        Отменить
                      </>
                    )}
                  </Button>
                </>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      <Dialog open={!!extendModal} onOpenChange={() => setExtendModal(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Продлить подписку</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Количество дней</Label>
              <Input
                type="number"
                min={1}
                value={extendDays}
                onChange={(e) => setExtendDays(Number(e.target.value) || 30)}
              />
            </div>
            <Button onClick={handleExtend} disabled={extending}>
              {extending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Продлить
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
