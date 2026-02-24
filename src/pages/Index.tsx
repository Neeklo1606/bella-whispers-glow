import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { BookOpen, Target, MessageCircle, Star, ChevronRight, Lock, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroImage from "@/assets/hero-fashion.jpg";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

const values = [
  { icon: BookOpen, title: "База знаний", desc: "Гайды, капсулы, разборы гардероба от профессионального стилиста" },
  { icon: Target, title: "Персонализация", desc: "Рекомендации под ваш стиль, тип фигуры и бюджет" },
  { icon: MessageCircle, title: "Закрытое комьюнити", desc: "Общение с единомышленницами и поддержка стилиста" },
];

const testimonials = [
  { name: "Анна К.", text: "Белла полностью изменила мой подход к гардеробу. Теперь одеваюсь осознанно и с удовольствием!", rating: 5 },
  { name: "Мария Д.", text: "Капсулы — это находка! Собрала базовый гардероб за неделю, и всё сочетается.", rating: 5 },
  { name: "Елена С.", text: "Персональная консультация стоила каждой копейки. Рекомендую премиум-подписку!", rating: 5 },
];

const previewCards = [
  "Капсула: Весна 2026", "Тренды сезона", "Базовый гардероб",
  "Обувь на каждый день", "Сумки: гид по стилям", "Образы для офиса",
];

export default function Index() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/90 backdrop-blur-md border-b border-border">
        <div className="container flex items-center justify-between h-14">
          <Link to="/" className="text-lg font-bold tracking-tight text-foreground">
            Bella<span className="text-primary">Hasias</span>
          </Link>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/pricing">Тарифы</Link>
            </Button>
            <Button variant="gold" size="sm" asChild>
              <Link to="/login">Войти</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0">
          <img src={heroImage} alt="Fashion editorial" className="w-full h-full object-cover object-top" />
          <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/40 to-background" />
        </div>
        <div className="container relative pt-20 pb-32 md:pt-32 md:pb-40">
          <motion.div
            initial="hidden"
            animate="visible"
            className="max-w-lg"
          >
            <motion.h1
              variants={fadeUp} custom={0}
              className="text-4xl md:text-5xl lg:text-6xl font-bold leading-[1.1] text-foreground text-balance"
            >
              Ваш персональный стилист в кармане
            </motion.h1>
            <motion.p
              variants={fadeUp} custom={1}
              className="mt-4 text-lg text-muted-foreground leading-relaxed max-w-md"
            >
              Закрытое сообщество с эксклюзивным контентом от Беллы Хасиас. Капсулы, тренды, персональные рекомендации.
            </motion.p>
            <motion.div variants={fadeUp} custom={2} className="mt-8 flex flex-col sm:flex-row gap-3">
              <Button variant="gold" size="xl" asChild>
                <Link to="/pricing">Начать бесплатный пробный период</Link>
              </Button>
            </motion.div>
            <motion.p variants={fadeUp} custom={3} className="mt-3 text-xs text-muted-foreground flex items-center gap-1">
              <Shield className="h-3.5 w-3.5" /> 7 дней бесплатно • Отмена в любое время
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Value Props */}
      <section className="py-16 md:py-24">
        <div className="container">
          <motion.h2
            initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
            className="text-2xl md:text-3xl font-bold text-center mb-12"
          >
            Что вас ждёт внутри
          </motion.h2>
          <div className="grid gap-6 md:grid-cols-3">
            {values.map((v, i) => (
              <motion.div
                key={v.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-card rounded-2xl p-6 shadow-card hover:shadow-elevated transition-shadow duration-300"
              >
                <div className="w-12 h-12 rounded-xl gradient-gold flex items-center justify-center mb-4">
                  <v.icon className="h-6 w-6 text-primary-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{v.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{v.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-16 bg-card">
        <div className="container">
          <div className="text-center mb-10">
            <p className="text-primary font-semibold text-sm uppercase tracking-wider mb-2">Отзывы</p>
            <h2 className="text-2xl md:text-3xl font-bold">Более 500 участниц доверяют Белле</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {testimonials.map((t, i) => (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-background rounded-2xl p-5 shadow-card"
              >
                <div className="flex gap-0.5 mb-3">
                  {Array.from({ length: t.rating }).map((_, j) => (
                    <Star key={j} className="h-4 w-4 fill-primary text-primary" />
                  ))}
                </div>
                <p className="text-sm text-foreground leading-relaxed mb-3">"{t.text}"</p>
                <p className="text-xs font-medium text-muted-foreground">{t.name}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Content Preview */}
      <section className="py-16 md:py-24">
        <div className="container">
          <h2 className="text-2xl md:text-3xl font-bold text-center mb-10">Превью контента</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {previewCards.map((title, i) => (
              <motion.div
                key={title}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="relative bg-secondary rounded-2xl aspect-[3/4] flex items-end p-4 overflow-hidden group cursor-pointer"
              >
                <div className="absolute inset-0 bg-gradient-to-t from-foreground/40 to-transparent" />
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-foreground/20 backdrop-blur-sm">
                  <div className="flex items-center gap-1.5 text-primary-foreground text-xs font-medium">
                    <Lock className="h-3.5 w-3.5" /> Подпишитесь, чтобы увидеть
                  </div>
                </div>
                <p className="relative text-sm font-medium text-primary-foreground">{title}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Teaser */}
      <section className="py-16 bg-card">
        <div className="container text-center">
          <h2 className="text-2xl md:text-3xl font-bold mb-3">Гибкие тарифы от 990₽/месяц</h2>
          <p className="text-muted-foreground mb-6">Выберите план, который подходит именно вам</p>
          <Button variant="gold" size="lg" asChild>
            <Link to="/pricing">Посмотреть тарифы <ChevronRight className="h-4 w-4" /></Link>
          </Button>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 md:py-28">
        <div className="container text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-balance">
            Начните свой путь к идеальному стилю
          </h2>
          <p className="text-muted-foreground mb-8 max-w-md mx-auto">
            Присоединяйтесь к закрытому сообществу и получите доступ к эксклюзивному контенту
          </p>
          <Button variant="gold" size="xl" asChild>
            <Link to="/pricing">Попробовать 7 дней бесплатно</Link>
          </Button>
        </div>
      </section>

      {/* Sticky mobile CTA */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-background/95 backdrop-blur-md border-t border-border md:hidden z-40">
        <Button variant="gold" size="lg" className="w-full" asChild>
          <Link to="/pricing">Попробовать 7 дней бесплатно</Link>
        </Button>
      </div>

      {/* Footer */}
      <footer className="py-8 border-t border-border md:mb-0 mb-16">
        <div className="container text-center text-xs text-muted-foreground space-y-2">
          <p>© 2026 BellaHasias. Все права защищены.</p>
          <div className="flex justify-center gap-4">
            <Link to="/privacy" className="hover:text-foreground transition-colors">Конфиденциальность</Link>
            <Link to="/terms" className="hover:text-foreground transition-colors">Условия</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
