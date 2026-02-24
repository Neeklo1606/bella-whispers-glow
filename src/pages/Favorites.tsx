import { motion } from "framer-motion";
import { Heart } from "lucide-react";

const saved = Array.from({ length: 4 }, (_, i) => ({
  id: i + 1,
  title: ["Капсула: Весна", "Базовый гардероб", "Деловой стиль", "Уличный шик"][i],
}));

export default function Favorites() {
  return (
    <div className="container py-4 space-y-4">
      <h1 className="text-xl font-bold">Избранное</h1>
      {saved.length === 0 ? (
        <div className="text-center py-16 text-muted-foreground">
          <Heart className="h-10 w-10 mx-auto mb-3 text-muted" />
          <p className="text-sm">Сохраняйте любимые образы здесь</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {saved.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-secondary rounded-xl aspect-[3/4] relative overflow-hidden shadow-card"
            >
              <div className="absolute inset-0 bg-gradient-to-t from-foreground/30 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-3">
                <p className="text-xs font-medium text-primary-foreground">{item.title}</p>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
