import { useState } from "react";
import { motion } from "framer-motion";
import { Heart } from "lucide-react";
import { cn } from "@/lib/utils";

const categories = ["Все", "Капсулы", "Обувь/Сумки", "Примерки", "Тренды"];

const feedItems = Array.from({ length: 12 }, (_, i) => ({
  id: i + 1,
  title: ["Капсула: Весна 2026", "Базовый гардероб", "Тренды сезона", "Деловой стиль", "Уличный шик", "Аксессуары"][i % 6],
  category: categories[1 + (i % 4)],
  liked: i % 3 === 0,
  aspectRatio: i % 3 === 0 ? "4/5" : i % 3 === 1 ? "3/4" : "1/1",
}));

export default function Feed() {
  const [active, setActive] = useState("Все");
  const [likes, setLikes] = useState<Set<number>>(new Set(feedItems.filter(f => f.liked).map(f => f.id)));

  const filtered = active === "Все" ? feedItems : feedItems.filter(f => f.category === active);

  const toggleLike = (id: number) => {
    setLikes(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <div className="container py-4 space-y-4">
      <h1 className="text-xl font-bold">Контент</h1>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-hide">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActive(cat)}
            className={cn(
              "px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors tap-highlight-none",
              active === cat ? "gradient-gold text-primary-foreground" : "bg-card text-muted-foreground shadow-card"
            )}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Masonry-ish grid */}
      <div className="columns-2 gap-3 space-y-3">
        {filtered.map((item, i) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
            className="break-inside-avoid"
          >
            <div
              className="relative bg-secondary rounded-xl overflow-hidden shadow-card group cursor-pointer"
              style={{ aspectRatio: item.aspectRatio }}
            >
              <div className="absolute inset-0 bg-gradient-to-t from-foreground/30 to-transparent" />
              <button
                onClick={(e) => { e.stopPropagation(); toggleLike(item.id); }}
                className="absolute top-2.5 right-2.5 w-8 h-8 rounded-full bg-card/80 backdrop-blur-sm flex items-center justify-center tap-highlight-none transition-transform active:scale-90"
              >
                <Heart className={cn("h-4 w-4 transition-colors", likes.has(item.id) ? "fill-destructive text-destructive" : "text-foreground")} />
              </button>
              <div className="absolute bottom-0 left-0 right-0 p-3">
                <p className="text-xs font-medium text-primary-foreground">{item.title}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
