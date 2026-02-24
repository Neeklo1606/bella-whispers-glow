import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, BookOpen, Target, MessageCircle, Star, Lock, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroImage from "@/assets/hero-bella.jpg";

const values = [
  { icon: BookOpen, title: "База знаний", desc: "Гайды, капсулы и разборы гардероба" },
  { icon: Target, title: "Персонализация", desc: "Рекомендации под ваш стиль и бюджет" },
  { icon: MessageCircle, title: "Комьюнити", desc: "Общение с единомышленницами" },
];

const testimonials = [
  { name: "Анна К.", text: "Белла полностью изменила мой подход к гардеробу." },
  { name: "Мария Д.", text: "Капсулы — это находка! Собрала базовый гардероб за неделю." },
  { name: "Елена С.", text: "Персональная консультация стоила каждой копейки." },
];

export default function Index() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/90 backdrop-blur-md">
        <div className="container flex items-center justify-between h-14">
          <Link to="/" className="text-sm font-semibold tracking-widest uppercase text-foreground">
            BH
          </Link>
          <nav className="hidden md:flex items-center gap-8 text-sm">
            <Link to="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">Тарифы</Link>
            <Link to="/login" className="text-muted-foreground hover:text-foreground transition-colors">Контакты</Link>
          </nav>
          <Button variant="default" size="sm" asChild>
            <Link to="/login">Связаться</Link>
          </Button>
        </div>
      </header>

      {/* Hero — split layout like bellahasias.ru */}
      <section className="min-h-[90vh] flex flex-col md:flex-row">
        <div className="flex-1 flex flex-col justify-center px-6 md:px-16 lg:px-24 py-12 md:py-0">
          <motion.p
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="text-xs tracking-[0.2em] uppercase text-muted-foreground mb-6"
          >
            Стилист · UGC · Контент
          </motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-5xl md:text-7xl lg:text-8xl font-bold leading-[0.95] tracking-tight text-foreground"
          >
            Bella<br />Hasias
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="mt-6 text-base text-muted-foreground max-w-sm leading-relaxed"
          >
            Закрытое сообщество с эксклюзивным контентом. Консультации по стилю, капсулы и персональные рекомендации.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="mt-8 flex gap-3"
          >
            <Button variant="default" size="lg" asChild>
              <Link to="/pricing">Связаться</Link>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <Link to="/pricing" className="gap-2">Смотреть работы <ArrowRight className="h-4 w-4" /></Link>
            </Button>
          </motion.div>
        </div>
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.8 }}
          className="flex-1 min-h-[50vh] md:min-h-0"
        >
          <img
            src={heroImage}
            alt="Bella Hasias"
            className="w-full h-full object-cover object-top"
          />
        </motion.div>
      </section>

      {/* Value Props */}
      <section className="py-20 md:py-28 bg-card">
        <div className="container">
          <p className="text-xs tracking-[0.2em] uppercase text-muted-foreground text-center mb-3">Услуги</p>
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-14">Что вас ждёт внутри</h2>
          <div className="grid gap-8 md:grid-cols-3">
            {values.map((v, i) => (
              <motion.div
                key={v.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center mx-auto mb-4">
                  <v.icon className="h-5 w-5 text-foreground" />
                </div>
                <h3 className="text-base font-semibold mb-2">{v.title}</h3>
                <p className="text-sm text-muted-foreground">{v.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 md:py-28">
        <div className="container">
          <p className="text-xs tracking-[0.2em] uppercase text-muted-foreground text-center mb-3">Отзывы</p>
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-14">Более 500 участниц</h2>
          <div className="grid gap-6 md:grid-cols-3 max-w-3xl mx-auto">
            {testimonials.map((t, i) => (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <div className="flex justify-center gap-0.5 mb-3">
                  {Array.from({ length: 5 }).map((_, j) => (
                    <Star key={j} className="h-3.5 w-3.5 fill-foreground text-foreground" />
                  ))}
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed mb-3">"{t.text}"</p>
                <p className="text-xs font-medium">{t.name}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 md:py-28 bg-secondary">
        <div className="container text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Начните свой путь к идеальному стилю</h2>
          <p className="text-muted-foreground mb-8 max-w-md mx-auto text-sm">
            Гибкие тарифы от 990₽/месяц. 7 дней бесплатно.
          </p>
          <Button variant="default" size="lg" asChild>
            <Link to="/pricing">Посмотреть тарифы <ChevronRight className="h-4 w-4" /></Link>
          </Button>
        </div>
      </section>

      {/* Sticky mobile CTA */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-background/95 backdrop-blur-md border-t border-border md:hidden z-40">
        <Button variant="default" size="lg" className="w-full" asChild>
          <Link to="/pricing">Попробовать 7 дней бесплатно</Link>
        </Button>
      </div>

      {/* Footer */}
      <footer className="py-8 border-t border-border mb-16 md:mb-0">
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
