#!/bin/bash

# Fix PROCEDURE_OPTIONS type assertions
sed -i '' 's/PROCEDURE_OPTIONS\.includes(p)/PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])/g' components/forms/BasicInfoForm.tsx

# Fix OTHER_SYMPTOMS_OPTIONS type assertions  
sed -i '' 's/OTHER_SYMPTOMS_OPTIONS\.includes(s)/OTHER_SYMPTOMS_OPTIONS.includes(s as typeof OTHER_SYMPTOMS_OPTIONS[number])/g' components/forms/SymptomsForm.tsx

echo "Type assertions fixed"
