export const en = {
    home: {
        title: 'Postoperative Complication Risk Assessment System for Oral Surgery Patients',
        subtitle: 'Faculty of Dentistry, Chulalongkorn University',
        startForm: {
            title: 'Fill in the Form',
            description: 'Patients can report their postoperative symptoms through a question form, which takes less than 10 minutes to complete.',
            button: 'Start the form →'
        },
        upload: {
            title: 'Upload CSV',
            description: 'Deprecated',
            button: 'Upload file →'
        },
        info: {
            title: 'About the System',
            list: [
                'Assesses complication risk in patients after oral surgery',
                'Classifies complication risk levels: High, Miderate, Complicated, Low',
                'Provides self-care advice based on the risk level'
            ]
        }
    },
    form: {
        backHome: 'Home',
        back: 'Back',
        clear: 'Clear data',
        next: 'Next',
        submit: 'Submit and assess risk',
        submitting: 'Saving...',
        title: 'Fill in patient information',
        steps: {
            basicInfo: 'Basic information',
            symptoms: 'Symptoms',
            dailyLife: 'Daily activities',
            description: {
                1: 'Section 1',
                2: 'Section 2',
                3: 'Section 3'
            }
        },
        savedDataFound: 'Saved data found. Your responses are automatically saved as you fill in the form.',
        confirmClear: 'Are you sure you want to clear all saved data?',
        validationError: 'Please complete all required fields',

        basicInfo: {
            title: 'Section 1: Basic Information',
            firstName: 'First Name',
            lastName: 'Last Name',
            email: 'Email',
            phone: 'Phone Number',
            birthYear: 'Birth Year (B.E.)',
            age: 'Age',
            gender: 'Gender',
            genderOptions: {
                male: 'Male',
                female: 'Female'
            },
            genderOther: 'Other: Please specify',
            hn: 'Hospital Number (HN)',
            procedures: 'Procedure(s) performed (multiple answers allowed)',
            subOptions: 'Select additional details',
            surgicalTooth: 'Surgical removal of tooth',
            otherProcedures: 'Other procedures',
            otherProceduresPlaceholder: 'please specify the procedure',
            addProcedure: 'Click to add other procedures',
            specialProcedures: 'Special Procedures',
            imfWire: 'IMF Wire',
            imfElastic: 'IMF Elastic',
            procedureOptions: {
                lefort: 'Maxillary surgery (Le Fort I osteotomy)',
                bssro: 'Mandibular surgery (BSSRO – Bilateral Sagittal Split Osteotomy)',
                surgicalRemoval: 'Surgical removal of tooth',
                extraction: 'Tooth extraction',
                biopsy: 'Biopsy',
                cyst: 'Cyst enucleation',
                incision: 'Incision and drainage',
                cleftRepair: 'Repair of alveolar cleft with iliac crest bone graft',
                torectomy: 'Torectomy',
                plateRemoval: 'Off plates and screws'
            },
            loops: 'Number of loops',
            icbg: 'Repair of alveolar cleft with iliac crest bone graft',
            icbgDesc: 'Details',
            ngTube: 'NG Tube',
            ngTubeDesc: 'Details',
            surgeryDate: 'Date of surgery',
            dischargeDate: 'Discharge Date',
            note: 'Special notes (for clinician use)'
        },

        symptoms: {
            title: 'Section 2: Symptoms',
            pain: {
                label: 'Current pain level (Pain score)',
                min: 'No pain at all',
                max: 'Worst pain imaginable',
                desc: 'Please select your pain level.'
            },
            painMed: {
                label: 'Did the pain get better after taking the pain medication?',
                better: 'Improved',
                notBetter: 'Not improved',
                notTaken: 'Not taken yet'
            },
            swelling: {
                label: 'Swelling',
                desc: 'Additional details (optional): location of swelling',
                gone: 'Swelling has completely gone',
                reduced: 'Reduced swelling',
                noChange: 'No change in swelling',
                increased: 'Increased swelling',
                severe: 'Severely increased swelling affecting daily activities'
            },
            breathing: {
                label: 'Do you have any difficulty breathing or swallowing?',
                no: 'No',
                yes: 'Yes'
            },
            bleeding: {
                label: 'Bleeding or oozing from a wound in the mouth or nose',
                no: 'No bleeding or oozing',
                slight: 'Slight oozing that stops by itself',
                heavy: 'Heavy bleeding with bright red blood that does not stop',
                desc: 'Additional details (optional): Location of bleeding/oozing'
            },
            fever: {
                label: 'Fever',
                no: 'No fever',
                yes: 'Fever (higher than 38°C)',
                desc: 'Additional details (optional): Body temperature'
            },
            numbness: {
                label: 'Numbness',
                desc: 'Additional details (optional): Please specify the area of numbness, e.g., numbness of the right lower lip.',
                resolved: 'Numbness has completely resolved after the procedure',
                improving: 'Still numb, but gradually improving',
                unchanged: 'Numbness feels the same as immediately after the procedure'
            },
            phlebitis: {
                label: 'Area where the IV needle was removed (back of the hand or wrist)',
                no: 'No pain, swelling, or redness around the needle site',
                yes: 'Pain, swelling, or redness around the needle site'
            },
            suture: {
                label: 'Stitches',
                secure: 'Stitches are secure / not noticed',
                loose: 'Some stitches have fallen out, but no bleeding',
                bleeding: 'Some stitches have fallen out, with ongoing bright red bleeding'
            },
            other: {
                label: 'Other symptoms (multiple answers allowed)',
                customLabel: 'Other symptoms:',
                namePlaceholder: 'Symptom',
                descPlaceholder: 'Description',
                add: 'Click to add other symptoms'
            },
            antibiotic: {
                label: 'Have you taken your antibiotics as prescribed?',
                all: 'Taken all doses as prescribed',
                missed: 'Missed some doses',
                none: 'Did not take the medication at all',
                forgotCount: 'Number of times forgotten'
            },
            compress: {
                label: 'Are you using a cold or warm compression?',
                cold: 'Cold compression',
                warm: 'Warm compression',
                none: 'Not using any compression'
            },
            imfWire: {
                label: 'Are your upper and lower teeth tied together so you cannot open your mouth? (IMF)',
                no: 'No jaw wiring',
                yes: 'Jaw wiring present',
                tight: 'Tight',
                loose: 'Loose (slight opening)',
                broken: 'Broken elastic (cannot open)'
            },
            walking: {
                label: 'Walking ability (for patients who had alveolar cleft repair using a hip bone graft)',
                na: 'Did not undergo alveolar cleft repair with hip bone graft',
                normal: 'Able to walk normally',
                difficult: 'Difficulty walking'
            }
        },

        dailyLife: {
            title: 'Section 3: Daily Activities',
            brushing: {
                label: 'Tooth brushing',
                desc: 'Additional description (Optional)',
                good: 'Able to brush teeth well',
                difficult: 'Difficulty brushing teeth'
            },
            rinsing: {
                label: 'Rinsing with mouthwash',
                good: 'Able to rinse mouth',
                difficult: 'Difficulty rinsing mouth',
                none: 'Not using mouthwash'
            },
            foodTypes: {
                label: 'Current type of food (multiple answers allowed)',
                other: 'Other',
                liquid: 'Clear liquid foods e.g., clear soup, strained fruit juice, milk',
                pureed: 'Blended / Pureed foods e.g., blended porridge, blended chicken',
                soft: 'Soft foods, e.g., porridge, soft rice, soft-boiled egg, steamed vegetables',
                regular: 'Regular foods, avoiding spicy, hot, hard, or sticky foods'
            },
            foodAmount: {
                label: 'Amount of food eaten',
                desc: 'Additional description (Optional)',
                normal: 'Eating a normal amount',
                less: 'Eating less than usual'
            },
            questions: {
                label: 'Do you have any questions for the nurse?',
                placeholder: 'Enter any questions or concerns you would like to ask'
            },
            ngTube: {
                label: 'Feeding tube position',
                secure: 'Feeding tube is in the same position; nasal tape is secure and not loose',
                loose: 'Feeding tube has moved or the tape is loose'
            },
            readySubmit: {
                title: 'Ready to submit',
                desc: 'Please review your information before clicking "Submit and assess risk". The system will analyze your responses and provide advice based on your assessed risk level.'
            }
        }
    },
    common: {
        yes: 'Yes',
        no: 'No',
        notSpecified: 'Not Specified',
        none: 'None',
        unknown: 'Unknown'
    },
    result: {
        title: 'Risk Assessment Result',
        header: {
            back: 'Back to Home',
            assessmentDate: 'Assessment Date',
            download: 'Download Report'
        },
        loading: {
            title: 'Processing Data...',
            subtitle: 'AI is analyzing your data, this may take 10-30 seconds.'
        },
        error: {
            title: 'Error Occurred',
            retry: 'Return to Edit Form'
        },
        summary: {
            title: 'Assessment Summary',
            saved: 'Data Saved - Assessment results have been recorded.',
            note: 'Note: System could assess only {count} out of 17 flows.',
            critical: 'Critical Issues Needing Attention:',
            aiSummaryBox: 'Assessment Summary'
        },
        riskLevels: {
            high: 'High Risk',
            medium: 'Moderate Risk',
            low: 'Low Risk',
            complex: 'Complex Condition - Cannot Conclude Risk Level'
        },
        qa: {
            title: 'Answers to Your Questions'
        },
        dataPreview: {
            title: 'Submitted Data',
            count: '{count} items'
        },
        actions: {
            nextSteps: 'Next Steps',
            contactDoctor: 'Contact Medical Team Immediately',
            contactDoctorDesc: 'High risk detected in some areas. Please contact a doctor or nurse for consultation and appropriate treatment.',
            monitor: 'Monitor Symptoms Closely',
            monitorDesc: 'Moderate risk detected. Recommend monitoring symptoms and following instructions. If symptoms do not improve, see a doctor.',
            normal: 'Symptoms within Normal Range',
            normalDesc: 'Low risk. Recommended to follow self-care instructions and continue monitoring.',
            assessAgain: 'Assess Again',
            share: 'Share Result'
        },
        disclaimer: 'Note: This assessment is preliminary information only. It does not replace diagnosis or advice from a medical professional. If you have doubts or abnormal symptoms, please consult a doctor.'
    }
};
