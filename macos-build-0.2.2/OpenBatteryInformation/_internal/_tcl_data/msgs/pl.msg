# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset pl DAYS_OF_WEEK_ABBREV [list \
        "N"\
        "Pn"\
        "Wt"\
        "Śr"\
        "Cz"\
        "Pt"\
        "So"]
    ::msgcat::mcset pl DAYS_OF_WEEK_FULL [list \
        "niedziela"\
        "poniedziałek"\
        "wtorek"\
        "środa"\
        "czwartek"\
        "piątek"\
        "sobota"]
    ::msgcat::mcset pl MONTHS_ABBREV [list \
        "sty"\
        "lut"\
        "mar"\
        "kwi"\
        "maj"\
        "cze"\
        "lip"\
        "sie"\
        "wrz"\
        "paź"\
        "lis"\
        "gru"\
        ""]
    ::msgcat::mcset pl MONTHS_FULL [list \
        "styczeń"\
        "luty"\
        "marzec"\
        "kwiecień"\
        "maj"\
        "czerwiec"\
        "lipiec"\
        "sierpień"\
        "wrzesień"\
        "październik"\
        "listopad"\
        "grudzień"\
        ""]
    ::msgcat::mcset pl BCE "p.n.e."
    ::msgcat::mcset pl CE "n.e."
    ::msgcat::mcset pl DATE_FORMAT "%Y-%m-%d"
    ::msgcat::mcset pl TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset pl DATE_TIME_FORMAT "%Y-%m-%d %H:%M:%S %z"
}
