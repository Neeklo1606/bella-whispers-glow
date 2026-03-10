import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Loader2, Plus, Pencil, Trash2, ToggleLeft, ToggleRight } from "lucide-react";
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
  getAdminPlans,
  createAdminPlan,
  updateAdminPlan,
  deleteAdminPlan,
  type AdminPlan,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function AdminPlans() {
  const [plans, setPlans] = useState<AdminPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState<AdminPlan | null>(null);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    description: "",
    price: 990,
    first_month_price: 990,
    duration_days: 30,
    is_active: true,
  });
  const { toast } = useToast();

  function load() {
    setLoading(true);
    getAdminPlans()
      .then(setPlans)
      .catch(() => setPlans([]))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  function openCreate() {
    setEditingPlan(null);
    setForm({
      name: "1 месяц",
      description: "Доступ в закрытый канал на 30 дней",
      price: 1500,
      first_month_price: 990,
      duration_days: 30,
      is_active: true,
    });
    setModalOpen(true);
  }

  function openEdit(plan: AdminPlan) {
    setEditingPlan(plan);
    setForm({
      name: plan.name,
      description: plan.description || "",
      price: plan.price,
      first_month_price: plan.first_month_price ?? plan.price,
      duration_days: plan.duration_days,
      is_active: plan.is_active,
    });
    setModalOpen(true);
  }

  async function handleSave() {
    try {
      setSaving(true);
      if (editingPlan) {
        await updateAdminPlan(editingPlan.id, form);
        toast({ title: "Тариф обновлён" });
      } else {
        await createAdminPlan(form);
        toast({ title: "Тариф создан" });
      }
      setModalOpen(false);
      load();
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось сохранить",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleActive(plan: AdminPlan) {
    try {
      await updateAdminPlan(plan.id, { is_active: !plan.is_active });
      toast({ title: plan.is_active ? "Тариф отключён" : "Тариф включён" });
      load();
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось изменить",
        variant: "destructive",
      });
    }
  }

  async function handleDelete(plan: AdminPlan) {
    if (!confirm(`Удалить тариф «${plan.name}»?`)) return;
    try {
      setDeletingId(plan.id);
      await deleteAdminPlan(plan.id);
      toast({ title: "Тариф удалён" });
      load();
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось удалить",
        variant: "destructive",
      });
    } finally {
      setDeletingId(null);
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
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Тарифы</h1>
        <Button onClick={openCreate}>
          <Plus className="h-4 w-4 mr-2" />
          Добавить тариф
        </Button>
      </div>

      {plans.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center text-muted-foreground">
          Нет тарифов. Создайте тариф — он появится в боте и Mini App.
        </div>
      ) : (
        <div className="space-y-3">
          {plans.map((plan) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between rounded-xl border border-border bg-card p-4"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{plan.name}</span>
                  {!plan.is_active && <Badge variant="secondary">Отключён</Badge>}
                </div>
                <p className="text-sm text-muted-foreground mt-0.5">
                  {plan.first_month_price ?? plan.price} ₽ первый месяц · далее {plan.price} ₽ · {plan.duration_days} дн.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleToggleActive(plan)}
                  title={plan.is_active ? "Отключить" : "Включить"}
                >
                  {plan.is_active ? (
                    <ToggleRight className="h-5 w-5 text-primary" />
                  ) : (
                    <ToggleLeft className="h-5 w-5 text-muted-foreground" />
                  )}
                </Button>
                <Button variant="outline" size="icon" onClick={() => openEdit(plan)}>
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="text-destructive"
                  onClick={() => handleDelete(plan)}
                  disabled={deletingId === plan.id}
                >
                  {deletingId === plan.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingPlan ? "Редактировать тариф" : "Новый тариф"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Название</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="1 месяц"
              />
            </div>
            <div>
              <Label>Описание</Label>
              <Input
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="Доступ в закрытый канал"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Цена первый месяц (₽)</Label>
                <Input
                  type="number"
                  value={form.first_month_price}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, first_month_price: Number(e.target.value) || 0 }))
                  }
                />
              </div>
              <div>
                <Label>Цена далее (₽)</Label>
                <Input
                  type="number"
                  value={form.price}
                  onChange={(e) => setForm((f) => ({ ...f, price: Number(e.target.value) || 0 }))}
                />
              </div>
            </div>
            <div>
              <Label>Дней действия</Label>
              <Input
                type="number"
                value={form.duration_days}
                onChange={(e) =>
                  setForm((f) => ({ ...f, duration_days: Number(e.target.value) || 30 }))
                }
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={form.is_active}
                onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
              />
              <Label htmlFor="is_active">Активен (отображается в боте)</Label>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Отмена
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Сохранить
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
