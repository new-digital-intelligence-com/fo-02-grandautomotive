"""Builds the Grand Automotive (Greece) knowledge base PDFs for the Greek voice agent.

Facts come from public sources saved under ../research: grandautomotive.eu, renault.gr, dacia.gr, the official Renault and
Dacia dealer locators (../research/dealers_*.json, see collect_dealers.py), Taavura's site, the Grand Automotive Central
Europe LinkedIn page and Greek motoring press (INEOS Grenadier, Alpine). The PDFs are in Greek, the language the agent
speaks; model and brand names stay in Latin letters, as on the official sites. Greek text extracts cleanly from these
PDFs (checked with pypdf).

Usage: python build_knowledge_base.py   -> writes the PDFs next to this file
"""
import json
import os
import re
import unicodedata

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.join(HERE, "..", "research")
CHECKED = "5 Οκτωβρίου 2026"

# Arial has the Greek letters.
pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial", boldItalic="Arial-Bold")

INK = colors.HexColor("#1c1b1a")
COPPER = colors.HexColor("#a85a24")
GREY = colors.HexColor("#5f5a55")

S = {
    "title": ParagraphStyle("title", fontName="Arial-Bold", fontSize=19, leading=23, textColor=INK, spaceAfter=4),
    "subtitle": ParagraphStyle("subtitle", fontName="Arial", fontSize=10.5, leading=14, textColor=GREY, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=14, leading=18, textColor=INK, spaceBefore=12, spaceAfter=5),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=11.5, leading=15, textColor=COPPER, spaceBefore=8, spaceAfter=3),
    "body": ParagraphStyle("body", fontName="Arial", fontSize=10, leading=13.5, alignment=TA_LEFT, spaceAfter=4),
    "note": ParagraphStyle("note", fontName="Arial", fontSize=9, leading=12, textColor=GREY, spaceAfter=4),
    "cell": ParagraphStyle("cell", fontName="Arial", fontSize=8.8, leading=11.2),
    "cellb": ParagraphStyle("cellb", fontName="Arial-Bold", fontSize=8.8, leading=11.2, textColor=colors.white),
    "q": ParagraphStyle("q", fontName="Arial-Bold", fontSize=10, leading=13.5, textColor=INK, spaceBefore=7, spaceAfter=1),
    "dealer": ParagraphStyle("dealer", fontName="Arial", fontSize=9.6, leading=12.8, spaceAfter=5, leftIndent=8),
}


def esc(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def bullets(items: list[str]) -> ListFlowable:
    return ListFlowable([ListItem(P(i), leftIndent=12, value="•") for i in items], bulletType="bullet", start="•", leftIndent=12,
                        bulletFontSize=9)


def table(header: list[str], rows: list[list[str]], widths: list[float]) -> Table:
    data = [[P(h, "cellb") for h in header]] + [[P(c, "cell") for c in row] for row in rows]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d6cfc4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f2ea")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def qa(pairs: list[tuple[str, str]]) -> list:
    return [KeepTogether([P(q, "q"), P(a)]) for q, a in pairs]


def header(title: str, subtitle: str) -> list:
    return [
        P(title, "title"),
        P(subtitle, "subtitle"),
        P(f"Συγκεντρωμένα στοιχεία από δημόσιες πηγές (grandautomotive.eu, renault.gr, dacia.gr, επίσημα δελτία τύπου), "
          f"έλεγχος στις {CHECKED}. Τιμές, προσφορές και ωράρια αλλάζουν: το εξουσιοδοτημένο δίκτυο ή η εξυπηρέτηση πελατών "
          "τα επιβεβαιώνει. Όπου γράφει <b>Γενική πρακτική</b>, πρόκειται για συνήθη πρακτική της αγοράς και όχι για "
          "δημοσιευμένο όρο της εταιρείας.", "note"),
    ]


def build(filename: str, story: list, title: str) -> None:
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Arial", 7.5)
        canvas.setFillColor(GREY)
        canvas.drawString(18 * mm, 10 * mm, f"Grand Automotive – {title}")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Σελίδα {doc.page}")
        canvas.restoreState()

    path = os.path.join(HERE, filename)
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                            title=f"Grand Automotive – {title}", author="Grand Automotive knowledge base (NDI demo)")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("wrote", path)


# ---------------------------------------------------------------- shared facts

CUSTOMER_CARE = "+30 214 444 46 40"
CUSTOMER_CARE_HOURS = "Δευτέρα έως Παρασκευή, 09:00–17:00"
HQ = "12ο χλμ. Νέας Εθνικής Οδού Αθηνών – Λαμίας (4ος όροφος), 144 52 Μεταμόρφωση Αττικής"
RNLT_ATHENS = ("rnlt© Athens (concept store της Renault, GA Motors): Σκουφά 8, Κολωνάκι, 106 73 Αθήνα (μετρό Σύνταγμα ή "
               "Ευαγγελισμός). Τηλέφωνο +30 214 411 10 49, e-mail rnlt@ga-motors.gr. Ωράριο: Δευτέρα και Τετάρτη 10:00–18:00, "
               "Τρίτη, Πέμπτη και Παρασκευή 10:00–20:00, Σάββατο 10:00–15:00, Κυριακή κλειστά.")
AUTO_ATHINA = ("Auto Athina 2026: Metropolitan Expo, 3–11 Οκτωβρίου 2026. Ωράριο έκθεσης: Δευτέρα–Παρασκευή 14:00–21:00, "
               "Σάββατο–Κυριακή 10:00–21:00. Renault: Hall 3, Stand A1. Dacia: Hall 4, Stand B4.")


# ---------------------------------------------------------------- 01 company


def doc_company() -> None:
    markets = [
        ("Κροατία", "Renault, Dacia, MG, Nissan, Ford, Chery, Hyundai, Maxus, Omoda, Jaecoo, Ineos"),
        ("Σλοβενία", "Renault, Dacia, Nissan, MG, Ineos, Chery, Omoda, Jaecoo, Alpine, Maxus"),
        ("Σερβία", "MG, Nissan, Chery, Ford, Hyundai, Ineos"),
        ("Ουγγαρία", "Nissan, Omoda, Jaecoo, Piaggio Commercial, Maxus"),
        ("Σλοβακία", "Nissan, Omoda, Jaecoo"),
        ("Τσεχία", "Nissan, Omoda, Jaecoo, Piaggio Commercial"),
        ("Αυστρία", "Piaggio Commercial"),
        ("Βουλγαρία", "Nissan"),
        ("Βόρεια Μακεδονία", "Ford, MG, Chery, Hyundai, Renault, Dacia, Nissan, Ineos"),
        ("Βοσνία-Ερζεγοβίνη", "Renault, Dacia, Nissan, Ford, MG, Chery, Ineos"),
        ("Αλβανία", "Renault, Dacia, Ford, MG, Chery, Hyundai, Ineos"),
        ("Μαυροβούνιο", "Ford, MG, Chery, Hyundai, Renault, Dacia, Nissan"),
        ("Κόσοβο", "Renault, Dacia, Nissan, MG, Chery, Hyundai, Ineos"),
        ("Ελλάδα", "Renault, Dacia, Ineos (και Alpine από το 2027)"),
        ("Κύπρος", "Ineos"),
    ]
    story = header("Grand Automotive: η εταιρεία και η επικοινωνία",
                   "Ο όμιλος Grand Automotive και η Grand Automotive Hellas (GA Hellas), ο αποκλειστικός εισαγωγέας των Renault "
                   "και Dacia στην Ελλάδα. Company overview and contacts.")
    story += [
        P("Επικοινωνία με την Grand Automotive Hellas (Ελλάδα)", "h1"),
        bullets([
            f"Τηλέφωνο εξυπηρέτησης πελατών: <b>{CUSTOMER_CARE}</b>, {CUSTOMER_CARE_HOURS}. Η εξυπηρέτηση γίνεται με την "
            "υποστήριξη ψηφιακού βοηθού.",
            "E-mail για τη Renault: <b>renault-info@grandautomotive.gr</b>. E-mail για την Dacia: <b>dacia-info@grandautomotive.gr</b>.",
            f"Κεντρικά γραφεία: {HQ}.",
            "Ιστοσελίδες: renault.gr και dacia.gr (γκάμα, τιμές, δίκτυο), grandautomotive.eu (ο όμιλος).",
            "Online αγορά υπηρεσιών (βεβαιώσεις): e-services.grandautomotive.gr.",
            RNLT_ATHENS,
        ]),
        P("Grand Automotive Hellas (GA Hellas)", "h1"),
        P("Η Grand Automotive Hellas είναι από την <b>1η Μαρτίου 2025</b> ο επίσημος και αποκλειστικός εισαγωγέας καινούργιων "
          "αυτοκινήτων <b>Renault</b> και <b>Dacia</b> στην Ελλάδα, με συμβάσεις διανομής που υπέγραψε με τη γαλλική "
          "κατασκευάστρια Renault S.A.S. Είναι μέλος του ομίλου Grand Automotive Group LLP."),
        bullets([
            "Πλήρης επωνυμία: Grand Automotive Hellas Μονοπρόσωπη Ανώνυμη Εταιρεία Εισαγωγής και Εμπορίας Αυτοκινήτων και "
            "Γενικών Δραστηριοτήτων και Υπηρεσιών. Διακριτικός τίτλος: GA Hellas Α.Ε.",
            "Έδρα: Δήμος Μεταμόρφωσης Αττικής, 12ο χλμ. Νέας Εθνικής Οδού Αθηνών – Λαμίας, Τ.Κ. 14452. Α.Φ.Μ. 802575339, "
            "Αρ. Γ.Ε.ΜΗ. 178882401000.",
            "Διευθύνων Σύμβουλος (CEO): κ. Στήβεν Σίρτης.",
            "Δίκτυο: <b>29 επίσημα σημεία πώλησης</b> και <b>34 εξουσιοδοτημένα σημεία service</b> σε όλη την Ελλάδα, "
            "κοινό για Renault και Dacia, που επεκτείνεται συνεχώς. Η πλήρης λίστα είναι στο έγγραφο «Δίκτυο αντιπροσώπων».",
            "Πριν από την 1η Μαρτίου 2025 εισαγωγέας ήταν η ΤΕΟΡΕΝ ΜΟΤΟΡΣ Α.Ε. Για παλιούς τιμοκαταλόγους εκείνης της "
            "περιόδου, η GA Hellas παραπέμπει απευθείας στην ΤΕΟΡΕΝ ΜΟΤΟΡΣ.",
        ]),
        P("Αποτελέσματα και διακρίσεις", "h2"),
        bullets([
            "2025: Renault 5.494 πωλήσεις, μερίδιο 3,8% (από 2,7% το 2024), αύξηση +50,1%, 10η θέση στην ελληνική αγορά, η "
            "καλύτερη επίδοση της μάρκας τα τελευταία 19 χρόνια.",
            "2025: Dacia 5.585 πωλήσεις, μερίδιο 3,9% (από 2,5%), αύξηση +63,3%, 9η θέση στην αγορά, οι υψηλότερες "
            "πωλήσεις που έχει καταγράψει ποτέ η μάρκα στην Ελλάδα.",
            "Μαζί οι δύο μάρκες πούλησαν 64% περισσότερα αυτοκίνητα το διάστημα Μαρτίου–Δεκεμβρίου 2025 σε σχέση με το 2024, "
            "ενώ η συνολική αγορά επιβατικών αυξήθηκε 5,2%.",
            "Renault Clio: 3η θέση στην κατηγορία του και 1η στις εταιρικές πωλήσεις (Μάρτιος–Δεκέμβριος 2025). Dacia Sandero: "
            "2η θέση στις πωλήσεις λιανικής της κατηγορίας του.",
            "Βραβείο «Most Improved Importer in Europe» του Renault Group, στο Παγκόσμιο Συνέδριο Εισαγωγέων που έγινε στην "
            "Αθήνα στις 23–25 Μαρτίου 2026 (πάνω από 100 σύνεδροι από 70 χώρες). Είναι η πρώτη φορά που η διάκριση "
            "δίνεται σε εισαγωγέα Renault στην Ελλάδα.",
            "Ετήσιο συνέδριο του δικτύου: 23–24 Ιανουαρίου 2026 στα Ιωάννινα, με πάνω από 80 συμμετέχοντες.",
        ]),
        P("GA Motors", "h2"),
        P("Η GA Motors Α.Ε. είναι αδελφή εταιρεία της GA Hellas και μέλος του επίσημου δικτύου. Λειτουργεί το concept store "
          "rnlt© Athens στο Κολωνάκι και την πρώτη ολοκληρωμένη κάθετη μονάδα Renault &amp; Dacia στη Θεσσαλονίκη (Πυλαία, "
          "7ο χλμ. Ε.Ο. Θεσσαλονίκης – Νέων Μουδανιών, 3.500 τ.μ.): πωλήσεις καινούργιων και επιλεγμένων μεταχειρισμένων, "
          "εξουσιοδοτημένο συνεργείο και φανοβαφείο, γνήσια ανταλλακτικά και αξεσουάρ. Η GA Motors διαθέτει επίσης το "
          "INEOS Grenadier στην Ελλάδα."),
        P("Μάρκες στην Ελλάδα και την Κύπρο", "h1"),
        bullets([
            "<b>Renault</b> και <b>Dacia</b>: αποκλειστικός εισαγωγέας η GA Hellas (από 1/3/2025), μέσω του εξουσιοδοτημένου δικτύου.",
            "<b>INEOS Grenadier</b>: στην Ελλάδα το διαθέτει η GA Motors. Πρεμιέρα στο ελληνικό κοινό στην Auto Athina 2026. "
            "Τιμή από 128.000 €. Λεπτομέρειες στο έγγραφο «Εγγύηση, service και προσφορές».",
            "<b>Alpine</b>: η GA Hellas θα είναι ο αποκλειστικός εισαγωγέας της Alpine στην Ελλάδα. Η εμπορική διάθεση ξεκινά "
            "το πρώτο τρίμηνο του 2027. Τα A290 και A390 παρουσιάζονται για πρώτη φορά στην Auto Athina 2026.",
            "<b>Κύπρος</b>: σύμφωνα με το grandautomotive.eu ο όμιλος εκπροσωπεί εκεί την INEOS. Δεν έχουμε στοιχεία "
            "εκθεσιακού χώρου για την Κύπρο: φόρμα επικοινωνίας στο grandautomotive.eu/contact-us ή ο εντοπισμός συνεργατών "
            "στο ineosgrenadier.com.",
            "Οι υπόλοιπες μάρκες του ομίλου (Nissan, Ford, Hyundai, MG, Chery, Omoda, Jaecoo, VinFast, Maxus, Piaggio "
            "Commercial) <b>δεν</b> διατίθενται από τον όμιλο στην Ελλάδα.",
        ]),
        P("Ο όμιλος Grand Automotive", "h1"),
        P("Η Grand Automotive (Grand Automotive LLP) είναι εισαγωγέας οχημάτων και δίκτυο αντιπροσωπειών σε <b>15 αγορές</b> "
          "της Κεντρικής και Νοτιοανατολικής Ευρώπης, εντός και εκτός Ευρωπαϊκής Ένωσης. Ιδρύθηκε το 2002 και ανήκει κατά "
          "95% στην Taavura Holdings, τη μεγαλύτερη εταιρεία οδικών μεταφορών και logistics του Ισραήλ, μέρος του "
          "επιχειρηματικού χαρτοφυλακίου της οικογένειας Livnat (πετρέλαιο και φυσικό αέριο, high-tech, επικοινωνίες, "
          "ακίνητα)."),
        bullets([
            "Μεγέθη (grandautomotive.eu): 14 μάρκες, 15 αγορές, 887 εργαζόμενοι, 69.291 οχήματα πωλήθηκαν το 2025, πάνω από "
            "320 σημεία (ιδιόκτητα και ανεξάρτητες αντιπροσωπείες).",
            "Κατά την Taavura: πάνω από 300 ανεξάρτητες αντιπροσωπείες και 26 ιδιόκτητοι εκθεσιακοί χώροι, περίπου 70.000 "
            "οχήματα τον χρόνο.",
            "Υπηρεσίες: εισαγωγή και διανομή, λιανική μέσω του δικτύου, πιστοποιημένα μεταχειρισμένα μέσω περιφερειακής "
            "μάρκας, λύσεις κινητικότητας (μακροχρόνια μίσθωση, leasing, προγράμματα επαναγοράς), ασφάλιση αυτοκινήτου, "
            "χρηματοδότηση.",
            "Οι 14 μάρκες του ομίλου: Renault, Dacia, Nissan, Alpine, Ford, Hyundai, Chery, VinFast, MG, Maxus, Ineos, Omoda, "
            "Jaecoo και Piaggio Commercial.",
            "Οι 15 αγορές: Αυστρία, Τσεχία, Σλοβακία, Σλοβενία, Κροατία, Βουλγαρία, Ουγγαρία, Σερβία, Βόρεια Μακεδονία, "
            "Βοσνία-Ερζεγοβίνη, Αλβανία, Μαυροβούνιο, Κόσοβο, Ελλάδα και Κύπρος.",
            "Ιστοσελίδα: grandautomotive.eu, με φόρμα επικοινωνίας στη σελίδα Contact Us. Η πολιτική απορρήτου του site "
            "αναφέρει την Grand Automotive, Ljubljanska Avenija 4, 10000 Ζάγκρεμπ, Κροατία.",
        ]),
        P("Μάρκες ανά αγορά (σελίδα «Where we operate» του grandautomotive.eu)", "h2"),
        table(["Αγορά", "Μάρκες"], [[m, b] for m, b in markets], [42, 132]),
        P("Grand Automotive Central Europe", "h2"),
        P("Θυγατρική με έδρα τη Βουδαπέστη (ιδρύθηκε το 2019, 201–500 εργαζόμενοι): εισάγει και διανέμει καινούργια οχήματα "
          "και ανταλλακτικά Nissan και Piaggio Commercial στην Κεντρική Ευρώπη και την Αδριατική, με γραφεία σε Βουδαπέστη, "
          "Μπρατισλάβα, Πράγα, Λιουμπλιάνα, Βελιγράδι, Σόφια και Ζάγκρεμπ. Για τη χρήση 2025 βραβεύτηκε στο συνέδριο "
          "εισαγωγέων της Nissan Europe για τη μεγαλύτερη αύξηση πωλήσεων ανάμεσα στις 18 ευρωπαϊκές αγορές εισαγωγέων της "
          "Nissan, για 3η συνεχόμενη χρονιά."),
    ]
    build("01_GA_Company_Contacts.pdf", story, "Η εταιρεία και η επικοινωνία")


# ---------------------------------------------------------------- 02 Renault

SUBSIDY = ("Στα ηλεκτρικά μοντέλα, η τιμή «από» με αστερίσκο περιλαμβάνει την κρατική επιδότηση του προγράμματος «Κινούμαι "
           "Ηλεκτρικά 3» (ΚΗ3) 3.000 € και το όφελος απόσυρσης ΚΗ3 1.500 €. Οι όροι του προγράμματος ισχύουν και τους "
           "επιβεβαιώνει ο αντιπρόσωπος.")


def model(name: str, kind: str, price: str, items: list[str]) -> list:
    return [P(name, "h2"), P(f"<i>{kind}</i> — <b>{price}</b>"), bullets(items)]


def doc_renault() -> None:
    story = header("Renault: γκάμα και τιμές στην Ελλάδα",
                   "Τα μοντέλα Renault που διαθέτει η Grand Automotive Hellas, με τις τιμές «από» του renault.gr. "
                   "Renault range and starting prices in Greece.")
    story += [
        P("Πώς διαβάζονται οι τιμές", "h1"),
        bullets([
            "Οι τιμές είναι τιμές λιανικής «από», για την έκδοση που αναφέρεται. Οι εκδόσεις και ο εξοπλισμός αλλάζουν την τιμή.",
            "Στα επαγγελματικά Kangoo Van, Trafic Van και Master η τιμή είναι <b>πλέον ΦΠΑ</b>.",
            SUBSIDY,
            "Τιμές και εξοπλισμός ανά έκδοση: renault.gr (ΤΙΜΕΣ &amp; ΕΞΟΠΛΙΣΜΟΙ) ή το εξουσιοδοτημένο δίκτυο, όπου γίνεται "
            "και το test drive.",
        ]),
        P("Επιβατικά", "h1"),
    ]
    story += model("Renault Twingo E-Tech electric", "ηλεκτρικό αυτοκίνητο πόλης, 5 πόρτες", "από 14.990 €*", [
        "Η τιμή αφορά την έκδοση Twingo E-Tech electric 27 kWh 80 evolution, με επιδότηση ΚΗ3 3.000 € και όφελος απόσυρσης "
        "ΚΗ3 1.500 €.",
        "Ηλεκτροκινητήρας 80 hp, μπαταρία 27 kWh, αυτονομία έως 263 km (WLTP, έκδοση evolution), κατανάλωση από 12,2 kWh/100 km.",
        "Ταχεία φόρτιση από 15% σε 80% σε 28 λεπτά. Λειτουργία V2L: τροφοδοτεί ηλεκτρικές συσκευές.",
        "Μήκος 3,79 m, κύκλος στροφής 9,87 m, πορτμπαγκάζ έως 360 lt, συρόμενα πίσω καθίσματα 50/50, έως 24 συστήματα "
        "υποβοήθησης οδήγησης (ADAS), openR link με Google built-in.",
    ])
    story += model("Renault 5 E-Tech electric", "ηλεκτρικό αυτοκίνητο πόλης, 5 θέσεις", "από 22.400 €*", [
        "Η τιμή αφορά την έκδοση Renault 5 E-Tech electric 40 kWh 120 hp evolution, με επιδότηση ΚΗ3 3.000 € και όφελος "
        "απόσυρσης ΚΗ3 1.500 €.",
        "Δύο μπαταρίες: urban range 40 kWh με 120 hp και αυτονομία έως 312 km, ή comfort range 52 kWh με 150 hp και "
        "αυτονομία έως 410 km (WLTP).",
        "Ταχεία φόρτιση DC από 15% σε 80% σε περίπου 30 λεπτά. Wallbox 11 kW (15–80%): 2 ώρες 37 λεπτά (40 kWh) ή 3 ώρες "
        "13 λεπτά (52 kWh). Οικιακή πρίζα 2,3 kW: 11 ώρες 12 λεπτά ή 17 ώρες 13 λεπτά. Λειτουργία V2L.",
        "Διαθέσιμο για παραγγελία και test drive στο δίκτυο Renault. Εφαρμογή My Renault για έλεγχο από απόσταση.",
    ])
    story += model("Renault 5 Turbo 3E", "περιορισμένη έκδοση, ηλεκτρικό supercar", "εκτιμώμενη αρχική τιμή 160.000 €", [
        "Μόνο 1.980 αριθμημένα αυτοκίνητα. Δύο ηλεκτροκινητήρες μέσα στους πίσω τροχούς, 555 hp, ροπή έως 4.800 Nm, "
        "τελική ταχύτητα 270 km/h.",
        "Κράτηση: επικοινωνία μέσω renault.gr για προ-παραγγελία, ποσό κράτησης 50.000 € (αφαιρείται από την τελική τιμή). "
        "Οριστικές παραγγελίες προτεραιότητας το πρώτο εξάμηνο του 2027, παραδόσεις μέσα στο 2027.",
        "Η τιμή είναι προτεινόμενη με ΦΠΑ, χωρίς έξτρα και εξατομίκευση, και μπορεί να αλλάξει στην έναρξη των πωλήσεων.",
    ])
    story += model("Νέο Renault Clio", "μικρό αυτοκίνητο, Νο1 σε πωλήσεις στην Ευρώπη το πρώτο εξάμηνο του 2025", "από 20.900 € ή 199 €/μήνα", [
        "Η τιμή αφορά την έκδοση Clio TCe turbo 115 evolution και περιλαμβάνει όφελος προωθητικού προγράμματος 500 €.",
        "Κινητήρες: full hybrid E-Tech 160 hp, βενζίνης TCe turbo 115 με αυτόματο EDC, διπλού καυσίμου βενζίνη/LPG Eco-G "
        "turbo 120 με αυτόματο EDC.",
        "Αυτονομία έως 1.000 km και κατανάλωση από 3,9 lt/100 km (full hybrid). Πορτμπαγκάζ έως 391 lt, 29 συστήματα ADAS, "
        "openR link με Google built-in.",
        "Παράδειγμα χρηματοδότησης 199 €/μήνα: τιμή 20.900 €, προκαταβολή 7.240 €, δάνειο 13.660 €, σταθερό επιτόκιο 7,5% "
        "(με εισφορά Ν.128/75), 48 μήνες, δόση 198,95 € και τελική δόση (balloon) 7.524 €, ΣΕΠΠΕ 8,5554%. Η δόση είναι "
        "ενδεικτική.",
    ])
    story += model("Renault Captur", "compact οικογενειακό SUV", "από 20.900 €", [
        "Η τιμή αφορά την έκδοση Captur TCe turbo 115 evolution.",
        "Κινητήρες: full hybrid E-Tech 160 hp, TCe turbo 115 βενζίνης, Eco-G turbo 120 βενζίνης/LPG (αυτονομία έως 1.400 km).",
        "Full hybrid: αυτονομία έως 1.000 km, έως 80% ηλεκτρική κίνηση και έως 40% οικονομία καυσίμου.",
        "Πορτμπαγκάζ έως 616 lt με το πίσω κάθισμα μπροστά (συρόμενο κατά 16 cm), οθόνη 10,4\", 29 συστήματα ADAS.",
    ])
    story += model("Renault Symbioz", "compact οικογενειακό SUV, full hybrid", "από 27.900 €", [
        "Η τιμή αφορά την έκδοση Symbioz full hybrid E-Tech 160 evolution.",
        "Full hybrid E-Tech 160 hp, αυτονομία έως 1.000 km, έως 80% ηλεκτρική κίνηση, έως 40% οικονομία καυσίμου.",
        "Πορτμπαγκάζ έως 624 lt (συρόμενο πίσω κάθισμα 16 cm), πανοραμική οροφή solarbay® με ρυθμιζόμενη σκίαση.",
    ])
    story += model("Νέο Renault Austral", "οικογενειακό SUV", "από 30.500 €", [
        "Η τιμή αφορά την έκδοση Austral hybrid 150 auto techno.",
        "Κινητήρες: full hybrid E-Tech 200 hp (από 4,7 lt/100 km, από 106 g/km CO₂) ή hybrid 150 hp με αυτόματο κιβώτιο "
        "(από 6,4 lt/100 km).",
        "Αυτονομία έως 1.100 km χωρίς φόρτιση, ηλεκτρική κίνηση έως 130 km/h και έως 80% του χρόνου στην πόλη.",
        "Πορτμπαγκάζ 657 lt, τετραδιεύθυνση 4Control (κύκλος στροφής 10,1 m), openR link με Google built-in.",
    ])
    story += model("Renault 4 E-Tech electric", "ηλεκτρικό B-SUV", "από 24.400 €*", [
        "Η τιμή αφορά την έκδοση Renault 4 E-Tech electric 40 kWh 120 evolution, με επιδότηση ΚΗ3 3.000 € και όφελος "
        "απόσυρσης ΚΗ3 1.500 €.",
        "Μπαταρία 40 kWh με 120 hp ή 52 kWh με 150 hp, αυτονομία έως 409 km (WLTP). Φόρτιση 15–80% σε 30 λεπτά.",
        "Πορτμπαγκάζ 420 lt (έως 1.405 lt με αναδιπλωμένα καθίσματα), απόσταση από το έδαφος 18,1 cm, ζάντες 18\", "
        "έκδοση με υφασμάτινη οροφή.",
    ])
    story += model("Renault Arkana", "coupé SUV", "από 30.900 €", [
        "Η τιμή αφορά την έκδοση techno full hybrid E-Tech 145.",
        "Κινητήρες: full hybrid E-Tech 145 hp ή mild hybrid 140 hp με αυτόματο EDC. Αυτονομία έως 1.020 km.",
        "Πορτμπαγκάζ έως 513 lt (480 lt στο full hybrid). Σπορ έκδοση esprit Alpine.",
    ])
    story += model("Renault Rafale", "SUV coupé, plug-in υβριδικό 4x4", "από 51.800 €", [
        "Η τιμή αφορά την έκδοση Rafale plug-in hyper hybrid E-Tech 4x4 300 esprit Alpine.",
        "Plug-in hyper hybrid E-Tech 4x4 300 hp, μπαταρία 22 kWh, έως 105 km αμιγώς ηλεκτρικά και έως 1.000 km συνολικά, "
        "από 1,7 lt/100 km και 39 g/km CO₂ (WLTP).",
        "Τετραδιεύθυνση 4Control Advanced, πανοραμική οροφή Solarbay®, head-up display. Κορυφαία έκδοση Atelier Alpine.",
    ])
    story += model("Renault Trafic Combi", "επιβατικό van έως 9 θέσεων", "από 52.000 €", [
        "Η τιμή αφορά την έκδοση Trafic Combi blue dCi turbo 150 Grand ZEN L2.",
        "Κινητήρες diesel Blue dCi 150 και Blue dCi 170 EDC. Οθόνη 8\" με Easy Link, full LED φωτισμός.",
    ])
    story += [P("Επαγγελματικά", "h1")]
    story += model("Renault Kangoo Van", "μικρό επαγγελματικό", "από 26.680 € πλέον ΦΠΑ", [
        "Όγκος φόρτωσης 3,6 m³ (L1) ή 4,6 m³ (L2, μήκος 4,91 m), ωφέλιμο φορτίο έως 1.000 kg, ρυμούλκηση έως 1.500 kg.",
        "Κινητήρες diesel Blue dCi 95 και Blue dCi 115 (και με αυτόματο EDC), καθώς και ηλεκτρική έκδοση E-Tech electric.",
    ])
    story += model("Renault Trafic Van", "μεσαίο επαγγελματικό", "από 35.709 € πλέον ΦΠΑ", [
        "Κινητήρες diesel Blue dCi 110, 130 και 150. Όγκος φόρτωσης έως 8,9 m³, μεταφορά αντικειμένων μήκους έως 4,15 m.",
        "Κινητό γραφείο στο μεσαίο κάθισμα, αποθηκευτικοί χώροι πάνω από 88 λίτρα.",
    ])
    story += model("Νέο Renault Trafic Van E-Tech electric", "ηλεκτρικό μεσαίο επαγγελματικό", "τιμή στο δίκτυο", [
        "Τεχνολογία 800V, αυτονομία έως 450 km, φόρτιση 15–80% σε περίπου 20 λεπτά, όγκος φόρτωσης πάνω από 5 m³, ύψος "
        "κάτω από 1,9 m, 18 συστήματα ADAS.",
    ])
    story += model("Νέο Renault Master", "μεγάλο επαγγελματικό", "από 40.224 € πλέον ΦΠΑ", [
        "Ωφέλιμο φορτίο έως 1.310 kg, ρυμούλκηση 2.500 kg, αποθηκευτικοί χώροι 135 lt, αεροδυναμικός σχεδιασμός με "
        "οικονομικό diesel Blue dCi. Διατίθεται και ηλεκτρικό.",
    ])
    story += [
        P("Τεχνολογίες Renault", "h1"),
        P("Full hybrid E-Tech", "h2"),
        P("Αυτοφορτιζόμενο υβριδικό: δεν μπαίνει στην πρίζα, η μπαταρία φορτίζει όταν επιβραδύνετε ή φρενάρετε. Έως 80% "
          "αμιγώς ηλεκτρική κίνηση στην πόλη και έως 40% οικονομία καυσίμου. 160 hp στα Clio, Captur και Symbioz, 200 hp "
          "στο Austral, 145 hp στο Arkana. Το Rafale είναι plug-in hyper hybrid 300 hp με τετρακίνηση."),
        P("Διπλού καυσίμου bi-fuel (Eco-G turbo, βενζίνη + LPG)", "h2"),
        bullets([
            "Εργοστασιακή τεχνολογία Renault: δύο ρεζερβουάρ (βενζίνη και υγραέριο LPG), αυτονομία έως 1.450 km συνολικά "
            "(ανάλογα με το μοντέλο). Διαθέσιμη στα Clio και Captur (Eco-G turbo 120).",
            "Το LPG κοστίζει περίπου 40% λιγότερο από τη βενζίνη (μέσες τιμές Ελλάδας 6/4/2026: LPG 1,372 €/lt, αμόλυβδη "
            "2,281 €/lt). Έως 11% λιγότερο CO₂ από αντίστοιχο βενζινοκίνητο.",
            "Η εκκίνηση γίνεται πάντα με βενζίνη. Η εναλλαγή καυσίμου γίνεται αυτόματα ή με ένα κουμπί. Όταν αδειάσει το "
            "LPG, περνά αυτόματα σε βενζίνη. Πάνω από 1.050 πρατήρια LPG στην Ελλάδα.",
            "Service κάθε 20.000 έως 30.000 km, σύμφωνα με το πρόγραμμα συντήρησης του κατασκευαστή.",
            "Συνεργασία με Shell και Coral Gas: η αγορά Renault bi-fuel (Clio ή Captur) συνοδεύεται με δώρο τα καύσιμα "
            "ενός ολόκληρου έτους. Τους όρους τους δίνει ο αντιπρόσωπος.",
        ]),
        P("Ηλεκτρικά E-Tech electric και συνδεσιμότητα", "h2"),
        P("Ηλεκτρική γκάμα: Twingo, Renault 5, Renault 4, Renault 5 Turbo 3E, Kangoo Van E-Tech, Trafic Van E-Tech και Master. "
          "Το σύστημα πολυμέσων openR link έχει Google built-in (Google Maps, Google Assistant, πάνω από 100 εφαρμογές, ανάλογα "
          "με την έκδοση). Η εφαρμογή My Renault δείχνει την αυτονομία, προγραμματίζει τη φόρτιση και τον κλιματισμό."),
    ]
    build("02_GA_Renault_Models_Prices.pdf", story, "Renault: γκάμα και τιμές")


# ---------------------------------------------------------------- 03 Dacia


def doc_dacia() -> None:
    story = header("Dacia: γκάμα και τιμές στην Ελλάδα",
                   "Τα μοντέλα Dacia που διαθέτει η Grand Automotive Hellas, με τις τιμές «από» του dacia.gr. "
                   "Dacia range and starting prices in Greece.")
    story += [
        P("Οι τιμές είναι τιμές λιανικής «από». Ο ισχύων τιμοκατάλογος λιανικής της Dacia είναι της 6ης Φεβρουαρίου 2026 "
          "(dacia.gr, σελίδα «Τιμοκατάλογοι»). Όλα τα Sandero, Sandero Stepway, Jogger, Duster και Bigster διατίθενται με το "
          "πρόγραμμα <b>Dacia Your Way</b> (δείτε στο τέλος)."),
        P("Μοντέλα", "h1"),
    ]
    story += model("Νέο Dacia Sandero", "αυτοκίνητο πόλης, πρώτο σε πωλήσεις στην Ευρώπη", "από 15.950 €", [
        "Κινητήρες: βενζίνης TCe 100 (100 hp) και διπλού καυσίμου βενζίνη/LPG Eco-G 120 (120 hp).",
        "Νέα εμπρός μάσκα με φωτιστική υπογραφή σε σχήμα «Τ», κεντρική οθόνη 10\" με Media Nav Live, ψηφιακός πίνακας 7\".",
        "Με το Eco-G εξοικονομείτε έως 35 € σε κάθε γέμισμα (υπολογισμός με μέσες τιμές Ελλάδας, Ιανουάριος 2025).",
    ])
    story += model("Νέο Dacia Sandero Stepway", "crossover", "από 17.350 €", [
        "Κινητήρες: βενζίνης TCe 110 (από 5,6 lt/100 km) και Eco-G 120 βενζίνη/LPG, και με αυτόματο κιβώτιο EDC.",
        "Με Eco-G αυτονομία έως 1.450 km. Αυξημένη απόσταση από το έδαφος, προστατευτικά Starkle®, ταπετσαρία που πλένεται.",
        "Το προηγούμενο Sandero Stepway διατίθεται ακόμη από 16.890 € (TCe 90, TCe 90 CVT, ECO-G 100).",
    ])
    story += model("Νέο Dacia Jogger", "7θέσιο οικογενειακό", "από 24.200 €", [
        "Κινητήρες: TCe 110 βενζίνης, Eco-G 120 βενζίνη/LPG και, για πρώτη φορά, hybrid 155 (full hybrid).",
        "Πορτμπαγκάζ έως 2.094 lt. Ευέλικτη διαμόρφωση εσωτερικού για 5 ή 7 επιβάτες.",
    ])
    story += model("Dacia Duster", "SUV (3η γενιά)", "από 20.700 €", [
        "Κινητήρες: hybrid 155 (full hybrid, 155 hp, 205 Nm, έως 80% ηλεκτρική οδήγηση στην πόλη), mild hybrid 140, "
        "Eco-G 120 βενζίνη/LPG (χειροκίνητο ή αυτόματο 6 σχέσεων διπλού συμπλέκτη) και tribrid 150 4x4.",
        "Tribrid 150 4x4: ηλεκτρική ενέργεια, βενζίνη και LPG μαζί, τετρακίνηση και αυτόματο κιβώτιο, αυτονομία έως 1.500 km "
        "(WLTP) με τα δύο ρεζερβουάρ.",
        "Απόσταση από το έδαφος 217 mm, γωνία προσέγγισης έως 30°. Πάνω από 2 εκατομμύρια χρήστες στην Ευρώπη.",
    ])
    story += model("Dacia Bigster", "5θέσιο υβριδικό C-SUV", "από 23.990 €", [
        "Κινητήρες: hybrid 155 (full hybrid), mild hybrid 140, mild hybrid-G 140 βενζίνη/LPG και tribrid 150 4x4.",
        "Πορτμπαγκάζ 702 lt (667 lt VDA), ηλεκτρική πόρτα πορτμπαγκάζ hands-free, κλιματισμός δύο ζωνών, έως 1.500 km μικτή "
        "αυτονομία.",
    ])
    story += model("Νέο Dacia Spring", "100% ηλεκτρικό αυτοκίνητο πόλης, κατασκευασμένο στην Ευρώπη", "τιμή στο δίκτυο", [
        "Κινητήρας 80 hp, αυτονομία έως 250 km (WLTP), ταχεία φόρτιση 15–80% σε 28 λεπτά, κόστος περίπου 2,50 € ανά 100 km "
        "με οικιακή φόρτιση.",
        "4 θέσεις, πορτμπαγκάζ 337 lt, μήκος 3,85 m. Εφαρμογή My Dacia για σταθμούς και χρόνους φόρτισης.",
    ])
    story += model("Dacia Striker", "νέο crossover", "τιμή και διάθεση στο δίκτυο", [
        "Μήκος 4,62 m, πανοραμική οροφή, απόσταση από το έδαφος 23,4 cm, πορτμπαγκάζ 600 lt με ηλεκτρικό άνοιγμα, 5 θέσεις. "
        "Τα στοιχεία εκκρεμούν πιστοποίησης.",
    ])
    story += [
        P("Τεχνολογίες Dacia", "h1"),
        bullets([
            "<b>Eco-G</b>: εργοστασιακός κινητήρας διπλού καυσίμου, βενζίνη και υγραέριο LPG, με δύο ρεζερβουάρ. Χαμηλότερο "
            "κόστος καυσίμου και μεγάλη αυτονομία (έως 1.450 km στα Sandero).",
            "<b>hybrid 155</b>: full hybrid που δεν μπαίνει στην πρίζα, έως 80% ηλεκτρική κίνηση στην πόλη και έως 40% "
            "οικονομία καυσίμου. Σε Duster, Bigster και Jogger.",
            "<b>mild hybrid 140</b>: βενζινοκινητήρας με ελαφριά ηλεκτρική υποβοήθηση (και σε έκδοση -G με LPG στο Bigster).",
            "<b>tribrid 150 4x4</b>: τρεις πηγές ενέργειας (ηλεκτρισμός, βενζίνη, LPG), τετρακίνηση, αυτόματο κιβώτιο, έως "
            "1.500 km αυτονομία. Σε Duster και Bigster.",
        ]),
        P("Dacia Your Way", "h1"),
        P("Πρόγραμμα απόκτησης για Sandero, Sandero Stepway, Duster, Bigster και Jogger, για περιορισμένο αριθμό αυτοκινήτων "
          "και έως εξαντλήσεως των αποθεμάτων. Ο πελάτης διαλέγει ένα από τα δύο:"),
        bullets([
            "<b>Επιλογή χρηματοδότησης</b>: επιδοτούμενο επιτόκιο από 1,9% (ή 3,9%), πλέον εισφοράς Ν.128/75, για "
            "συγκεκριμένες εκδόσεις, με ελάχιστη προκαταβολή 20% και διάρκεια 36 μήνες.",
            "<b>Επιλογή οφέλους</b>: χρηματικό όφελος (έκπτωση) έως 3.000 €, ανάλογα με το μοντέλο και την έκδοση. Λειτουργεί "
            "εναλλακτικά του επιδοτούμενου επιτοκίου.",
            "Προσφορά ή test drive: στον εξουσιοδοτημένο διανομέα Dacia της επιλογής σας.",
        ]),
    ]
    build("03_GA_Dacia_Models_Prices.pdf", story, "Dacia: γκάμα και τιμές")


# ---------------------------------------------------------------- 04 dealer network

SALES = "e8821c46-86c7-41b1-9b8e-a27c5d388d71"  # "Εξουσιοδοτημένος Διανομέας" in the locators' services list
SERVICE = "ff6cdca6-b177-47b9-b730-878c3aa74e8a"  # "Εξουσιοδοτημένος Επισκευαστής"

REGIONS = {
    "ΑΙΤΩΛ/ΝΑΝΙΑ": "Αιτωλοακαρνανία (Aitoloakarnania)", "ΑΡΓΟΛΙΔΑ": "Αργολίδα (Argolida)", "ΑΤΤΙΚΗ": "Αττική (Attica)",
    "ΑΧΑΪΑ": "Αχαΐα (Achaia)", "ΒΟΙΩΤΙΑ": "Βοιωτία (Boeotia)", "ΔΡΑΜΑ": "Δράμα (Drama)", "ΔΩΔΕΚΑΝΗΣΑ": "Δωδεκάνησα (Dodecanese)",
    "ΕΒΡΟΣ": "Έβρος (Evros)", "ΕΥΒΟΙΑ": "Εύβοια (Evia)", "ΖΑΚΥΝΘΟΣ": "Ζάκυνθος (Zakynthos)", "ΗΜΑΘΙΑ": "Ημαθία (Imathia)",
    "ΗΡΑΚΛΕΙΟ": "Ηράκλειο Κρήτης (Heraklion, Crete)", "ΘΕΣΠΡΩΤΙΑ": "Θεσπρωτία (Thesprotia)",
    "ΘΕΣΣΑΛΟΝΙΚΗ": "Θεσσαλονίκη (Thessaloniki)", "ΙΩΑΝΝΙΝΑ": "Ιωάννινα (Ioannina)", "ΚΑΒΑΛΑ": "Καβάλα (Kavala)",
    "ΚΑΡΔΙΤΣΑ": "Καρδίτσα (Karditsa)", "ΚΕΡΚΥΡΑ": "Κέρκυρα (Corfu)", "ΚΟΖΑΝΗ": "Κοζάνη (Kozani)",
    "ΚΟΡΙΝΘΙΑ": "Κορινθία (Corinthia)", "ΛΑΡΙΣΑ": "Λάρισα (Larissa)", "ΜΑΓΝΗΣΙΑ": "Μαγνησία (Magnesia, Βόλος)",
    "ΞΑΝΘΗ": "Ξάνθη (Xanthi)", "ΠΙΕΡΙΑ": "Πιερία (Pieria, Κατερίνη)", "ΠΡΕΒΕΖΑ": "Πρέβεζα (Preveza)",
    "ΡΕΘΥΜΝΟ": "Ρέθυμνο Κρήτης (Rethymno, Crete)", "ΣΕΡΡΕΣ": "Σέρρες (Serres)", "ΦΘΙΩΤΙΔΑ": "Φθιώτιδα (Fthiotida, Λαμία)",
    "ΦΛΩΡΙΝΑ": "Φλώρινα (Florina)", "ΧΑΛΚΙΔΙΚΗ": "Χαλκιδική (Chalkidiki)", "ΧΑΝΙΑ": "Χανιά Κρήτης (Chania, Crete)",
    "ΧΙΟΣ": "Χίος (Chios)",
}
# Greek -> Latin (close to ELOT 743), only to give each town a Latin spelling next to the Greek one.
_ONE = dict(zip("αβγδεζηθικλμνξοπρστυφχψως", ["a", "v", "g", "d", "e", "z", "i", "th", "i", "k", "l", "m", "n", "x", "o", "p", "r",
                                                 "s", "t", "y", "f", "ch", "ps", "o", "s"]))


# The usual English names of the bigger places (a caller may say "Athens", not "Athina").
ENGLISH = {"Αθήνα": "Athens", "Πειραιάς": "Piraeus", "Ηράκλειο": "Heraklion", "Κέρκυρα": "Corfu", "Ρόδος": "Rhodes",
           "Πάτρα": "Patras", "Λάρισα": "Larissa", "Κόρινθος": "Corinth", "Θεσσαλονίκη": "Thessaloniki"}


def latin(word: str) -> str:
    if word in ENGLISH:
        return ENGLISH[word]
    text = "".join(c for c in unicodedata.normalize("NFD", word.lower()) if not unicodedata.combining(c))
    out, i = "", 0
    while i < len(text):
        pair = text[i:i + 2]
        nxt = text[i + 2:i + 3]
        if pair in ("αυ", "ευ"):
            out += pair[0].replace("α", "a").replace("ε", "e") + ("v" if nxt and nxt in "αεηιοωυβγδζλμνρ" else "f")
            i += 2
        elif pair == "ου":
            out, i = out + "ou", i + 2
        elif pair == "μπ":
            out, i = out + ("b" if i == 0 else "mp"), i + 2
        elif pair == "ντ":
            out, i = out + ("d" if i == 0 else "nt"), i + 2
        elif pair in ("γκ", "γγ"):
            out, i = out + ("g" if i == 0 else "ng"), i + 2
        else:
            out += _ONE.get(text[i], text[i])
            i += 1
    return out.title()


def phone_text(raw: str) -> str:
    """Greek numbers have 10 digits; written as 210 960 2556 (Athens area) or 2752 028 288, as people read them."""
    numbers = []
    for part in re.split(r"[,/]", raw or ""):
        digits = re.sub(r"\D", "", part)
        if digits.startswith("0030"):
            digits = digits[4:]
        if len(digits) != 10:
            if part.strip():
                numbers.append(part.strip())
            continue
        numbers.append(f"{digits[:3]} {digits[3:6]} {digits[6:]}" if digits.startswith("21") else f"{digits[:4]} {digits[4:7]} {digits[7:]}")
    return " ή ".join(numbers) or "–"


def squash(text: str) -> str:
    """For matching the same dealer in the Renault and Dacia lists (accents, Latin look-alike capitals, punctuation)."""
    text = unicodedata.normalize("NFD", (text or "").upper())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.translate(str.maketrans("ABEZHIKMNOPTYX", "ΑΒΕΖΗΙΚΜΝΟΡΤΥΧ"))
    return re.sub(r"[^0-9Α-ΩA-Z]", "", text)


def same_place(a: str, b: str) -> bool:
    """The two lists sometimes write one address differently ("Καρφά 22, Κοντάρι" / "Καρφά 22, Κοντάρι Χίου")."""
    a, b = squash(a), squash(b)
    return a.startswith(b) or b.startswith(a)


def load_network() -> list[dict]:
    """One entry per address, with what each brand offers there (sales, service), from both official dealer locators."""
    locations: list[dict] = []
    for brand in ("renault", "dacia"):
        data = json.load(open(os.path.join(RESEARCH, f"dealers_{brand}.json"), encoding="utf-8"))
        for d in data["dealers"]:
            address = ", ".join(x.strip() for x in (d["AddressLine1"], d["AddressLine2"]) if x and x.strip())
            loc = next((x for x in locations if squash(x["name"]) == squash(d["DealerName"]) and same_place(x["address"], address)), None)
            if loc is None:
                loc = {
                    "name": re.sub(r"\s+", " ", d["DealerName"]).strip(), "address": address, "city": d["City"].strip(),
                    "postcode": d["Postcode"].strip(), "region": d["CountryName"].strip(), "phone": phone_text(d["Phone"]),
                    "email": d["Email"].strip(), "web": d["WebsiteUrl"].strip() if len(d["WebsiteUrl"].strip()) > 8 else "",
                    "services": {},
                }
                locations.append(loc)
            loc["services"][brand] = (SALES in d["AvailableServices"], SERVICE in d["AvailableServices"])
    return sorted(locations, key=lambda x: (squash(REGIONS.get(x["region"], x["region"])), squash(x["city"]), squash(x["name"])))


def services_text(services: dict) -> str:
    parts = []
    for brand, label in (("renault", "Renault"), ("dacia", "Dacia")):
        if brand not in services:
            continue
        sales, service = services[brand]
        what = "πωλήσεις και service" if sales and service else "πωλήσεις" if sales else "service (συνεργείο)" if service else ""
        if what:
            parts.append(f"{label}: {what}")
    return " · ".join(parts)


def doc_network() -> None:
    network = load_network()
    by_region: dict[str, list[dict]] = {}
    for loc in network:
        by_region.setdefault(REGIONS.get(loc["region"], loc["region"].title()), []).append(loc)
    cities = [f"{city} ({latin(city)})" for city in sorted({loc["city"] for loc in network}, key=squash)]
    story = header("Δίκτυο αντιπροσώπων Renault και Dacia στην Ελλάδα",
                   "Εξουσιοδοτημένοι διανομείς (πωλήσεις) και επισκευαστές (service) της Grand Automotive Hellas, από τους "
                   "επίσημους εντοπιστές καταστημάτων του renault.gr και του dacia.gr. Official dealer network in Greece.")
    story += [
        bullets([
            "Το δίκτυο είναι κοινό για Renault και Dacia: 29 επίσημα σημεία πώλησης και 34 εξουσιοδοτημένα σημεία service. "
            f"Αυτή η λίστα έχει {len(network)} διευθύνσεις.",
            "Οι επίσημοι εντοπιστές δεν δημοσιεύουν ωράρια: για το ωράριο, το test drive ή ραντεβού service, ο πελάτης "
            "τηλεφωνεί στο κατάστημα.",
            "«Πωλήσεις» σημαίνει εξουσιοδοτημένος διανομέας (έκθεση, προσφορές, test drive). «Service» σημαίνει "
            "εξουσιοδοτημένος επισκευαστής (συνεργείο, συντήρηση, εγγύηση).",
            f"Για οτιδήποτε άλλο: εξυπηρέτηση πελατών GA Hellas {CUSTOMER_CARE}, {CUSTOMER_CARE_HOURS}.",
            RNLT_ATHENS,
        ]),
        P("Πόλεις με κατάστημα: " + ", ".join(cities) + ".", "note"),
    ]
    for region in sorted(by_region, key=squash):
        story.append(P(region, "h1"))
        for loc in by_region[region]:
            line = (f"<b>{esc(loc['name'])}</b> — {esc(loc['city'])} ({latin(loc['city'])}), {esc(loc['address'])}, "
                    f"Τ.Κ. {esc(loc['postcode'])}. Τηλέφωνο {esc(loc['phone'])}."
                    + (f" E-mail {esc(loc['email'])}." if loc["email"] else "")
                    + (f" Ιστοσελίδα {esc(loc['web'].replace('https://', '').replace('http://', '').rstrip('/'))}." if loc["web"] else "")
                    + f" {services_text(loc['services'])}.")
            story.append(P(line, "dealer"))
    build("04_GA_Dealer_Network_Greece.pdf", story, "Δίκτυο αντιπροσώπων")


# ---------------------------------------------------------------- 05 warranty, service, offers, events


def doc_aftersales() -> None:
    story = header("Εγγύηση, service, προσφορές και εκδηλώσεις",
                   "Εγγυήσεις Renault και Dacia, service και ανταλλακτικά, τρέχουσες προσφορές, Auto Athina 2026, INEOS "
                   "Grenadier και Alpine. Warranty, after-sales, offers and events.")
    story += [
        P("Εγγύηση Renault", "h1"),
        bullets([
            "<b>5 χρόνια εργοστασιακή εγγύηση</b> για όλα τα μοντέλα Renault, από την Grand Automotive Hellas.",
            "3 χρόνια εγγύηση βαφής και 12 χρόνια εγγύηση αντιδιαβρωτικής προστασίας.",
            "1 χρόνος εγγύηση στα ανταλλακτικά και την εργασία, για κάθε επέμβαση στο εξουσιοδοτημένο δίκτυο Renault.",
        ]),
        P("Εγγύηση Dacia", "h1"),
        bullets([
            "<b>5 χρόνια εργοστασιακή εγγύηση ΔΩΡΟ</b> για τους νέους πελάτες Dacia, σε όλα τα μοντέλα, από την GA Hellas.",
            "6 χρόνια εγγύηση αντιδιαβρωτικής προστασίας.",
            "<b>5 χρόνια οδική βοήθεια</b>.",
            "1 χρόνος εγγύηση σε κάθε εργασία συντήρησης ή επισκευής και στα ανταλλακτικά, στο δίκτυο Dacia.",
        ]),
        P("Οδική βοήθεια και έκτακτη ανάγκη", "h2"),
        bullets([
            "Ο αριθμός οδικής βοήθειας του αυτοκινήτου υπάρχει στα έγγραφα του αυτοκινήτου (βιβλίο εγγύησης και service). Οι "
            "ιστοσελίδες renault.gr και dacia.gr δεν τον δημοσιεύουν σήμερα.",
            f"Αν ο πελάτης δεν τον βρίσκει: εξυπηρέτηση πελατών GA Hellas {CUSTOMER_CARE} ({CUSTOMER_CARE_HOURS}) ή ο "
            "αντιπρόσωπός του.",
            "Σε ατύχημα με τραυματία ή κίνδυνο: <b>112</b>, ο ευρωπαϊκός αριθμός έκτακτης ανάγκης (και 100 Αστυνομία, 166 ΕΚΑΒ, "
            "199 Πυροσβεστική).",
        ]),
        P("Service, ανταλλακτικά και αξεσουάρ", "h1"),
        bullets([
            "Service και επισκευές γίνονται στους εξουσιοδοτημένους επισκευαστές (34 σημεία, λίστα στο έγγραφο «Δίκτυο "
            "αντιπροσώπων»). Το ραντεβού κλείνεται με τηλέφωνο στο συνεργείο.",
            "Το πρόγραμμα συντήρησης ορίζει ο κατασκευαστής και υπάρχει στο βιβλίο service. Στα bi-fuel (LPG) το service γίνεται "
            "κάθε 20.000 έως 30.000 km.",
            "Γνήσια ανταλλακτικά Renault και Dacia, με εγγύηση 1 έτους. Η Renault συνιστά λιπαντικά Castrol (Renault-Castrol "
            "GTX, Castrol Edge).",
            "Αξεσουάρ: παιδικά καθίσματα (Babysafe Plus, Duo Plus Isofix), μπάρες οροφής, μπαγκαζιέρες, βάσεις ποδηλάτων και "
            "σκι, κοτσαδόροι, πατάκια, κιτ σπορ, και συλλογή lifestyle «The Originals» στο rnlt© Athens.",
            "Online αγορά υπηρεσιών (βεβαιώσεις): e-services.grandautomotive.gr.",
            "Γενική πρακτική: αυτοκίνητα που αγοράστηκαν πριν από τον Μάρτιο 2025 (εποχή ΤΕΟΡΕΝ ΜΟΤΟΡΣ) εξυπηρετούνται κανονικά "
            "στο εξουσιοδοτημένο δίκτυο· τους όρους εγγύησης τους επιβεβαιώνει το συνεργείο.",
        ]),
        P("Τρέχουσες προσφορές (5 Οκτωβρίου 2026)", "h1"),
        bullets([
            "<b>Renault Reward</b> στην Auto Athina 2026: όφελος έως 3.500 € για περιορισμένο αριθμό ετοιμοπαράδοτων "
            "αυτοκινήτων Renault, μαζί με 5 χρόνια εργοστασιακή εγγύηση.",
            "<b>Renault Clio</b>: από 20.900 € με όφελος προωθητικού προγράμματος 500 €, ή 199 €/μήνα με χρηματοδότηση "
            "(παράδειγμα στο έγγραφο Renault).",
            "<b>Dacia Your Way</b>: επιτόκιο από 1,9% ή όφελος έως 3.000 € σε Sandero, Sandero Stepway, Duster, Bigster και "
            "Jogger, έως εξαντλήσεως των αποθεμάτων.",
            "<b>Renault bi-fuel με Shell και Coral Gas</b>: με Clio ή Captur bi-fuel, δώρο τα καύσιμα ενός έτους.",
            "<b>Ηλεκτρικά</b>: οι τιμές των Twingo, Renault 5 και Renault 4 περιλαμβάνουν επιδότηση «Κινούμαι Ηλεκτρικά 3» "
            "3.000 € και όφελος απόσυρσης 1.500 €.",
            "Όλες οι προσφορές έχουν όρους και περιορισμένη διάρκεια: τις επιβεβαιώνει ο αντιπρόσωπος.",
        ]),
        P("Test drive", "h2"),
        P("Το test drive κλείνεται στον εξουσιοδοτημένο διανομέα Renault ή Dacia της επιλογής του πελάτη (λίστα στο έγγραφο "
          "«Δίκτυο αντιπροσώπων»). Στην Auto Athina 2026 γίνονται test drives στον χώρο της έκθεσης: Renault Twingo, Renault 5 "
          "E-Tech electric, Clio και Austral· Dacia Sandero Stepway και Duster."),
        P("Auto Athina 2026", "h1"),
        bullets([
            AUTO_ATHINA,
            "Renault: όλη η γκάμα (Clio, Captur, Symbioz, Austral, Rafale, Twingo, Renault 5, Renault 4). Full hybrid E-Tech "
            "160 hp στα Clio, Captur, Symbioz και 200 hp στο Austral, Rafale 300 hp plug-in.",
            "Dacia: Sandero και Sandero Stepway (Eco-G 120 και Eco-G 120 EDC, αυτονομία έως 1.450 km), Duster και Bigster με "
            "tribrid 150 4x4, Jogger για πρώτη φορά με hybrid 155.",
            "Alpine: πρώτη επίσημη εμφάνιση στην Ελλάδα, με τα A290 Performance και A390 GT.",
            "INEOS Grenadier: πανελλήνια πρεμιέρα, από την GA Motors.",
        ]),
        P("INEOS Grenadier", "h1"),
        bullets([
            "Στην Ελλάδα διατίθεται από την GA Motors, μέλος του επίσημου δικτύου της Grand Automotive Hellas. Τιμή από 128.000 €.",
            "Grenadier Station Wagon: πενταθέσιο 4x4 με πλαίσιο σκάλας. Κινητήρες BMW εξακύλινδροι 3.0: βενζίνης B58 286 PS "
            "και 450 Nm, diesel B57 249 PS και 550 Nm. Αυτόματο ZF 8 σχέσεων, μόνιμη τετρακίνηση, κιβώτιο μεταφοράς δύο σχέσεων.",
            "Απόσταση από το έδαφος 264 mm, διέλευση νερού 800 mm, ρυμούλκηση 3,5 τόνοι, χώρος φόρτωσης πάνω από 2.000 lt, "
            "ωφέλιμο φορτίο από 689 kg. Οθόνη 12,3\", Apple CarPlay, Android Auto, πλοήγηση εκτός δρόμου Pathfinder.",
            "Κύπρος: ο όμιλος δηλώνει την INEOS στην Κύπρο, χωρίς δημοσιευμένο εκθεσιακό χώρο· φόρμα στο "
            "grandautomotive.eu/contact-us ή ineosgrenadier.com.",
        ]),
        P("Alpine (από το 2027)", "h1"),
        bullets([
            "Η Grand Automotive Hellas θα είναι ο αποκλειστικός εισαγωγέας της Alpine, της σπορ μάρκας του Renault Group. "
            "Οι πωλήσεις ξεκινούν το πρώτο τρίμηνο του 2027. Τιμές δεν έχουν ανακοινωθεί.",
            "Alpine A290: ηλεκτρικό hot hatch, 5 πόρτες, 180 ή 220 PS, μπαταρία 52 kWh, αυτονομία έως 380 km, 0–100 km/h σε "
            "6,4 sec (220 PS).",
            "Alpine A390: ηλεκτρικό sport fastback 5 θέσεων, τρεις κινητήρες και τετρακίνηση, 400 PS (GT) ή 470 PS (GTS, 0–100 "
            "σε 3,9 sec), μπαταρία 89 kWh, αυτονομία έως 557 km.",
        ]),
    ]
    build("05_GA_Warranty_Service_Offers.pdf", story, "Εγγύηση, service και προσφορές")


# ---------------------------------------------------------------- 06 FAQ


def doc_faq() -> None:
    pairs = [
        ("Ποια είναι η Grand Automotive;",
         "Όμιλος εισαγωγής και διανομής αυτοκινήτων σε 15 αγορές της Κεντρικής και Νοτιοανατολικής Ευρώπης, με 14 μάρκες. "
         "Στην Ελλάδα τον εκπροσωπεί η Grand Automotive Hellas (GA Hellas), αποκλειστικός εισαγωγέας των Renault και Dacia από "
         "την 1η Μαρτίου 2025."),
        ("Ποιος είναι ο εισαγωγέας της Renault και της Dacia στην Ελλάδα;",
         "Η Grand Automotive Hellas Α.Ε. (GA Hellas), από την 1η Μαρτίου 2025. Πριν ήταν η ΤΕΟΡΕΝ ΜΟΤΟΡΣ."),
        ("Πώς επικοινωνώ με την εξυπηρέτηση πελατών;",
         f"Στο {CUSTOMER_CARE}, {CUSTOMER_CARE_HOURS}, ή με e-mail στο renault-info@grandautomotive.gr (Renault) και "
         "dacia-info@grandautomotive.gr (Dacia)."),
        ("Πού είναι τα γραφεία της εταιρείας;", f"Στη Μεταμόρφωση Αττικής: {HQ}."),
        ("Πόσα καταστήματα έχει το δίκτυο;",
         "29 επίσημα σημεία πώλησης και 34 εξουσιοδοτημένα σημεία service σε όλη την Ελλάδα, κοινά για Renault και Dacia."),
        ("Ποια είναι η πλησιέστερη αντιπροσωπεία;",
         "Εξαρτάται από την πόλη και την περιοχή. Στην Αττική υπάρχουν καταστήματα σε Αθήνα (Μιχαλακοπούλου και Πόντου), Γλυφάδα, Γέρακα, "
         "Μαρούσι, Καλλιθέα, Μοσχάτο, Πειραιά, Κερατσίνι, Χαλάνδρι και Χαϊδάρι. Στη Θεσσαλονίκη: GA Motors (Πυλαία) και "
         "ΒΙΟ-ΚΑΡ PLUS. Η πλήρης λίστα με διευθύνσεις και τηλέφωνα είναι στο έγγραφο «Δίκτυο αντιπροσώπων»."),
        ("Ποιο είναι το ωράριο των καταστημάτων;",
         "Οι επίσημοι εντοπιστές δεν δημοσιεύουν ωράρια: καλύτερα ένα τηλεφώνημα στο κατάστημα. Το rnlt© Athens στο Κολωνάκι "
         "είναι ανοιχτό Δευτέρα και Τετάρτη 10:00–18:00, Τρίτη, Πέμπτη και Παρασκευή 10:00–20:00, Σάββατο 10:00–15:00."),
        ("Μπορώ να κλείσω test drive;",
         "Ναι, στον εξουσιοδοτημένο διανομέα Renault ή Dacia της επιλογής σας. Μέχρι τις 11 Οκτωβρίου 2026 γίνονται test drives "
         "και στην Auto Athina (Metropolitan Expo)."),
        ("Ποιο είναι το πιο οικονομικό αυτοκίνητο;",
         "Το Dacia Sandero, από 15.950 €. Στα ηλεκτρικά, το Renault Twingo E-Tech electric από 14.990 € με την επιδότηση "
         "«Κινούμαι Ηλεκτρικά 3» και το όφελος απόσυρσης."),
        ("Πόσο κοστίζει το νέο Renault Clio;",
         "Από 20.900 € (Clio TCe turbo 115 evolution, με όφελος 500 €) ή 199 € τον μήνα με χρηματοδότηση."),
        ("Ποια ηλεκτρικά μοντέλα υπάρχουν;",
         "Renault Twingo, Renault 5 και Renault 4 E-Tech electric, το περιορισμένο Renault 5 Turbo 3E, τα επαγγελματικά Kangoo "
         "Van E-Tech, Trafic Van E-Tech και Master, και το Dacia Spring. Η Alpine (A290, A390) έρχεται το 2027."),
        ("Τι σημαίνει ο αστερίσκος στην τιμή των ηλεκτρικών;",
         "Ότι η τιμή περιλαμβάνει την κρατική επιδότηση «Κινούμαι Ηλεκτρικά 3» (ΚΗ3) 3.000 € και το όφελος απόσυρσης ΚΗ3 "
         "1.500 €. Τους όρους τους επιβεβαιώνει ο αντιπρόσωπος."),
        ("Τι είναι το full hybrid E-Tech;",
         "Υβριδικό σύστημα της Renault που δεν μπαίνει στην πρίζα: φορτίζει μόνο του όταν φρενάρετε. Έως 80% ηλεκτρική κίνηση "
         "στην πόλη και έως 40% οικονομία καυσίμου (Clio, Captur, Symbioz, Austral, Arkana)."),
        ("Τι είναι το Eco-G ή bi-fuel;",
         "Εργοστασιακός κινητήρας διπλού καυσίμου, βενζίνη και υγραέριο LPG, με δύο ρεζερβουάρ. Το LPG κοστίζει περίπου 40% "
         "λιγότερο από τη βενζίνη και η αυτονομία φτάνει έως 1.450 km. Υπάρχει σε Renault Clio και Captur και σε Dacia Sandero, "
         "Sandero Stepway, Jogger, Duster και Bigster."),
        ("Τι είναι ο κινητήρας tribrid της Dacia;",
         "Συνδυάζει ηλεκτρισμό, βενζίνη και LPG με τετρακίνηση και αυτόματο κιβώτιο (tribrid 150 4x4), με αυτονομία έως "
         "1.500 km. Υπάρχει στα Dacia Duster και Bigster."),
        ("Τι εγγύηση έχει ένα καινούργιο Renault;",
         "5 χρόνια εργοστασιακή εγγύηση σε όλα τα μοντέλα, 3 χρόνια εγγύηση βαφής και 12 χρόνια αντιδιαβρωτική προστασία."),
        ("Τι εγγύηση έχει ένα καινούργιο Dacia;",
         "5 χρόνια εργοστασιακή εγγύηση δώρο για νέους πελάτες, 6 χρόνια αντιδιαβρωτική προστασία και 5 χρόνια οδική βοήθεια."),
        ("Χάλασε το αυτοκίνητο στον δρόμο. Τι κάνω;",
         "Αν υπάρχει κίνδυνος ή τραυματίας, πρώτα 112. Για την οδική βοήθεια, ο αριθμός είναι στα έγγραφα του αυτοκινήτου "
         f"(βιβλίο εγγύησης). Αλλιώς, ο αντιπρόσωπος ή η εξυπηρέτηση πελατών {CUSTOMER_CARE} τις εργάσιμες 09:00–17:00."),
        ("Πώς κλείνω ραντεβού για service;",
         "Με τηλέφωνο σε έναν από τους 34 εξουσιοδοτημένους επισκευαστές. Οι επισκευές στο δίκτυο έχουν 1 χρόνο εγγύηση σε "
         "ανταλλακτικά και εργασία."),
        ("Υπάρχει χρηματοδότηση;",
         "Ναι. Για την Dacia, το πρόγραμμα Dacia Your Way δίνει επιτόκιο από 1,9% (προκαταβολή από 20%, 36 μήνες) ή όφελος έως "
         "3.000 €. Για τη Renault, για παράδειγμα το Clio με 199 € τον μήνα. Την προσφορά τη δίνει ο αντιπρόσωπος."),
        ("Ποιες προσφορές ισχύουν τώρα;",
         "Renault Reward με όφελος έως 3.500 € σε ετοιμοπαράδοτα (Auto Athina), Dacia Your Way (1,9% ή έως 3.000 €), δώρο "
         "καύσιμα ενός έτους με Renault bi-fuel (Shell και Coral Gas), και οι επιδοτήσεις ΚΗ3 στα ηλεκτρικά."),
        ("Πού βρίσκεται η Renault και η Dacia στην Auto Athina 2026;",
         "Στο Metropolitan Expo, 3–11 Οκτωβρίου 2026: Renault στο Hall 3, Stand A1, και Dacia στο Hall 4, Stand B4. Ωράριο "
         "Δευτέρα–Παρασκευή 14:00–21:00, Σάββατο–Κυριακή 10:00–21:00."),
        ("Τι είναι το rnlt© Athens;",
         "Το concept store της Renault στο Κολωνάκι (Σκουφά 8), της GA Motors: νέα μοντέλα όπως το Renault 5, lifestyle "
         "αξεσουάρ της συλλογής The Originals και εκδηλώσεις. Τηλέφωνο +30 214 411 10 49."),
        ("Πουλάτε INEOS Grenadier;",
         "Ναι, μέσω της GA Motors, μέλους του επίσημου δικτύου. Το Grenadier Station Wagon κοστίζει από 128.000 €, με "
         "κινητήρες BMW 3.0 βενζίνης 286 PS ή diesel 249 PS."),
        ("Πότε έρχεται η Alpine στην Ελλάδα;",
         "Η Grand Automotive Hellas θα είναι ο αποκλειστικός εισαγωγέας. Οι πωλήσεις ξεκινούν το πρώτο τρίμηνο του 2027, με "
         "τα ηλεκτρικά A290 και A390."),
        ("Πουλάτε μεταχειρισμένα;",
         "Η GA Motors στη Θεσσαλονίκη πουλά και επιλεγμένα μεταχειρισμένα. Για άλλες περιοχές, ο πελάτης ρωτά τον αντιπρόσωπο."),
        ("Έχετε επαγγελματικά οχήματα;",
         "Ναι: Renault Kangoo Van (από 26.680 € πλέον ΦΠΑ), Trafic Van (από 35.709 € πλέον ΦΠΑ), το ηλεκτρικό Trafic Van "
         "E-Tech, το Master (από 40.224 € πλέον ΦΠΑ) και το επιβατικό Trafic Combi (από 52.000 €)."),
        ("Ποιο αυτοκίνητο έχει 7 θέσεις;", "Το Dacia Jogger, από 24.200 €. Το Renault Trafic Combi μεταφέρει έως 9 επιβάτες."),
        ("Πουλάτε Nissan, Ford, Hyundai ή MG στην Ελλάδα;",
         "Όχι. Αυτές τις μάρκες ο όμιλος Grand Automotive τις έχει σε άλλες χώρες. Στην Ελλάδα: Renault, Dacia, INEOS και, από "
         "το 2027, Alpine."),
        ("Σε ποιες χώρες είναι η Grand Automotive;",
         "Αυστρία, Τσεχία, Σλοβακία, Σλοβενία, Κροατία, Βουλγαρία, Ουγγαρία, Σερβία, Βόρεια Μακεδονία, Βοσνία-Ερζεγοβίνη, "
         "Αλβανία, Μαυροβούνιο, Κόσοβο, Ελλάδα και Κύπρος."),
        ("Τι γίνεται στην Κύπρο;",
         "Ο όμιλος δηλώνει την INEOS στην Κύπρο. Δεν έχουμε στοιχεία καταστήματος εκεί: φόρμα επικοινωνίας στο "
         "grandautomotive.eu/contact-us ή ineosgrenadier.com."),
        ("Πώς κάνω κράτηση για το Renault 5 Turbo 3E;",
         "Μέσω του renault.gr (επικοινωνία για προ-παραγγελία), με ποσό κράτησης 50.000 €. Θα κατασκευαστούν μόνο 1.980 "
         "αυτοκίνητα, με εκτιμώμενη τιμή 160.000 € και παραδόσεις μέσα στο 2027."),
        ("Πόσο γρήγορα φορτίζει το Renault 5;",
         "Σε ταχυφορτιστή DC από 15% σε 80% σε περίπου 30 λεπτά. Σε wallbox 11 kW, περίπου 2,5 έως 3,2 ώρες, ανάλογα με "
         "την μπαταρία."),
        ("Πού αγοράζω βεβαιώσεις για το αυτοκίνητό μου;", "Online στο e-services.grandautomotive.gr."),
        ("Ποιος είναι ο CEO της Grand Automotive Hellas;", "Ο κ. Στήβεν Σίρτης."),
    ]
    story = header("Συχνές ερωτήσεις", "Σύντομες απαντήσεις στις πιο συχνές ερωτήσεις πελατών. Frequently asked questions.")
    story += qa(pairs)
    build("06_GA_FAQ.pdf", story, "Συχνές ερωτήσεις")


if __name__ == "__main__":
    doc_company()
    doc_renault()
    doc_dacia()
    doc_network()
    doc_aftersales()
    doc_faq()
