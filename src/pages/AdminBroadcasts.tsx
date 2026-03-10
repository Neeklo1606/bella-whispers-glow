import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Loader2, Image, Video, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getAdminUsers, sendBroadcast, type AdminUser } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function AdminBroadcasts() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [text, setText] = useState("");
  const [mediaType, setMediaType] = useState<"none" | "photo" | "video">("none");
  const [mediaUrl, setMediaUrl] = useState("");
  const [target, setTarget] = useState<"all" | "selected">("all");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const { toast } = useToast();

  useEffect(() => {
    getAdminUsers()
      .then(setUsers)
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  }, []);

  const usersWithTelegram = users.filter((u) => u.telegram_id != null);

  function toggleUser(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function selectAll() {
    if (selectedIds.size === usersWithTelegram.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(usersWithTelegram.map((u) => u.id)));
    }
  }

  async function handleSend() {
    if (!text.trim()) {
      toast({
        title: "Ошибка",
        description: "Введите текст сообщения",
        variant: "destructive",
      });
      return;
    }
    if (target === "selected" && selectedIds.size === 0) {
      toast({
        title: "Ошибка",
        description: "Выберите хотя бы одного пользователя",
        variant: "destructive",
      });
      return;
    }
    if (mediaType !== "none" && !mediaUrl.trim()) {
      toast({
        title: "Ошибка",
        description: "Укажите URL фото или видео",
        variant: "destructive",
      });
      return;
    }

    try {
      setSending(true);
      const res = await sendBroadcast({
        text: text.trim(),
        media_type: mediaType === "none" ? undefined : mediaType,
        media_url: mediaType !== "none" ? mediaUrl.trim() : undefined,
        target,
        user_ids: target === "selected" ? Array.from(selectedIds) : undefined,
      });
      toast({
        title: "Рассылка отправлена",
        description: `Доставлено: ${res.sent} из ${res.total}${res.failed ? `, ошибок: ${res.failed}` : ""}`,
      });
      if (res.sent > 0) {
        setText("");
        setMediaUrl("");
      }
    } catch (e) {
      toast({
        title: "Ошибка рассылки",
        description: e instanceof Error ? e.message : "Не удалось отправить",
        variant: "destructive",
      });
    } finally {
      setSending(false);
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
      <h1 className="text-2xl font-bold">Рассылки</h1>
      <p className="text-muted-foreground text-sm">
        Отправка сообщений, фото или видео пользователям бота в личные сообщения.
      </p>

      <Card>
        <CardHeader>
          <CardTitle>Новая рассылка</CardTitle>
          <CardDescription>
            Текст, опционально фото или видео (URL). Получатели: все или выбранные.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Текст сообщения *</Label>
            <Textarea
              placeholder="Введите текст..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              className="mt-1"
            />
          </div>

          <div>
            <Label>Медиа (опционально)</Label>
            <div className="flex gap-4 mt-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="mediaType"
                  checked={mediaType === "none"}
                  onChange={() => setMediaType("none")}
                />
                <span className="text-sm">Только текст</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="mediaType"
                  checked={mediaType === "photo"}
                  onChange={() => setMediaType("photo")}
                />
                <Image className="h-4 w-4" />
                <span className="text-sm">Фото</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="mediaType"
                  checked={mediaType === "video"}
                  onChange={() => setMediaType("video")}
                />
                <Video className="h-4 w-4" />
                <span className="text-sm">Видео</span>
              </label>
            </div>
            {(mediaType === "photo" || mediaType === "video") && (
              <Input
                placeholder={`URL ${mediaType === "photo" ? "фото" : "видео"}`}
                value={mediaUrl}
                onChange={(e) => setMediaUrl(e.target.value)}
                className="mt-2"
              />
            )}
          </div>

          <div>
            <Label>Получатели</Label>
            <div className="flex gap-4 mt-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="target"
                  checked={target === "all"}
                  onChange={() => setTarget("all")}
                />
                <Users className="h-4 w-4" />
                <span className="text-sm">Всем ({usersWithTelegram.length} с Telegram)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="target"
                  checked={target === "selected"}
                  onChange={() => setTarget("selected")}
                />
                <span className="text-sm">Выбранным</span>
              </label>
            </div>
          </div>

          {target === "selected" && (
            <div className="rounded-lg border p-4 max-h-60 overflow-y-auto">
              <Button variant="outline" size="sm" onClick={selectAll} className="mb-3">
                {selectedIds.size === usersWithTelegram.length ? "Снять выбор" : "Выбрать всех"}
              </Button>
              <div className="space-y-2">
                {usersWithTelegram.length === 0 ? (
                  <p className="text-sm text-muted-foreground">Нет пользователей с Telegram</p>
                ) : (
                  usersWithTelegram.map((u) => (
                    <label key={u.id} className="flex items-center gap-2 cursor-pointer">
                      <Checkbox
                        checked={selectedIds.has(u.id)}
                        onCheckedChange={() => toggleUser(u.id)}
                      />
                      <span className="text-sm">
                        {u.first_name || u.username || u.email || u.id}
                        {u.username && <span className="text-muted-foreground"> @{u.username}</span>}
                      </span>
                    </label>
                  ))
                )}
              </div>
            </div>
          )}

          <Button onClick={handleSend} disabled={sending}>
            {sending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Send className="h-4 w-4 mr-2" />
            )}
            Отправить
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
