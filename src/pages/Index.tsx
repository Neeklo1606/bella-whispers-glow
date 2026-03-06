import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Minus, Menu, X, ChevronLeft, ChevronRight } from "lucide-react";
import heroImage from "@/assets/hero-bella.jpg";

const TELEGRAM_LINK = "https://t.me/bellahasias_bot";
const CONTACT_LINK = "https://t.me/bellahasias";

/* ─── data ─── */

const painPoints = [
  "Полный гардероб, но нечего надеть",
  "Хочешь выглядеть дороже, не увеличивая бюджет",
  "Устаёшь выбирать, что надеть на работу и встречи",
  "Хочешь меньше импульсивных покупок",
];

const benefits = [
  "Авторские обзоры из примерочных с готовыми ссылками",
  "Комьюнити женщин, которые выбирают стиль как состояние",
  "Экономия времени и денег",
  "Глубокие знания, которые помогают развивать персональный стиль",
  "Эксклюзивные промокоды, которые экономят больше стоимости подписки",
];

const testimonials = [
  { name: "Анна К.", text: "Белла полностью изменила мой подход к гардеробу. Я перестала покупать лишнее и наконец собрала базу, которая работает каждый день." },
  { name: "Мария Д.", text: "Капсулы — это находка! Собрала базовый гардероб за неделю. Теперь каждое утро одеваюсь за 5 минут и выгляжу отлично." },
  { name: "Елена С.", text: "Персональная консультация стоила каждой копейки. Белла увидела то, чего я не замечала годами." },
  { name: "Ольга П.", text: "Промокоды от Беллы окупили подписку в первый же месяц. А ещё чат — это тёплое место с потрясающими девушками." },
];

const faqItems = [
  { q: "Я ничего не понимаю в стиле. Мне подойдёт?", a: "Конечно! Чат создан именно для тех, кто хочет разобраться. Белла объясняет всё простым языком." },
  { q: "Успею ли я, если много работаю?", a: "Все материалы доступны в записи. Вы смотрите и читаете в своём темпе." },
  { q: "Что будет, если не продлю подписку?", a: "Доступ автоматически закроется. Вернуться можно в любой момент." },
  { q: "Можно ли войти с середины месяца?", a: "Да, подписка действует 30 дней с момента оплаты." },
];

/* ─── header ─── */

function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled ? "bg-background/80 backdrop-blur-md" : "bg-transparent"
      }`}
    >
      <div className="max-w-[1400px] mx-auto flex items-center justify-between h-14 px-6">
        <div className="flex items-center gap-3">
          <span className="w-2.5 h-2.5 rounded-full bg-foreground" />
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="text-[11px] tracking-[0.2em] uppercase text-foreground hover:opacity-60 transition-opacity"
          >
            {menuOpen ? "Закрыть" : "Меню"}
          </button>
        </div>

        <a
          href={TELEGRAM_LINK}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[11px] tracking-[0.2em] uppercase text-foreground hover:opacity-60 transition-opacity"
        >
          Связаться
        </a>
      </div>

      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-background/95 backdrop-blur-md border-b border-border overflow-hidden"
          >
            <div className="max-w-[1400px] mx-auto px-6 py-8 flex flex-col gap-4">
              {[
                { label: "Для кого", href: "#for-whom" },
                { label: "Почему выбирают", href: "#why" },
                { label: "Отзывы", href: "#reviews" },
                { label: "Вопросы", href: "#faq" },
              ].map((l) => (
                <button
                  key={l.href}
                  onClick={() => {
                    setMenuOpen(false);
                    document.querySelector(l.href)?.scrollIntoView({ behavior: "smooth" });
                  }}
                  className="text-2xl font-light text-foreground hover:opacity-60 transition-opacity text-left"
                >
                  {l.label}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

/* ─── mobile sticky CTA ─── */

function MobileStickyBar() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 400);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 p-4 bg-background/90 backdrop-blur-md md:hidden z-40">
      <a
        href={TELEGRAM_LINK}
        target="_blank"
        rel="noopener noreferrer"
        className="block w-full py-4 bg-foreground text-background text-center text-xs tracking-[0.15em] uppercase rounded-full"
      >
        Вступить в чат
      </a>
    </div>
  );
}

/* ─── page ─── */

export default function Index() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      {/* ═══ HERO ═══ */}
      <section className="min-h-screen flex flex-col items-center justify-center pt-14 pb-20 px-6">
        {/* Top text row */}
        <div className="w-full max-w-[1100px] flex flex-col md:flex-row md:items-end md:justify-between mb-8 md:mb-12 mt-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="max-w-[280px]"
          >
            <p className="text-[11px] tracking-[0.15em] uppercase leading-relaxed text-muted-foreground">
              Закрытый канал
              <br />
              по подписке в Telegram
              <br />
              всё о стиле: обзоры,
              <br />
              капсулы и обучающие
              <br />
              материалы
            </p>
          </motion.div>
        </div>

        {/* Center photo card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.2 }}
          className="relative w-full max-w-[480px]"
        >
          <div className="bg-card p-3 pb-6">
            <img
              src={heroImage}
              alt="Bella Hasias"
              className="w-full aspect-[3/4] object-cover object-top"
            />
            <div className="mt-4 px-1">
              <h1 className="text-3xl md:text-4xl font-light lowercase tracking-tight leading-[1.1]">
                стильный
                <br />
                чат
              </h1>
            </div>
          </div>
          {/* Name caption */}
          <p className="text-right mt-3 text-[11px] tracking-[0.15em] uppercase text-muted-foreground">
            Беллы Хасиас
          </p>

          {/* Side label */}
          <div className="hidden md:block absolute -right-16 top-1/2 -translate-y-1/2">
            <p className="text-[10px] tracking-[0.2em] uppercase text-muted-foreground [writing-mode:vertical-rl] rotate-180">
              Март 2026
            </p>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="w-full max-w-[1100px] flex justify-end mt-12"
        >
          <div className="text-right">
            <p className="text-5xl md:text-7xl font-extralight italic tracking-tight">5000<sup className="text-2xl md:text-3xl">+</sup></p>
            <p className="text-[10px] tracking-[0.15em] uppercase text-muted-foreground mt-2 leading-relaxed">
              Девушек обрели
              <br />
              собственный стиль
              <br />
              вместе со мной
            </p>
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-12"
        >
          <a
            href={TELEGRAM_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-10 py-4 border border-foreground rounded-full text-xs tracking-[0.2em] uppercase hover:bg-foreground hover:text-background transition-all duration-300"
          >
            Вступить в чат
          </a>
        </motion.div>
      </section>

      {/* ═══ FOR WHOM — full-bleed photo + numbered cards ═══ */}
      <section id="for-whom" className="relative">
        <div className="relative min-h-[90vh] md:min-h-screen overflow-hidden bg-secondary">
          {/* Background image placeholder — using gradient */}
          <div className="absolute inset-0 bg-gradient-to-b from-secondary via-muted to-secondary" />

          {/* Numbered cards overlaid */}
          <div className="relative z-10 max-w-[1200px] mx-auto px-6 py-24 md:py-32 grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-12">
            {painPoints.map((point, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className={`bg-card/90 backdrop-blur-sm p-8 md:p-10 ${
                  i === 1 ? "md:mt-20" : i === 2 ? "md:-mt-10" : i === 3 ? "md:mt-10" : ""
                }`}
              >
                <p className="text-4xl md:text-5xl font-extralight italic text-foreground/20 mb-4">
                  0{i + 1}
                </p>
                <p className="text-[11px] md:text-xs tracking-[0.12em] uppercase leading-[1.8] text-foreground">
                  {point}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ WHY CHOOSE — editorial scattered text ═══ */}
      <section id="why" className="py-24 md:py-36 px-6">
        <div className="max-w-[900px] mx-auto">
          <motion.h2
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center text-2xl md:text-3xl font-light lowercase tracking-tight mb-20"
          >
            почему выбирают
            <br />
            именно наш чат
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-y-12 md:gap-x-16 md:gap-y-16">
            {benefits.map((b, i) => (
              <motion.p
                key={i}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="text-[11px] tracking-[0.1em] uppercase leading-[1.9] text-foreground"
              >
                {b}
              </motion.p>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ REVIEWS — minimal carousel ═══ */}
      <section id="reviews" className="border-t border-border">
        <div className="max-w-[1200px] mx-auto px-6 py-24 md:py-32">
          <div className="flex items-baseline justify-between mb-16">
            <p className="text-[11px] tracking-[0.2em] uppercase text-muted-foreground">
              Что говорят участницы
            </p>
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={currentTestimonial}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.4 }}
              className="max-w-2xl"
            >
              <p className="text-lg md:text-xl font-light leading-relaxed mb-8">
                «{testimonials[currentTestimonial].text}»
              </p>
              <p className="text-[11px] tracking-[0.2em] uppercase text-muted-foreground">
                — {testimonials[currentTestimonial].name}
              </p>
            </motion.div>
          </AnimatePresence>

          <div className="flex items-center gap-4 mt-12">
            {testimonials.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentTestimonial(i)}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  i === currentTestimonial ? "bg-foreground scale-125" : "bg-border"
                }`}
              />
            ))}
            <div className="flex gap-2 ml-auto">
              <button
                onClick={() => setCurrentTestimonial((c) => (c - 1 + testimonials.length) % testimonials.length)}
                className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-foreground hover:text-background hover:border-foreground transition-all"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                onClick={() => setCurrentTestimonial((c) => (c + 1) % testimonials.length)}
                className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-foreground hover:text-background hover:border-foreground transition-all"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <section id="faq" className="border-t border-border">
        <div className="max-w-[800px] mx-auto px-6 py-24 md:py-32">
          <p className="text-[11px] tracking-[0.2em] uppercase text-muted-foreground mb-12">
            Вопросы
          </p>

          <div className="divide-y divide-border">
            {faqItems.map((item, i) => (
              <div key={i}>
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between py-6 text-left group"
                >
                  <span className="text-sm md:text-base font-light pr-8 group-hover:opacity-60 transition-opacity">
                    {item.q}
                  </span>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {openFaq === i ? "−" : "+"}
                  </span>
                </button>
                <AnimatePresence>
                  {openFaq === i && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.25 }}
                      className="overflow-hidden"
                    >
                      <p className="text-sm text-muted-foreground leading-relaxed pb-6 pr-12">
                        {item.a}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FINAL CTA ═══ */}
      <section className="border-t border-border">
        <div className="max-w-[600px] mx-auto px-6 py-24 md:py-32 text-center">
          <p className="text-[10px] tracking-[0.3em] uppercase text-muted-foreground mb-4">
            990 ₽ первый месяц
          </p>
          <h2 className="text-2xl md:text-3xl font-light lowercase tracking-tight mb-8">
            Не откладывай свою
            <br />
            лучшую версию на потом
          </h2>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a
              href={TELEGRAM_LINK}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-10 py-4 bg-foreground text-background rounded-full text-xs tracking-[0.2em] uppercase hover:opacity-80 transition-opacity"
            >
              Вступить в чат
            </a>
            <a
              href={CONTACT_LINK}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-10 py-4 border border-border rounded-full text-xs tracking-[0.2em] uppercase hover:bg-foreground hover:text-background hover:border-foreground transition-all duration-300"
            >
              Написать Белле
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-border mb-16 md:mb-0">
        <div className="max-w-[1200px] mx-auto px-6 text-center">
          <p className="text-[10px] tracking-[0.15em] uppercase text-muted-foreground">
            © 2026 Bella Hasias
          </p>
        </div>
      </footer>

      <MobileStickyBar />
    </div>
  );
}
