# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset lv DAYS_OF_WEEK_ABBREV [list \
        "Sv"\
        "P"\
        "O"\
        "T"\
        "C"\
        "Pk"\
        "S"]
    ::msgcat::mcset lv DAYS_OF_WEEK_FULL [list \
        "svētdiena"\
        "pirmdiena"\
        "otrdiena"\
        "trešdiena"\
        "ceturdien"\
        "piektdiena"\
        "sestdiena"]
    ::msgcat::mcset lv MONTHS_ABBREV [list \
        "Jan"\
        "Feb"\
        "Mar"\
        "Apr"\
        "Maijs"\
        "Jūn"\
        "Jūl"\
        "Aug"\
        "Sep"\
        "Okt"\
        "Nov"\
        "Dec"\
        ""]
    ::msgcat::mcset lv MONTHS_FULL [list \
        "janvāris"\
        "februāris"\
        "marts"\
        "aprīlis"\
        "maijs"\
        "jūnijs"\
        "jūlijs"\
        "augusts"\
        "septembris"\
        "oktobris"\
        "novembris"\
        "decembris"\
        ""]
    ::msgcat::mcset lv BCE "pmē"
    ::msgcat::mcset lv CE "mē"
    ::msgcat::mcset lv DATE_FORMAT "%Y.%e.%m"
    ::msgcat::mcset lv TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset lv DATE_TIME_FORMAT "%Y.%e.%m %H:%M:%S %z"
}
