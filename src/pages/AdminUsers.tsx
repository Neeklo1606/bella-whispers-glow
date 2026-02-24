import { motion } from "framer-motion";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const users = [
  { name: "Анна Козлова", tg: "@anna_k", plan: "Premium", status: "active", joined: "12.01.2026" },
  { name: "Мария Дмитриева", tg: "@maria_d", plan: "Basic", status: "active", joined: "05.12.2025" },
  { name: "Елена Смирнова", tg: "@elena_s", plan: "Trial", status: "trial", joined: "20.02.2026" },
  { name: "Ольга Петрова", tg: "@olga_p", plan: "Basic", status: "expired", joined: "10.11.2025" },
  { name: "Наталья Иванова", tg: "@natasha_i", plan: "Premium", status: "active", joined: "01.02.2026" },
];

const statusMap: Record<string, string> = {
  active: "bg-success/10 text-success",
  trial: "bg-primary/10 text-primary",
  expired: "bg-destructive/10 text-destructive",
};

export default function AdminUsers() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Пользователи</h1>
        <span className="text-sm text-muted-foreground">{users.length} всего</span>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Поиск по имени или ID..." className="pl-10" />
      </div>

      <div className="space-y-2">
        {users.map((u, i) => (
          <motion.div
            key={u.tg}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}
            className="flex items-center gap-3 bg-card rounded-xl p-4 shadow-card"
          >
            <Avatar className="h-10 w-10">
              <AvatarFallback className="bg-secondary text-foreground text-sm font-medium">
                {u.name.split(" ").map(n => n[0]).join("")}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{u.name}</p>
              <p className="text-xs text-muted-foreground">{u.tg}</p>
            </div>
            <div className="text-right">
              <Badge variant="outline" className={statusMap[u.status]}>{u.plan}</Badge>
              <p className="text-[10px] text-muted-foreground mt-0.5">{u.joined}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
