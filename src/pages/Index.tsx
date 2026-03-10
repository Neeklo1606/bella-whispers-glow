import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import heroImage from "@/assets/hero-bella.jpg";
import chatScreen1 from "@/assets/chat-screen-1.png";
import chatScreen2 from "@/assets/chat-screen-2.png";
import chatScreen3 from "@/assets/chat-screen-3.jpg";
import chatScreen4 from "@/assets/chat-screen-4.jpg";
import chatScreen5 from "@/assets/chat-screen-5.jpg";
import chatScreen6 from "@/assets/chat-screen-6.jpg";
import { useMiniappContent } from "@/hooks/useMiniappContent";

const chatScreenshots = [chatScreen1, chatScreen2, chatScreen3, chatScreen4, chatScreen5, chatScreen6];

/* ─── header ─── */

function Header({ contactLink }: { contactLink: string }) {
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
          href={contactLink}
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
                { label: "Что в чате?", href: "#what-inside" },
                { label: "Цена", href: "#pricing" },
                { label: "Вопросы", href: "#faq" },
              ].map((l) => (
                 <button
                  key={l.href}
                  onClick={() => {
                    setMenuOpen(false);
                    setTimeout(() => {
                      document.querySelector(l.href)?.scrollIntoView({ behavior: "smooth" });
                    }, 250);
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
                href={telegramLink}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full md:w-auto md:inline-block text-center px-8 py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity"
              >
                Вступить в чат
              </a>
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
          </motion.div>
        </div>
      </section>

      {/* ═══ PRICING — second screen ═══ */}
      <section id="pricing" className="px-5 py-10 md:py-14">
        <div className="max-w-[480px] mx-auto text-center">
          <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-2">
            Подписка на месяц
          </p>
          <p className="text-4xl md:text-5xl font-display font-bold tracking-tight mb-1">
            990 ₽ <span className="text-lg font-normal text-muted-foreground">— первый месяц</span>
          </p>
          <p className="text-[10px] text-muted-foreground mb-1">
            далее 1500 ₽/мес · отмена в любой момент
          </p>
          <p className="text-[10px] text-muted-foreground/70 mb-5">
            Доступ к чату через Telegram‑бота, сразу после оплаты
          </p>
          <a
            href={telegramLink}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity"
          >
            Вступить в чат
          </a>
        </div>
      </section>

      {/* ═══ WHAT'S INSIDE — chat screenshots ═══ */}
      <section id="what-inside" className="px-5 py-12 md:py-16 border-t border-border">
        <div className="max-w-[600px] mx-auto">
          <p className="text-[9px] tracking-[0.25em] uppercase text-muted-foreground mb-6">
            Что в чате?
          </p>
          <div className="flex gap-3 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-hide">
            {chatScreenshots.map((src, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="shrink-0 w-[260px] snap-center"
              >
                <img
                  src={src}
                  alt={`Скриншот из чата ${i + 1}`}
                  className="w-full aspect-[9/16] object-cover rounded-lg bg-muted"
                />
              </motion.div>
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
            {(faqItems as Array<{ q: string; a: string }>).map((item, i) => (
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
            href={telegramLink}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3.5 bg-foreground text-background text-[10px] tracking-[0.18em] uppercase rounded-full hover:opacity-85 transition-opacity mb-3"
          >
            Вступить в чат
          </a>
          <a
            href={contactLink}
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
