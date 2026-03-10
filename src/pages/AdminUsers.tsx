import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, Loader2, Ban, Eye, Plus, Trash2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  getAdminUsers,
  banUser,
  getUserSubscriptions,
  createAdminUser,
  deleteAdminUser,
  updateAdminUser,
  type AdminUser,
  type AdminSubscription,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const ADMIN_ROLES = [
  { value: "admin", label: "Админ" },
  { value: "super_admin", label: "Супер-админ" },
] as const;

export default function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [subsModal, setSubsModal] = useState<AdminUser | null>(null);
  const [subsList, setSubsList] = useState<AdminSubscription[]>([]);
  const [subsLoading, setSubsLoading] = useState(false);
  const [banningId, setBanningId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [createModal, setCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createForm, setCreateForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    role: "admin" as "admin" | "super_admin",
  });
  const [roleUpdatingId, setRoleUpdatingId] = useState<string | null>(null);
  const { toast } = useToast();

  function refresh() {
    getAdminUsers()
      .then(setUsers)
      .catch(() => setUsers([]));
  }

  useEffect(() => {
    getAdminUsers()
      .then(setUsers)
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  }, []);

  async function handleBan(user: AdminUser) {
    try {
      setBanningId(user.id);
      await banUser(user.id);
      setUsers((prev) => prev.filter((u) => u.id !== user.id));
      toast({ title: "Пользователь заблокирован" });
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось заблокировать",
        variant: "destructive",
      });
    } finally {
      setBanningId(null);
    }
  }

  async function handleCreate() {
    if (!createForm.email || !createForm.password) {
      toast({ title: "Укажите email и пароль", variant: "destructive" });
      return;
    }
    if (createForm.password.length < 6) {
      toast({ title: "Пароль минимум 6 символов", variant: "destructive" });
      return;
    }
    setCreating(true);
    try {
      await createAdminUser({
        email: createForm.email,
        password: createForm.password,
        first_name: createForm.first_name || undefined,
        last_name: createForm.last_name || undefined,
        role: createForm.role,
      });
      toast({ title: "Администратор создан" });
      setCreateModal(false);
      setCreateForm({ email: "", password: "", first_name: "", last_name: "", role: "admin" });
      refresh();
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось создать",
        variant: "destructive",
      });
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(user: AdminUser) {
    setDeletingId(user.id);
    try {
      await deleteAdminUser(user.id);
      setUsers((prev) => prev.filter((u) => u.id !== user.id));
      toast({ title: "Пользователь удалён" });
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

  async function handleRoleChange(user: AdminUser, newRole: string) {
    if (newRole === user.role) return;
    setRoleUpdatingId(user.id);
    try {
      const updated = await updateAdminUser(user.id, { role: newRole as "user" | "admin" | "super_admin" });
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, role: updated.role } : u))
      );
      toast({ title: "Роль обновлена" });
    } catch (e) {
      toast({
        title: "Ошибка",
        description: e instanceof Error ? e.message : "Не удалось обновить роль",
        variant: "destructive",
      });
    } finally {
      setRoleUpdatingId(null);
    }
  }

  async function handleViewSubs(user: AdminUser) {
    setSubsModal(user);
    setSubsList([]);
    setSubsLoading(true);
    try {
      const list = await getUserSubscriptions(user.id);
      setSubsList(list);
    } catch {
      setSubsList([]);
    } finally {
      setSubsLoading(false);
    }
  }

  const filtered = users.filter(
    (u) =>
      !search ||
      (u.username || "").toLowerCase().includes(search.toLowerCase()) ||
      (u.first_name || "").toLowerCase().includes(search.toLowerCase()) ||
      (u.email || "").toLowerCase().includes(search.toLowerCase()) ||
      (u.id || "").toLowerCase().includes(search.toLowerCase())
  );

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
        <h1 className="text-2xl font-bold">Пользователи</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">{users.length} всего</span>
          <Button onClick={() => setCreateModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Создать администратора
          </Button>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Поиск по имени, email, username..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        {filtered.map((u, i) => (
          <motion.div
            key={u.id}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: i * 0.03 }}
            className="flex items-center gap-3 bg-card rounded-xl p-4 shadow-card"
          >
            <Avatar className="h-10 w-10">
              <AvatarFallback className="bg-secondary text-foreground text-sm font-medium">
                {(u.first_name || u.username || "?").charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {u.first_name || u.username || u.email || u.id.slice(0, 8)}
              </p>
              <p className="text-xs text-muted-foreground">
                {u.username ? `@${u.username}` : u.email || u.id}
              </p>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              {u.is_admin ? (
                <Select
                  value={u.role}
                  onValueChange={(v) => handleRoleChange(u, v)}
                  disabled={roleUpdatingId === u.id}
                >
                  <SelectTrigger className="w-[130px] h-8">
                    <SelectValue />
                    {roleUpdatingId === u.id && (
                      <Loader2 className="h-3 w-3 animate-spin ml-1" />
                    )}
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Админ</SelectItem>
                    <SelectItem value="super_admin">Супер-админ</SelectItem>
                    <SelectItem value="user">Пользователь</SelectItem>
                  </SelectContent>
                </Select>
              ) : (
                <Badge variant="outline">{u.role}</Badge>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleViewSubs(u)}
                disabled={subsLoading}
              >
                <Eye className="h-4 w-4 mr-1" />
                Подписки
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => handleBan(u)}
                disabled={banningId === u.id}
              >
                {banningId === u.id ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Ban className="h-4 w-4 mr-1" />
                    Бан
                  </>
                )}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDelete(u)}
                disabled={deletingId === u.id}
                className="text-destructive hover:text-destructive"
              >
                {deletingId === u.id ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" title="Удалить" />
                )}
              </Button>
            </div>
          </motion.div>
        ))}
      </div>

      <Dialog open={!!subsModal} onOpenChange={() => setSubsModal(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Подписки: {subsModal?.first_name || subsModal?.username || subsModal?.email || subsModal?.id}
            </DialogTitle>
          </DialogHeader>
          {subsLoading ? (
            <Loader2 className="h-6 w-6 animate-spin mx-auto" />
          ) : subsList.length === 0 ? (
            <p className="text-muted-foreground">Нет подписок</p>
          ) : (
            <ul className="space-y-2">
              {subsList.map((s) => (
                <li key={s.id} className="flex justify-between text-sm">
                  <span>{s.status}</span>
                  <span className="text-muted-foreground">
                    до {s.end_date ? new Date(s.end_date).toLocaleDateString("ru") : "—"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={createModal} onOpenChange={setCreateModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Создать администратора</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Email *</Label>
              <Input
                type="email"
                value={createForm.email}
                onChange={(e) => setCreateForm((f) => ({ ...f, email: e.target.value }))}
                placeholder="admin@example.com"
              />
            </div>
            <div>
              <Label>Пароль * (мин. 6 символов)</Label>
              <Input
                type="password"
                value={createForm.password}
                onChange={(e) => setCreateForm((f) => ({ ...f, password: e.target.value }))}
                placeholder="••••••••"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Имя</Label>
                <Input
                  value={createForm.first_name}
                  onChange={(e) => setCreateForm((f) => ({ ...f, first_name: e.target.value }))}
                  placeholder="Иван"
                />
              </div>
              <div>
                <Label>Фамилия</Label>
                <Input
                  value={createForm.last_name}
                  onChange={(e) => setCreateForm((f) => ({ ...f, last_name: e.target.value }))}
                  placeholder="Иванов"
                />
              </div>
            </div>
            <div>
              <Label>Роль</Label>
              <Select
                value={createForm.role}
                onValueChange={(v) => setCreateForm((f) => ({ ...f, role: v as "admin" | "super_admin" }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ADMIN_ROLES.map((r) => (
                    <SelectItem key={r.value} value={r.value}>
                      {r.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setCreateModal(false)}>
                Отмена
              </Button>
              <Button onClick={handleCreate} disabled={creating}>
                {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : "Создать"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
