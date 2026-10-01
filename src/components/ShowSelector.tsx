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
        <div className="relative px-6 pt-10 pb-14 max-w-4xl mx-auto">
          {/* Language switcher */}
          <div className="absolute top-4 right-4">
            <LanguageSwitcher />
          </div>

          <BilingualText
            i18nKey="app.name"
            as="div"
            className="text-4xl sm:text-5xl font-bold text-primary-900 tracking-tight"
            zhClassName="text-primary-600"
          />
          <BilingualText
            i18nKey="app.subtitle"
            as="div"
            className="mt-2 text-base text-primary-600 font-medium"
            zhClassName="text-primary-500"
          />
        </div>
      </header>

      {/* Show grid */}
      <section className="max-w-4xl mx-auto px-4 -mt-6 sm:px-6 pb-10">
        <div className="bg-white rounded-2xl shadow-card border border-border-light p-6">
          <div className="text-sm font-semibold text-primary-700 flex items-center gap-2 mb-1">
            <span className="w-1 h-4 bg-accent-600 rounded-full inline-block" />
            <Bi i18nKey="show.title" />
          </div>
          <p className="text-xs text-primary-500 mb-5">
            <Bi i18nKey="show.subtitle" />
          </p>

          {sortedLangs.map((lang) => {
            const shows = grouped[lang]
            return (
            <div key={lang} className="mb-6 last:mb-0">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-base">{LANG_FLAGS[lang]}</span>
                <span className="text-sm font-semibold text-primary-700">
                  <Bi i18nKey={lang === 'en' ? 'show.english' : 'show.spanish'} />
                </span>
                <div className="flex-1 h-px bg-border-light" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {shows.map((show) => (
                  <button
                    key={show.id}
                    onClick={() => onSelectShow(show.id)}
                    className="group relative text-left rounded-xl border border-border-light hover:border-accent-300 shadow-subtle hover:shadow-card transition-all overflow-hidden bg-white"
                  >
                    {/* Cover */}
                    <div className={`h-24 bg-surface-secondary flex items-center justify-center relative`}>
                      <span className="text-4xl">{show.coverEmoji}</span>
                      <span className="absolute top-2 right-2 px-2 py-0.5 rounded-full bg-primary-100 text-primary-600 text-[10px] font-medium">
                        {show.episodes.length} <Bi i18nKey="show.episodes" />
                      </span>
                    </div>

                    {/* Info */}
                    <div className="p-4">
                      <BilingualText
                        i18nKey={show.titleKey}
                        as="div"
                        className="font-semibold text-primary-900 group-hover:text-accent-600 transition"
                        zhClassName="text-primary-500"
                      />
                      <p className="mt-1.5 text-xs text-primary-600 leading-relaxed line-clamp-2">
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

      <footer className="py-8 text-center text-xs text-primary-400">
        <Bi i18nKey="app.footer" values={{ year: new Date().getFullYear() }} />
      </footer>
    </div>
  )
}
