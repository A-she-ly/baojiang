import { useTranslation } from 'react-i18next'
import { SHOWS } from '../data/shows'
import type { ShowDefinition } from '../data/showTypes'
import LanguageSwitcher from './LanguageSwitcher'
import BilingualText, { Bi } from './BilingualText'

interface Props {
  onSelectShow: (showId: string) => void
}

const LANG_FLAGS: Record<string, string> = { en: '🇺🇸', es: '🇪🇸' }

export default function ShowSelector({ onSelectShow }: Props) {
  const { t, i18n } = useTranslation()

  // Group shows by language, current language's shows first
  const currentLang = i18n.language as string
  const grouped = SHOWS.reduce<Record<string, ShowDefinition[]>>((acc, show) => {
    const lang = show.language
    if (!acc[lang]) acc[lang] = []
    acc[lang].push(show)
    return acc
  }, {} as Record<string, ShowDefinition[]>)

  // Sort: current language group first
  const sortedLangs = Object.keys(grouped).sort((a, b) => {
    if (a === currentLang) return -1
    if (b === currentLang) return 1
    return 0
  })

  return (
    <div className="min-h-full">
      {/* Header */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-friends-sofa via-friends-coffee to-friends-sofa opacity-90" />
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage:
            "radial-gradient(circle at 20% 20%, #FFB74D 0, transparent 40%), radial-gradient(circle at 80% 60%, #FFF8E1 0, transparent 35%)",
        }} />
        <div className="relative px-6 pt-10 pb-14 text-white max-w-4xl mx-auto">
          {/* Language switcher */}
          <div className="absolute top-4 right-4">
            <LanguageSwitcher />
          </div>

          <BilingualText
            i18nKey="app.name"
            as="div"
            className="font-hand text-5xl sm:text-6xl text-friends-cream drop-shadow-md"
            zhClassName="text-friends-cream/80"
          />
          <BilingualText
            i18nKey="app.subtitle"
            as="div"
            className="mt-1 text-lg text-friends-accent/90 font-medium tracking-wide"
            zhClassName="text-friends-accent/70"
          />
        </div>
      </header>

      {/* Show grid */}
      <section className="max-w-4xl mx-auto px-4 -mt-6 sm:px-6 pb-10">
        <div className="bg-white rounded-2xl shadow-card border border-friends-coffee/10 p-6">
          <div className="text-sm font-semibold text-friends-sofa/80 flex items-center gap-2 mb-1">
            <span className="w-1 h-4 bg-friends-perk rounded-full inline-block" />
            <Bi i18nKey="show.title" />
          </div>
          <p className="text-xs text-friends-coffee/70 mb-5">
            <Bi i18nKey="show.subtitle" />
          </p>

          {sortedLangs.map((lang) => {
            const shows = grouped[lang]
            return (
            <div key={lang} className="mb-6 last:mb-0">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-base">{LANG_FLAGS[lang]}</span>
                <span className="text-sm font-semibold text-friends-sofa">
                  <Bi i18nKey={lang === 'en' ? 'show.english' : 'show.spanish'} />
                </span>
                <div className="flex-1 h-px bg-friends-coffee/10" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {shows.map((show) => (
                  <button
                    key={show.id}
                    onClick={() => onSelectShow(show.id)}
                    className="group relative text-left rounded-xl border border-friends-coffee/10 hover:border-friends-perk/40 shadow-sm hover:shadow-card transition-all overflow-hidden"
                  >
                    {/* Cover gradient */}
                    <div className={`h-28 bg-gradient-to-br ${show.accentFrom} ${show.accentTo} flex items-center justify-center relative`}>
                      <span className="text-5xl drop-shadow-md">{show.coverEmoji}</span>
                      <span className="absolute top-2 right-2 px-2 py-0.5 rounded-full bg-black/30 backdrop-blur text-white text-[10px] font-medium">
                        {show.episodes.length} <Bi i18nKey="show.episodes" />
                      </span>
                    </div>

                    {/* Info */}
                    <div className="p-3.5 bg-white">
                      <BilingualText
                        i18nKey={show.titleKey}
                        as="div"
                        className="font-semibold text-friends-sofa group-hover:text-friends-perk transition"
                        zhClassName="text-friends-coffee/50"
                      />
                      <p className="mt-1 text-xs text-friends-coffee/80 leading-relaxed line-clamp-2">
                        <Bi i18nKey={show.descKey} />
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
            )
          })}
        </div>
      </section>

      <footer className="py-8 text-center text-xs text-friends-coffee/60">
        <Bi i18nKey="app.footer" values={{ year: new Date().getFullYear() }} />
      </footer>
    </div>
  )
}
