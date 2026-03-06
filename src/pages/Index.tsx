import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import heroImage from "@/assets/hero-bella.jpg";
import fashionImage from "@/assets/for-whom-bg.jpg";

const TELEGRAM_LINK = "https://t.me/bellahasias_bot";
const CONTACT_LINK = "https://t.me/Bella_hasias";

const painPoints = [
  "Полный гардероб, но нечего надеть",
  "Хочешь выглядеть дороже, не увеличивая бюджет",
  "Устаёшь выбирать, что надеть на работу и встречи",
];

const benefits = [
  "Авторские обзоры с готовыми ссылками",
  "Комьюнити, которое выбирает стиль как состояние",
  "Экономия времени и денег на шопинге",
  "Промокоды, которые отбивают стоимость подписки",
];

const faqItems = [
  { q: "Я ничего не понимаю в стиле. Мне подойдёт?", a: "Конечно! Чат создан именно для тех, кто хочет разобраться. Белла объясняет всё простым языком." },
  { q: "Успею ли я, если много работаю?", a: "Все материалы доступны в записи. Вы смотрите и читаете в своём темпе." },
  { q: "Что будет, если не продлю подписку?", a: "Доступ автоматически закроется. Вернуться можно в любой момент." },
  { q: "Можно ли войти с середины месяца?", a: "Да, подписка действует 30 дней с момента оплаты." },
  { q: "Материалы останутся со мной навсегда?", a: "Доступ к материалам активен пока действует подписка. После окончания доступ закрывается." },
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
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-background/85 backdrop-blur-md border-b border-border" : "bg-transparent"
      }`}
    >
      <div className="max-w-[1100px] mx-auto flex items-center justify-between h-12 px-5">
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="text-[10px] tracking-[0.2em] uppercase text-foreground hover:opacity-50 transition-opacity"
        >
          {menuOpen ? "Закрыть" : "Меню"}
        </button>
        <a
          href={CONTACT_LINK}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[10px] tracking-[0.2em] uppercase text-foreground hover:opacity-50 transition-opacity"
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
            transition={{ duration: 0.2 }}
            className="bg-background/95 backdrop-blur-md border-b border-border overflow-hidden"
          >
            <div className="max-w-[1100px] mx-auto px-5 py-6 flex flex-col gap-3">
              {[
                { label: "Для кого", href: "#for-whom" },
                { label: "Почему выбирают", href: "#why" },
                { label: "Вопросы", href: "#faq" },
              ].map((l) => (
                <button
                  key={l.href}
                  onClick={() => {
                    setMenuOpen(false);
                    document.querySelector(l.href)?.scrollIntoView({ behavior: "smooth" });
                  }}
                  className="text-xl font-light text-foreground hover:opacity-50 transition-opacity text-left"
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
/* ─── page ─── */

export default function Index() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      {/* ═══ HERO — fits one mobile screen ═══ */}
      <section className="min-h-[100svh] flex flex-col justify-center pt-14 pb-6 px-5">
        <div className="max-w-[1100px] mx-auto w-full flex flex-col md:flex-row md:items-center md:gap-16">
          {/* Left — text + CTA */}
          <div className="flex-1 flex flex-col justify-center md:max-w-[480px]">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="mb-5"
            >
              <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-3">
                Закрытый канал в Telegram о стиле
              </p>
              <h1 className="text-[36px] md:text-6xl font-display font-bold tracking-tight leading-[1.05] mb-3">
                Стильный чат
                <br />
                Беллы Хасиас
              </h1>
              <p className="text-[11px] md:text-[13px] tracking-[0.08em] text-muted-foreground">
                Образы, капсулы и ссылки в одном месте
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="flex flex-col gap-2 mb-5 md:mb-0"
            >
              <a
                href={TELEGRAM_LINK}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full md:w-auto md:inline-block text-center px-8 py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity"
              >
                Вступить в чат
              </a>
              <button
                onClick={() => document.querySelector("#for-whom")?.scrollIntoView({ behavior: "smooth" })}
                className="text-[10px] tracking-[0.12em] text-muted-foreground hover:text-foreground transition-colors text-center md:text-left py-1"
              >
                Смотреть программу месяца ↓
              </button>
            </motion.div>
          </div>

          {/* Right — photo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="w-full max-w-[420px] mx-auto md:mx-0 md:flex-1"
          >
            <img
              src={heroImage}
              alt="Bella Hasias"
              className="w-full aspect-[3/4] md:aspect-[3/4] object-cover object-top rounded-xl"
            />
            <p className="text-right mt-2 text-[9px] tracking-[0.18em] uppercase text-muted-foreground">
              Март 2026
            </p>
          </motion.div>
        </div>
      </section>

      {/* ═══ PRICING — second screen ═══ */}
      <section className="px-5 py-10 md:py-14">
        <div className="max-w-[480px] mx-auto text-center">
          <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-2">
            Подписка на месяц
          </p>
          <p className="text-4xl md:text-5xl font-display font-bold tracking-tight mb-1">
            990 ₽
          </p>
          <p className="text-[10px] text-muted-foreground mb-1">
            всегда 990 ₽/мес · отмена в любой момент
          </p>
          <p className="text-[10px] text-muted-foreground/70 mb-5">
            Оплата через Telegram‑бота, доступ сразу после оплаты
          </p>
          <a
            href={TELEGRAM_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity"
          >
            Вступить в чат
          </a>
        </div>
      </section>

      {/* ═══ FOR WHOM — 3 compact cards ═══ */}
      <section id="for-whom" className="relative px-5 py-12 md:py-16 overflow-hidden">
        {/* Background photo */}
        <div className="absolute inset-0 opacity-[0.07]">
          <img
            src={fashionImage}
            alt=""
            className="w-full h-full object-cover"
          />
        </div>
        <div className="relative max-w-[600px] mx-auto">
          <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-6">
            Для кого
          </p>
          <div className="flex flex-col gap-3">
            {painPoints.map((point, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06 }}
                className="flex items-start gap-4 bg-card/80 backdrop-blur-sm p-5 rounded-lg"
              >
                <span className="text-lg font-extralight text-foreground/20 leading-none mt-0.5">
                  0{i + 1}
                </span>
                <p className="text-[11px] tracking-[0.08em] uppercase leading-[1.6] text-foreground">
                  {point}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ WHY CHOOSE — compact list ═══ */}
      <section id="why" className="px-5 py-12 md:py-16 border-t border-border">
        <div className="max-w-[600px] mx-auto">
          <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-6">
            Почему выбирают
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {benefits.map((b, i) => (
              <motion.p
                key={i}
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="text-[11px] tracking-[0.06em] uppercase leading-[1.7] text-foreground"
              >
                {b}
              </motion.p>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <section id="faq" className="px-5 py-12 md:py-16 border-t border-border">
        <div className="max-w-[600px] mx-auto">
          <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-6">
            Вопросы
          </p>
          <div className="divide-y divide-border">
            {faqItems.map((item, i) => (
              <div key={i}>
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between py-4 text-left group"
                >
                  <span className="text-[13px] font-light pr-6 group-hover:opacity-50 transition-opacity">
                    {item.q}
                  </span>
                  <span className="shrink-0 text-[10px] text-muted-foreground">
                    {openFaq === i ? "−" : "+"}
                  </span>
                </button>
                <AnimatePresence>
                  {openFaq === i && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <p className="text-[12px] text-muted-foreground leading-relaxed pb-4 pr-10">
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
      <section id="join" className="px-5 py-14 md:py-20 border-t border-border mb-14 md:mb-0">
        <div className="max-w-[480px] mx-auto text-center">
          <h2 className="text-2xl md:text-3xl font-display font-bold tracking-tight mb-2">
            Готова присоединиться?
          </h2>
          <p className="text-[10px] text-muted-foreground mb-5">
            Не откладывай свою лучшую версию на потом
          </p>
          <a
            href={TELEGRAM_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity mb-3"
          >
            Вступить в чат
          </a>
          <a
            href={CONTACT_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[10px] text-muted-foreground hover:text-foreground transition-colors"
          >
            Если остались вопросы — напишите Белле
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 border-t border-border pb-20">
        <p className="text-center text-[9px] tracking-[0.15em] uppercase text-muted-foreground">
          © 2026 Bella Hasias
        </p>
      </footer>
    </div>
  );
}
