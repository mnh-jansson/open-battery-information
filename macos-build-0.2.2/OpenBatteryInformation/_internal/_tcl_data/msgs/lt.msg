# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset lt DAYS_OF_WEEK_ABBREV [list \
        "Sk"\
        "Pr"\
        "An"\
        "Tr"\
        "Kt"\
        "Pn"\
        "Št"]
    ::msgcat::mcset lt DAYS_OF_WEEK_FULL [list \
        "Sekmadienis"\
        "Pirmadienis"\
        "Antradienis"\
        "Trečiadienis"\
        "Ketvirtadienis"\
        "Penktadienis"\
        "Šeštadienis"]
    ::msgcat::mcset lt MONTHS_ABBREV [list \
        "Sau"\
        "Vas"\
        "Kov"\
        "Bal"\
        "Geg"\
        "Bir"\
        "Lie"\
        "Rgp"\
        "Rgs"\
        "Spa"\
        "Lap"\
        "Grd"\
        ""]
    ::msgcat::mcset lt MONTHS_FULL [list \
        "Sausio"\
        "Vasario"\
        "Kovo"\
        "Balandžio"\
        "Gegužės"\
        "Birželio"\
        "Liepos"\
        "Rugpjūčio"\
        "Rugsėjo"\
        "Spalio"\
        "Lapkričio"\
        "Gruodžio"\
        ""]
    ::msgcat::mcset lt BCE "pr.Kr."
    ::msgcat::mcset lt CE "po.Kr."
    ::msgcat::mcset lt DATE_FORMAT "%Y.%m.%e"
    ::msgcat::mcset lt TIME_FORMAT "%H.%M.%S"
    ::msgcat::mcset lt DATE_TIME_FORMAT "%Y.%m.%e %H.%M.%S %z"
}
