#!/bin/bash

# Fix all radio button type assertions in SymptomsForm
sed -i '' 's/onChange({ pain_medication_effective: e.target.value })/onChange({ pain_medication_effective: e.target.value as typeof data.pain_medication_effective })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ swelling_status: e.target.value })/onChange({ swelling_status: e.target.value as typeof data.swelling_status })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ bleeding_status: e.target.value })/onChange({ bleeding_status: e.target.value as typeof data.bleeding_status })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ numbness_status: e.target.value })/onChange({ numbness_status: e.target.value as typeof data.numbness_status })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ phlebitis: e.target.value })/onChange({ phlebitis: e.target.value as typeof data.phlebitis })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ suture_status: e.target.value })/onChange({ suture_status: e.target.value as typeof data.suture_status })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ antibiotic_compliance: e.target.value })/onChange({ antibiotic_compliance: e.target.value as typeof data.antibiotic_compliance })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ compress_type: e.target.value })/onChange({ compress_type: e.target.value as typeof data.compress_type })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ has_imf: e.target.value })/onChange({ has_imf: e.target.value as typeof data.has_imf })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ imf_wire_status: e.target.value })/onChange({ imf_wire_status: e.target.value as typeof data.imf_wire_status })/g' components/forms/SymptomsForm.tsx

sed -i '' 's/onChange({ walking_status: e.target.value })/onChange({ walking_status: e.target.value as typeof data.walking_status })/g' components/forms/SymptomsForm.tsx

# Fix DailyLifeForm
sed -i '' 's/onChange({ feeding_method: e.target.value })/onChange({ feeding_method: e.target.value as typeof data.feeding_method })/g' components/forms/DailyLifeForm.tsx

sed -i '' 's/onChange({ food_amount: e.target.value })/onChange({ food_amount: e.target.value as typeof data.food_amount })/g' components/forms/DailyLifeForm.tsx

sed -i '' 's/onChange({ ng_tube_position: e.target.value })/onChange({ ng_tube_position: e.target.value as typeof data.ng_tube_position })/g' components/forms/DailyLifeForm.tsx

echo "Radio button types fixed"
