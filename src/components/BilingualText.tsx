import { useTranslation } from 'react-i18next'
import type { ReactNode } from 'react'

interface BilingualTextProps {
  i18nKey: string
  values?: Record<string, string | number>
  className?: string
  zhClassName?: string
  as?: 'div' | 'span' | 'p' | 'h1' | 'h2' | 'h3'
}

/**
 * Renders bilingual text: target language (main) + Chinese (zh) as auxiliary.
 * The Chinese text is displayed smaller and lighter below the main text.
 */
export default function BilingualText({
  i18nKey,
  values = {},
  className = '',
  zhClassName = '',
  as: Tag = 'div',
}: BilingualTextProps) {
  const { t, i18n } = useTranslation()

  // Get the raw translation object
  const raw = t(i18nKey, { ...values, returnObjects: true }) as { main?: string; zh?: string } | string

  // Fallback: if it's a plain string (no zh), just render it
  if (typeof raw === 'string') {
    return <Tag className={className}>{raw}</Tag>
  }

  const mainText = raw.main ?? i18nKey
  const zhText = raw.zh ?? ''

  // For inline elements, render side by side
  if (Tag === 'span') {
    return (
      <span className={className}>
        {mainText}
        {zhText && (
          <span className={`text-friends-coffee/60 text-xs ml-1.5 ${zhClassName}`}>
            {zhText}
          </span>
        )}
      </span>
    )
  }

  // For block elements, render zh on a new line below
  return (
    <Tag className={className}>
      {mainText}
      {zhText && (
        <div className={`text-friends-coffee/60 text-xs mt-0.5 ${zhClassName}`}>
          {zhText}
        </div>
      )}
    </Tag>
  )
}

/**
 * Helper: get bilingual text as a ReactNode for use inside other elements.
 * Returns main text + zh text in a compact inline format.
 */
export function Bi({ i18nKey, values }: { i18nKey: string; values?: Record<string, string | number> }) {
  const { t } = useTranslation()
  const raw = t(i18nKey, { ...values, returnObjects: true }) as { main?: string; zh?: string } | string

  if (typeof raw === 'string') return <>{raw}</>

  return (
    <>
      {raw.main}
      {raw.zh && <span className="text-friends-coffee/50 text-[11px] ml-1">{raw.zh}</span>}
    </>
  )
}
