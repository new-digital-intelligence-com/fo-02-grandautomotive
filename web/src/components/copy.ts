export type UiLanguage = "el" | "en";

/** Every text on the page, in Greek (default) and English. The language also sets the language of the next call. */
const el = {
  brandTagline: "Renault · Dacia στην Ελλάδα",
  demoBadge: "Δοκιμαστική έκδοση",
  title: "Μιλήστε με την Κατερίνα, την ψηφιακή βοηθό της Grand Automotive",
  subtitle:
    "Ρωτήστε για μοντέλα και τιμές Renault και Dacia, την πλησιέστερη αντιπροσωπεία, την εγγύηση ή τις προσφορές, στα ελληνικά ή στα αγγλικά.",
  start: "Έναρξη κλήσης",
  end: "Τερματισμός κλήσης",
  mute: "Σίγαση μικροφώνου",
  unmute: "Ενεργοποίηση μικροφώνου",
  statusIdle: "Πατήστε «Έναρξη κλήσης» και μιλήστε φυσικά",
  statusConnecting: "Σύνδεση με την Κατερίνα…",
  statusListening: "Η Κατερίνα σας ακούει…",
  statusSpeaking: "Η Κατερίνα μιλάει…",
  statusMuted: "Το μικρόφωνο είναι σε σίγαση",
  callLimit: "Χωρίς εγγραφή. Κάθε κλήση διαρκεί έως 10 λεπτά.",
  micError: "Επιτρέψτε στο πρόγραμμα περιήγησης να χρησιμοποιήσει το μικρόφωνο για να μιλήσετε με την Κατερίνα.",
  startError: "Η κλήση δεν ξεκίνησε. Δοκιμάστε ξανά.",
  tooManyCalls: "Ξεκινήσατε αρκετές κλήσεις σε λίγο χρόνο. Δοκιμάστε ξανά σε λίγα λεπτά.",
  transcriptTitle: "Η συνομιλία",
  transcriptEmpty: "Ό,τι λέτε εσείς και η Κατερίνα εμφανίζεται εδώ κατά τη διάρκεια της κλήσης.",
  you: "Εσείς",
  agent: "Κατερίνα",
  tryTitle: "Δοκιμάστε να ρωτήσετε",
  tryQuestions: [
    "Πόσο κοστίζει το νέο Renault Clio;",
    "Πού είναι η πλησιέστερη αντιπροσωπεία Dacia στη Θεσσαλονίκη;",
    "Τι εγγύηση έχει ένα καινούργιο Dacia Duster;",
    "Τι είναι το Eco-G και πόσο οικονομικό είναι;",
    "Ποια ηλεκτρικά Renault υπάρχουν και με τι επιδότηση;",
    "Where can I see Renault at Auto Athina 2026?",
  ],
  helpTitle: "Η Κατερίνα σας βοηθά με",
  help: [
    "Μοντέλα, κινητήρες και τιμές Renault και Dacia",
    "Την πλησιέστερη αντιπροσωπεία ή το πλησιέστερο service",
    "Εγγύηση, service και οδική βοήθεια",
    "Προσφορές, χρηματοδότηση και επιδοτήσεις ηλεκτρικών",
    "INEOS Grenadier, Alpine και τον όμιλο Grand Automotive",
  ],
  brandsTitle: "Η Grand Automotive στην Ελλάδα",
  brands: "Renault · Dacia · INEOS · Alpine (από το 2027)",
  footer:
    "Δοκιμαστική εφαρμογή της NDI (New Digital Intelligence). Δεν είναι επίσημη ιστοσελίδα της Grand Automotive. Τιμές και προσφορές: renault.gr, dacia.gr και το εξουσιοδοτημένο δίκτυο.",
  languageLabel: "Γλώσσα κλήσης",
};

export type Copy = typeof el;

const en: Copy = {
  brandTagline: "Renault · Dacia in Greece",
  demoBadge: "Demo",
  title: "Talk to Katerina, Grand Automotive's voice assistant",
  subtitle:
    "Ask about Renault and Dacia models and prices, the nearest dealer, the warranty or current offers, in English or in Greek.",
  start: "Start the call",
  end: "End the call",
  mute: "Mute microphone",
  unmute: "Unmute microphone",
  statusIdle: "Press “Start the call” and just talk",
  statusConnecting: "Connecting to Katerina…",
  statusListening: "Katerina is listening…",
  statusSpeaking: "Katerina is speaking…",
  statusMuted: "Microphone muted",
  callLimit: "No sign-up needed. Calls last up to 10 minutes.",
  micError: "Please allow microphone access to talk with Katerina.",
  startError: "The call could not start. Please try again.",
  tooManyCalls: "You have started several calls in a short time. Please try again in a few minutes.",
  transcriptTitle: "Call transcript",
  transcriptEmpty: "What you and Katerina say appears here during the call.",
  you: "You",
  agent: "Katerina",
  tryTitle: "Try asking",
  tryQuestions: [
    "How much is the new Renault Clio?",
    "Where is the nearest Dacia dealer in Thessaloniki?",
    "What warranty does a new Dacia Duster have?",
    "What is Eco-G, and how much does it save?",
    "Which Renault electric cars are there, and with what subsidy?",
    "Πού θα δω τη Renault στην Auto Athina 2026;",
  ],
  helpTitle: "Katerina can help with",
  help: [
    "Renault and Dacia models, engines and prices",
    "The nearest dealer or service point",
    "Warranty, service and roadside assistance",
    "Offers, financing and electric car subsidies",
    "INEOS Grenadier, Alpine and the Grand Automotive group",
  ],
  brandsTitle: "Grand Automotive in Greece",
  brands: "Renault · Dacia · INEOS · Alpine (from 2027)",
  footer:
    "Demo by NDI (New Digital Intelligence). Not an official Grand Automotive website. Prices and offers: renault.gr, dacia.gr and the authorised dealers.",
  languageLabel: "Call language",
};

export const COPY: Record<UiLanguage, Copy> = { el, en };
