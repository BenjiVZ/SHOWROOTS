// Anti-desintermediación scanner — espejo del módulo Python en backend/bookings/anti_disinter.py
// Mantener sincronizado: cualquier patrón nuevo aquí debe replicarse en Python.

export const PATTERNS = {
  phone:      /(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}/g,
  email:      /[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/g,
  username_at:/@[A-Za-z0-9_.]{3,}/g,
  whatsapp:   /\b(?:whats?app|wsp|wpp|wa\.me)\b/gi,
  call_me:    /\b(?:ll[aá]mame|c[oó]ntactame|escr[ií]beme|tel(?:[eé]fono)?|movil|celular|m[oó]vil)\b/gi,
  social:     /\b(?:instagram|insta|facebook|fb|tiktok|telegram|signal|twitter|x\.com)\b/gi,
  url:        /(?:https?:\/\/|www\.)\S+/gi,
}

export const CATEGORY_LABELS = {
  phone: 'Número de teléfono',
  email: 'Email',
  username_at: 'Usuario (@)',
  whatsapp: 'WhatsApp',
  call_me: 'Solicitud de contacto directo',
  social: 'Red social',
  url: 'URL externa',
}

export const MASK = '***'

export function scan(text) {
  if (!text) return []
  const findings = []
  for (const [category, pattern] of Object.entries(PATTERNS)) {
    // Reset lastIndex porque son /g
    pattern.lastIndex = 0
    const matches = text.match(pattern)
    if (matches) {
      matches.forEach(m => findings.push({ category, match: m }))
    }
  }
  return findings
}

export function sanitize(text) {
  if (!text) return { clean: text, findings: [] }
  const findings = scan(text)
  let clean = text
  for (const pattern of Object.values(PATTERNS)) {
    pattern.lastIndex = 0
    clean = clean.replace(pattern, MASK)
  }
  return { clean, findings }
}

export function hasViolations(text) {
  return scan(text).length > 0
}

// Helper para mostrar warning humano
export function violationsMessage(findings) {
  if (!findings.length) return ''
  const categories = [...new Set(findings.map(f => CATEGORY_LABELS[f.category] || f.category))]
  return `No se permite compartir: ${categories.join(', ')}. Toda comunicación va por Pulsar.`
}
