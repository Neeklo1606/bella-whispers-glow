import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, ChevronLeft, ChevronRight, Plus, Minus, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
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
  "Авторские разборы с готовыми ссылками",
  "Комьюнити женщин, которые выбирают стиль как состояние",
  "Экономия времени и денег на шопинге",
  "Глубокие знания, а не поверхностные советы",
  "Промокоды, которые отбивают стоимость подписки",
];

const contentBlocks = [
  { title: "Капсулы на сезон", desc: "Мини‑гардеробы на разные сценарии, собранные из доступных брендов." },
  { title: "Живые примерки", desc: "Видео и фото из примерочных с готовыми ссылками на вещи." },
  { title: "Разбор гардероба", desc: "Гайды, что оставить, что убрать и как всё сочетать." },
  { title: "Ответы на вопросы", desc: "Белла отвечает в чате на ваши запросы и ситуации." },
  { title: "Промокоды и находки", desc: "Подборки по бюджетам и брендам, которые помогают экономить." },
  { title: "Личное", desc: "Мысли о стиле и жизни, которых нет в открытых соцсетях." },
];

const testimonials = [
  { name: "Анна К.", text: "Белла полностью изменила мой подход к гардеробу. Я перестала покупать лишнее и наконец собрала базу, которая работает каждый день." },
  { name: "Мария Д.", text: "Капсулы — это находка! Собрала базовый гардероб за неделю. Теперь каждое утро одеваюсь за 5 минут и выгляжу отлично." },
  { name: "Елена С.", text: "Персональная консультация стоила каждой копейки. Белла увидела то, чего я не замечала годами, и помогла выстроить стиль." },
  { name: "Ольга П.", text: "Промокоды от Беллы окупили подписку в первый же месяц. А ещё чат — это тёплое место с потрясающими девушками." },
];

const faqItems = [
  { q: "Я ничего не понимаю в стиле. Мне подойдёт чат?", a: "Конечно! Чат создан именно для тех, кто хочет разобраться. Белла объясняет всё простым языком и помогает на каждом этапе." },
  { q: "Успею ли я, если много работаю?", a: "Все материалы доступны в записи. Вы смотрите и читаете в своём темпе, когда удобно." },
  { q: "Что будет, если я не продлю подписку?", a: "Доступ к чату автоматически закроется. Вы сможете вернуться в любой момент, оплатив следующий месяц." },
  { q: "Можно ли войти с середины месяца?", a: "Да, подписка действует 30 дней с момента оплаты. Вы получите доступ ко всем материалам текущего месяца." },
  { q: "Материалы останутся со мной навсегда?", a: "Материалы доступны, пока активна подписка. Ключевые гайды и чек‑листы можно сохранить себе." },
];

const calendarEvents: Record<number, string> = {
  1: "Сбор заявок",
  2: "Сбор заявок",
  3: "Сбор заявок",
  6: "Старт месяца",
  10: "Примерки",
  11: "Капсулы",
  17: "Примерки",
  18: "Капсулы",
  24: "Примерки",
  25: "Капсулы",
  28: "Разбор образов",
  29: "Разбор образов",
};

/* ─── nav items ─── */
const navLinks = [
  { label: "Программа", href: "#program" },
  { label: "Для кого", href: "#for-whom" },
  { label: "Отзывы", href: "#reviews" },
  { label: "Вопросы", href: "#faq" },
];

/* ─── components ─── */

function StickyHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handleNav = (href: string) => {
    setMenuOpen(false);
    const el = document.querySelector(href);
    el?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-background/90 backdrop-blur-md border-b border-border" : "bg-transparent"
      }`}
    >
      <div className="max-w-5xl mx-auto flex items-center justify-between h-14 px-5">
        <a href="#" className="text-sm font-semibold tracking-[0.15em] uppercase text-foreground">
          Bella Hasias
        </a>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-6">
          {navLinks.map((l) => (
            <button
              key={l.href}
              onClick={() => handleNav(l.href)}
              className="text-xs tracking-wide uppercase text-muted-foreground hover:text-foreground transition-colors"
            >
              {l.label}
            </button>
          ))}
          <Button size="sm" asChild>
            <a href={TELEGRAM_LINK} target="_blank" rel="noopener noreferrer">Вступить</a>
          </Button>
        </nav>

        {/* Mobile burger */}
        <button onClick={() => setMenuOpen(!menuOpen)} className="md:hidden p-2 -mr-2">
          {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile dropdown */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-background/95 backdrop-blur-md border-b border-border overflow-hidden"
          >
            <div className="px-5 py-4 flex flex-col gap-3">
              {navLinks.map((l) => (
                <button
                  key={l.href}
                  onClick={() => handleNav(l.href)}
                  className="text-sm text-left text-muted-foreground hover:text-foreground py-2"
                >
                  {l.label}
                </button>
              ))}
              <Button size="sm" className="mt-2" asChild>
                <a href={TELEGRAM_LINK} target="_blank" rel="noopener noreferrer">Вступить в чат</a>
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

function MobileStickyBar() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 300);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 p-4 bg-background/95 backdrop-blur-md border-t border-border md:hidden z-40">
      <Button size="lg" className="w-full" asChild>
        <a href={TELEGRAM_LINK} target="_blank" rel="noopener noreferrer">Вступить в чат</a>
      </Button>
    </div>
  );
}

function CalendarGrid() {
  const daysOfWeek = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"];
  // March 2026 starts on Sunday (index 6 in Mon-start week)
  const startOffset = 6;
  const totalDays = 31;
  const cells = [];

  for (let i = 0; i < startOffset; i++) {
    cells.push(<div key={`empty-${i}`} className="aspect-square" />);
  }

  for (let d = 1; d <= totalDays; d++) {
    const event = calendarEvents[d];
    cells.push(
      <div
        key={d}
        className={`aspect-square border border-border flex flex-col items-center justify-center p-1 text-center transition-colors ${
          event ? "bg-accent/50" : ""
        }`}
      >
        <span className="text-xs font-medium">{d}</span>
        {event && <span className="text-[9px] md:text-[10px] text-accent-foreground leading-tight mt-0.5">{event}</span>}
      </div>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-7 gap-0 mb-1">
        {daysOfWeek.map((day) => (
          <div key={day} className="text-center text-[10px] tracking-widest uppercase text-muted-foreground py-2 font-medium">
            {day}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-0">{cells}</div>
    </div>
  );
}

function TestimonialCarousel() {
  const [current, setCurrent] = useState(0);
  const total = testimonials.length;

  const prev = () => setCurrent((c) => (c - 1 + total) % total);
  const next = () => setCurrent((c) => (c + 1) % total);

  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        <motion.div
          key={current}
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -30 }}
          transition={{ duration: 0.3 }}
          className="bg-card rounded-2xl p-6 md:p-10 shadow-soft"
        >
          <p className="text-base md:text-lg leading-relaxed text-foreground mb-6">
            "{testimonials[current].text}"
          </p>
          <p className="text-xs tracking-widest uppercase text-muted-foreground">
            — {testimonials[current].name}
          </p>
        </motion.div>
      </AnimatePresence>

      <div className="flex items-center justify-between mt-6">
        <div className="flex gap-2">
          {testimonials.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrent(i)}
              className={`w-2 h-2 rounded-full transition-colors ${
                i === current ? "bg-primary" : "bg-border"
              }`}
            />
          ))}
        </div>
        <div className="flex gap-2">
          <button onClick={prev} className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-colors">
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button onClick={next} className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-colors">
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function FAQAccordion() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="divide-y divide-border">
      {faqItems.map((item, i) => (
        <div key={i}>
          <button
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
            className="w-full flex items-center justify-between py-5 text-left group"
          >
            <span className="text-sm md:text-base font-medium pr-4 text-foreground group-hover:text-primary transition-colors">
              {item.q}
            </span>
            <span className="shrink-0 w-8 h-8 rounded-full border border-border flex items-center justify-center transition-colors group-hover:border-primary">
              {openIndex === i ? <Minus className="h-3.5 w-3.5" /> : <Plus className="h-3.5 w-3.5" />}
            </span>
          </button>
          <AnimatePresence>
            {openIndex === i && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25 }}
                className="overflow-hidden"
              >
                <p className="text-sm text-muted-foreground leading-relaxed pb-5 pr-12">
                  {item.a}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
}

/* ─── section wrapper ─── */
const Section = ({
  children,
  id,
  className = "",
  dark = false,
}: {
  children: React.ReactNode;
  id?: string;
  className?: string;
  dark?: boolean;
}) => (
  <section
    id={id}
    className={`${dark ? "bg-foreground text-background" : ""} ${className}`}
  >
    <div className="max-w-5xl mx-auto px-5 py-20 md:py-28">{children}</div>
  </section>
);

const SectionLabel = ({ children }: { children: React.ReactNode }) => (
  <p className="text-[11px] tracking-[0.2em] uppercase text-muted-foreground mb-4">{children}</p>
);

/* ─── page ─── */

export default function Index() {
  const scrollTo = (id: string) => {
    document.querySelector(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-background">
      <StickyHeader />

      {/* ───── BLOCK 1: HERO ───── */}
      <section className="min-h-screen flex flex-col md:flex-row pt-14">
        <div className="flex-1 flex flex-col justify-center px-5 md:px-12 lg:px-20 py-12 md:py-0">
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-[11px] tracking-[0.2em] uppercase text-muted-foreground mb-6"
          >
            Закрытый Telegram‑клуб о стиле
          </motion.p>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-4xl md:text-6xl lg:text-7xl font-bold leading-[0.95] tracking-tight uppercase"
          >
            Стильный чат
            <br />
            Беллы Хасиас
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-6 text-sm md:text-base text-muted-foreground max-w-sm leading-relaxed"
          >
            Образы на каждый день, капсулы, ссылки и поддержка стилиста в одном месте.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-8 flex flex-col sm:flex-row gap-3"
          >
            <Button size="lg" asChild>
              <a href={TELEGRAM_LINK} target="_blank" rel="noopener noreferrer">
                Вступить в чат
              </a>
            </Button>
            <Button variant="outline" size="lg" onClick={() => scrollTo("#program")}>
              Смотреть программу месяца
            </Button>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.8 }}
          className="flex-1 min-h-[50vh] md:min-h-0 relative"
        >
          <img
            src={heroImage}
            alt="Bella Hasias"
            className="w-full h-full object-cover object-top"
          />
          <p className="absolute bottom-4 left-4 right-4 text-[10px] tracking-[0.15em] uppercase text-background/80 bg-foreground/40 backdrop-blur-sm px-3 py-2 rounded-lg">
            Март 2026 · Тема месяца: весенний гардероб
          </p>
        </motion.div>
      </section>

      {/* ───── BLOCK 2: FOR WHOM ───── */}
      <Section id="for-whom">
        <SectionLabel>Для кого этот чат</SectionLabel>
        <h2 className="text-2xl md:text-4xl font-bold mb-12 max-w-lg">
          Если хотя бы одно — про вас, вам сюда
        </h2>

        <div className="relative">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {painPoints.map((point, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="bg-card rounded-xl p-5 shadow-soft"
              >
                <p className="text-xs tracking-widest uppercase leading-relaxed text-foreground">
                  {point}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* ───── BLOCK 3: WHY CHOOSE ───── */}
      <Section className="bg-secondary">
        <SectionLabel>Почему участницы выбирают чат</SectionLabel>
        <h2 className="text-2xl md:text-4xl font-bold mb-12">Не просто советы, а система</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6 max-w-3xl">
          {benefits.map((b, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.06 }}
              className="flex items-start gap-3"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
              <p className="text-sm leading-relaxed">{b}</p>
            </motion.div>
          ))}
        </div>
      </Section>

      {/* ───── BLOCK 4: CALENDAR ───── */}
      <Section id="program">
        <SectionLabel>Программа</SectionLabel>
        <h2 className="text-2xl md:text-4xl font-bold mb-10">Как устроен месяц в чате</h2>

        <div className="max-w-xl mx-auto md:mx-0">
          <CalendarGrid />
          <p className="text-xs text-muted-foreground mt-6 leading-relaxed">
            Подписка действует 30 дней с момента оплаты. Если не продлеваете — доступ автоматически закрывается.
          </p>
        </div>
      </Section>

      {/* ───── BLOCK 5: WHAT'S INSIDE ───── */}
      <Section className="bg-secondary">
        <SectionLabel>Контент</SectionLabel>
        <h2 className="text-2xl md:text-4xl font-bold mb-12">Что внутри</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {contentBlocks.map((block, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.06 }}
            >
              <h3 className="text-sm font-semibold mb-2">{block.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{block.desc}</p>
            </motion.div>
          ))}
        </div>
      </Section>

      {/* ───── BLOCK 6: TESTIMONIALS ───── */}
      <Section id="reviews">
        <SectionLabel>Отзывы</SectionLabel>
        <h2 className="text-2xl md:text-4xl font-bold mb-10">Участницы говорят</h2>
        <div className="max-w-2xl">
          <TestimonialCarousel />
        </div>
      </Section>

      {/* ───── BLOCK 7: FAQ ───── */}
      <Section id="faq" className="bg-secondary">
        <SectionLabel>FAQ</SectionLabel>
        <h2 className="text-2xl md:text-4xl font-bold mb-10">Вопросы</h2>
        <div className="max-w-2xl">
          <FAQAccordion />
        </div>
      </Section>

      {/* ───── BLOCK 8: LAST CALL ───── */}
      <Section dark id="join">
        <div className="text-center">
          <p className="text-[11px] tracking-[0.3em] uppercase mb-6 opacity-60">Last call</p>
          <h2 className="text-2xl md:text-4xl font-bold mb-6">
            Осталось 12 мест на март
          </h2>
          <p className="text-sm opacity-70 mb-2">
            Подписка закрывается 05.03 в 23:59
          </p>
          <p className="text-sm opacity-70 mb-8">
            Стоимость: 990 ₽ первый месяц, далее 1 500 ₽
          </p>
          <Button
            size="lg"
            className="bg-background text-foreground hover:bg-background/90"
            asChild
          >
            <a href={TELEGRAM_LINK} target="_blank" rel="noopener noreferrer">
              Вступить в чат
            </a>
          </Button>
          <p className="mt-4">
            <a
              href="#program"
              onClick={(e) => {
                e.preventDefault();
                scrollTo("#program");
              }}
              className="text-xs underline underline-offset-4 opacity-50 hover:opacity-80 transition-opacity"
            >
              Сначала посмотреть демо
            </a>
          </p>
        </div>
      </Section>

      {/* ───── BLOCK 9: FINAL CTA ───── */}
      <Section>
        <div className="text-center max-w-lg mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold mb-4 text-balance">
            Не откладывай свою лучшую версию на потом
          </h2>
          <p className="text-sm text-muted-foreground mb-8">
            Займёмся гардеробом в спокойном, поддерживающем формате.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button size="lg" asChild>
              <a href={TELEGRAM_LINK} target="_blank" rel="noopener noreferrer">
                Вступить в чат
              </a>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <a href={CONTACT_LINK} target="_blank" rel="noopener noreferrer">
                Написать Белле
              </a>
            </Button>
          </div>
        </div>
      </Section>

      {/* Footer */}
      <footer className="py-8 border-t border-border mb-16 md:mb-0">
        <div className="max-w-5xl mx-auto px-5 text-center text-xs text-muted-foreground space-y-2">
          <p>© 2026 Bella Hasias. Все права защищены.</p>
        </div>
      </footer>

      <MobileStickyBar />
    </div>
  );
}
