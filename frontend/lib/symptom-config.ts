import { th } from '@/lib/locales'

const s = th.form.symptoms
const d = th.form.dailyLife

/**
 * Canonical ordered list of symptom_values fields for display.
 * Single source of truth — derived from locale labels.
 * Add new fields here to control order and label in the patient detail panel.
 */
export const SYMPTOM_FIELDS: { key: string; label: string }[] = [
  { key: 'pain_score',                         label: s.pain.label },
  { key: 'pain_description',                   label: s.pain.desc },
  { key: 'pain_medication_effect',             label: s.painMed.label },
  { key: 'swelling_status',                    label: s.swelling.label },
  { key: 'breathing_or_swallowing_difficulty', label: s.breathing.label },
  { key: 'bleeding_status',                    label: s.bleeding.label },
  { key: 'fever_status',                       label: s.fever.label },
  { key: 'numbness_status',                    label: s.numbness.label },
  { key: 'phlebitis',                          label: s.phlebitis.label },
  { key: 'suture_status',                      label: s.suture.label },
  { key: 'other_symptoms',                     label: s.other.label },
  { key: 'antibiotic_compliance',              label: s.antibiotic.label },
  { key: 'compress_type',                      label: s.compress.label },
  { key: 'imf_wire_status',                    label: s.imfWire.label },
  { key: 'walking_status',                     label: s.walking.label },
  { key: 'brushing_teeth',                     label: d.brushing.label },
  { key: 'mouth_rinsing',                      label: d.rinsing.label },
  { key: 'food_types',                         label: d.foodTypes.label },
  { key: 'food_amount',                        label: d.foodAmount.label },
  { key: 'ng_tube_position',                   label: d.ngTube.label },
]

/** Keys to never show in the symptom grid (shown separately or are raw objects) */
export const SYMPTOM_SKIP_KEYS = new Set([
  'other_symptoms_custom',
  'food_types_custom',
])

/** Map from key → label for O(1) lookup */
export const SYMPTOM_LABEL_MAP: Record<string, string> = Object.fromEntries(
  SYMPTOM_FIELDS.map(({ key, label }) => [key, label])
)
