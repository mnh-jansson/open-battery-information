# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset he DAYS_OF_WEEK_ABBREV [list \
        "א"\
        "ב"\
        "ג"\
        "ד"\
        "ה"\
        "ו"\
        "ש"]
    ::msgcat::mcset he DAYS_OF_WEEK_FULL [list \
        "יום ראשון"\
        "יום שני"\
        "יום שלישי"\
        "יום רביעי"\
        "יום חמישי"\
        "יום שישי"\
        "שבת"]
    ::msgcat::mcset he MONTHS_ABBREV [list \
        "ינו"\
        "פבר"\
        "מרץ"\
        "אפר"\
        "מאי"\
        "יונ"\
        "יול"\
        "אוג"\
        "ספט"\
        "אוק"\
        "נוב"\
        "דצמ"\
        ""]
    ::msgcat::mcset he MONTHS_FULL [list \
        "ינואר"\
        "פברואר"\
        "מרץ"\
        "אפריל"\
        "מאי"\
        "יוני"\
        "יולי"\
        "אוגוסט"\
        "ספטמבר"\
        "אוקטובר"\
        "נובמבר"\
        "דצמבר"\
        ""]
    ::msgcat::mcset he BCE "לסה"נ"
    ::msgcat::mcset he CE "לפסה"נ"
    ::msgcat::mcset he DATE_FORMAT "%d/%m/%Y"
    ::msgcat::mcset he TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset he DATE_TIME_FORMAT "%d/%m/%Y %H:%M:%S %z"
}
