# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset ar DAYS_OF_WEEK_ABBREV [list \
        "ح"\
        "ن"\
        "ث"\
        "ر"\
        "خ"\
        "ج"\
        "س"]
    ::msgcat::mcset ar DAYS_OF_WEEK_FULL [list \
        "الأحد"\
        "الاثنين"\
        "الثلاثاء"\
        "الأربعاء"\
        "الخميس"\
        "الجمعة"\
        "السبت"]
    ::msgcat::mcset ar MONTHS_ABBREV [list \
        "ينا"\
        "فبر"\
        "مار"\
        "أبر"\
        "ماي"\
        "يون"\
        "يول"\
        "أغس"\
        "سبت"\
        "أكت"\
        "نوف"\
        "ديس"\
        ""]
    ::msgcat::mcset ar MONTHS_FULL [list \
        "يناير"\
        "فبراير"\
        "مارس"\
        "أبريل"\
        "مايو"\
        "يونيو"\
        "يوليو"\
        "أغسطس"\
        "سبتمبر"\
        "أكتوبر"\
        "نوفمبر"\
        "ديسمبر"\
        ""]
    ::msgcat::mcset ar BCE "ق.م"
    ::msgcat::mcset ar CE "م"
    ::msgcat::mcset ar AM "ص"
    ::msgcat::mcset ar PM "م"
    ::msgcat::mcset ar DATE_FORMAT "%d/%m/%Y"
    ::msgcat::mcset ar TIME_FORMAT_12 "%I:%M:%S %P"
    ::msgcat::mcset ar DATE_TIME_FORMAT "%d/%m/%Y %I:%M:%S %P %z"
}
