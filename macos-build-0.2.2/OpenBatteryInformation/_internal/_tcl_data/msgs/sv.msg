# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset sv DAYS_OF_WEEK_ABBREV [list \
        "sö"\
        "må"\
        "ti"\
        "on"\
        "to"\
        "fr"\
        "lö"]
    ::msgcat::mcset sv DAYS_OF_WEEK_FULL [list \
        "söndag"\
        "måndag"\
        "tisdag"\
        "onsdag"\
        "torsdag"\
        "fredag"\
        "lördag"]
    ::msgcat::mcset sv MONTHS_ABBREV [list \
        "jan"\
        "feb"\
        "mar"\
        "apr"\
        "maj"\
        "jun"\
        "jul"\
        "aug"\
        "sep"\
        "okt"\
        "nov"\
        "dec"\
        ""]
    ::msgcat::mcset sv MONTHS_FULL [list \
        "januari"\
        "februari"\
        "mars"\
        "april"\
        "maj"\
        "juni"\
        "juli"\
        "augusti"\
        "september"\
        "oktober"\
        "november"\
        "december"\
        ""]
    ::msgcat::mcset sv BCE "f.Kr."
    ::msgcat::mcset sv CE "e.Kr."
    ::msgcat::mcset sv DATE_FORMAT "%Y-%m-%d"
    ::msgcat::mcset sv TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset sv DATE_TIME_FORMAT "%Y-%m-%d %H:%M:%S %z"
}
