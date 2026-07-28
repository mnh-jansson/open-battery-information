# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset is DAYS_OF_WEEK_ABBREV [list \
        "sun."\
        "mán."\
        "þri."\
        "mið."\
        "fim."\
        "fös."\
        "lau."]
    ::msgcat::mcset is DAYS_OF_WEEK_FULL [list \
        "sunnudagur"\
        "mánudagur"\
        "þriðjudagur"\
        "miðvikudagur"\
        "fimmtudagur"\
        "föstudagur"\
        "laugardagur"]
    ::msgcat::mcset is MONTHS_ABBREV [list \
        "jan."\
        "feb."\
        "mar."\
        "apr."\
        "maí"\
        "jún."\
        "júl."\
        "ágú."\
        "sep."\
        "okt."\
        "nóv."\
        "des."\
        ""]
    ::msgcat::mcset is MONTHS_FULL [list \
        "janúar"\
        "febrúar"\
        "mars"\
        "apríl"\
        "maí"\
        "júní"\
        "júlí"\
        "ágúst"\
        "september"\
        "október"\
        "nóvember"\
        "desember"\
        ""]
    ::msgcat::mcset is DATE_FORMAT "%e.%m.%Y"
    ::msgcat::mcset is TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset is DATE_TIME_FORMAT "%e.%m.%Y %H:%M:%S %z"
}
