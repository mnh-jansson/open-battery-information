# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset bg DAYS_OF_WEEK_ABBREV [list \
        "Нд"\
        "Пн"\
        "Вт"\
        "Ср"\
        "Чт"\
        "Пт"\
        "Сб"]
    ::msgcat::mcset bg DAYS_OF_WEEK_FULL [list \
        "Неделя"\
        "Понеделник"\
        "Вторник"\
        "Сряда"\
        "Четвъртък"\
        "Петък"\
        "Събота"]
    ::msgcat::mcset bg MONTHS_ABBREV [list \
        "I"\
        "II"\
        "III"\
        "IV"\
        "V"\
        "VI"\
        "VII"\
        "VIII"\
        "IX"\
        "X"\
        "XI"\
        "XII"\
        ""]
    ::msgcat::mcset bg MONTHS_FULL [list \
        "Януари"\
        "Февруари"\
        "Март"\
        "Април"\
        "Май"\
        "Юни"\
        "Юли"\
        "Август"\
        "Септември"\
        "Октомври"\
        "Ноември"\
        "Декември"\
        ""]
    ::msgcat::mcset bg BCE "пр.н.е."
    ::msgcat::mcset bg CE "н.е."
    ::msgcat::mcset bg DATE_FORMAT "%Y-%m-%e"
    ::msgcat::mcset bg TIME_FORMAT "%k:%M:%S"
    ::msgcat::mcset bg DATE_TIME_FORMAT "%Y-%m-%e %k:%M:%S %z"
}
