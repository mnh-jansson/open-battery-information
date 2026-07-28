# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset mk DAYS_OF_WEEK_ABBREV [list \
        "нед."\
        "пон."\
        "вт."\
        "сре."\
        "чет."\
        "пет."\
        "саб."]
    ::msgcat::mcset mk DAYS_OF_WEEK_FULL [list \
        "недела"\
        "понеделник"\
        "вторник"\
        "среда"\
        "четврток"\
        "петок"\
        "сабота"]
    ::msgcat::mcset mk MONTHS_ABBREV [list \
        "јан."\
        "фев."\
        "мар."\
        "апр."\
        "мај."\
        "јун."\
        "јул."\
        "авг."\
        "септ."\
        "окт."\
        "ноем."\
        "декем."\
        ""]
    ::msgcat::mcset mk MONTHS_FULL [list \
        "јануари"\
        "февруари"\
        "март"\
        "април"\
        "мај"\
        "јуни"\
        "јули"\
        "август"\
        "септември"\
        "октомври"\
        "ноември"\
        "декември"\
        ""]
    ::msgcat::mcset mk BCE "пр.н.е."
    ::msgcat::mcset mk CE "ае."
    ::msgcat::mcset mk DATE_FORMAT "%e.%m.%Y"
    ::msgcat::mcset mk TIME_FORMAT "%H:%M:%S %z"
    ::msgcat::mcset mk DATE_TIME_FORMAT "%e.%m.%Y %H:%M:%S %z %z"
}
