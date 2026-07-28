# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset sr DAYS_OF_WEEK_ABBREV [list \
        "Нед"\
        "Пон"\
        "Уто"\
        "Сре"\
        "Чет"\
        "Пет"\
        "Суб"]
    ::msgcat::mcset sr DAYS_OF_WEEK_FULL [list \
        "Недеља"\
        "Понедељак"\
        "Уторак"\
        "Среда"\
        "Четвртак"\
        "Петак"\
        "Субота"]
    ::msgcat::mcset sr MONTHS_ABBREV [list \
        "Јан"\
        "Феб"\
        "Мар"\
        "Апр"\
        "Мај"\
        "Јун"\
        "Јул"\
        "Авг"\
        "Сеп"\
        "Окт"\
        "Нов"\
        "Дец"\
        ""]
    ::msgcat::mcset sr MONTHS_FULL [list \
        "Јануар"\
        "Фебруар"\
        "Март"\
        "Април"\
        "Мај"\
        "Јуни"\
        "Јули"\
        "Август"\
        "Септембар"\
        "Октобар"\
        "Новембар"\
        "Децембар"\
        ""]
    ::msgcat::mcset sr BCE "п. н. е."
    ::msgcat::mcset sr CE "н. е"
    ::msgcat::mcset sr DATE_FORMAT "%Y.%m.%e"
    ::msgcat::mcset sr TIME_FORMAT "%k.%M.%S"
    ::msgcat::mcset sr DATE_TIME_FORMAT "%Y.%m.%e %k.%M.%S %z"
}
