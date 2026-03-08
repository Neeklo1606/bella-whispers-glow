import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, Loader2, Ban, Eye } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  getAdminUsers,
  banUser,
  getUserSubscriptions,
  type AdminUser,
  type AdminSubscription,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [subsModal, setSubsModal] = useState<AdminUser | null>(null);
  const [subsList, setSubsList] = useState<AdminSubscription[]>([]);
  const [subsLoading, setSubsLoading] = useState(false);
  const [banningId, setBanningId] = useState<string | null>(null);
  const { toast } = useToast();

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
        <span className="text-sm text-muted-foreground">{users.length} всего</span>
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
            <div className="flex items-center gap-2">
              <Badge variant="outline">{u.role}</Badge>
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
    </div>
  );
}
