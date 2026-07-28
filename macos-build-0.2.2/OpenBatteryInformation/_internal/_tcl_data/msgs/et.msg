# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset et DAYS_OF_WEEK_ABBREV [list \
        "P"\
        "E"\
        "T"\
        "K"\
        "N"\
        "R"\
        "L"]
    ::msgcat::mcset et DAYS_OF_WEEK_FULL [list \
        "pühapäev"\
        "esmaspäev"\
        "teisipäev"\
        "kolmapäev"\
        "neljapäev"\
        "reede"\
        "laupäev"]
    ::msgcat::mcset et MONTHS_ABBREV [list \
        "Jaan"\
        "Veebr"\
        "Märts"\
        "Apr"\
        "Mai"\
        "Juuni"\
        "Juuli"\
        "Aug"\
        "Sept"\
        "Okt"\
        "Nov"\
        "Dets"\
        ""]
    ::msgcat::mcset et MONTHS_FULL [list \
        "Jaanuar"\
        "Veebruar"\
        "Märts"\
        "Aprill"\
        "Mai"\
        "Juuni"\
        "Juuli"\
        "August"\
        "September"\
        "Oktoober"\
        "November"\
        "Detsember"\
        ""]
    ::msgcat::mcset et BCE "e.m.a."
    ::msgcat::mcset et CE "m.a.j."
    ::msgcat::mcset et DATE_FORMAT "%e-%m-%Y"
    ::msgcat::mcset et TIME_FORMAT "%k:%M:%S"
    ::msgcat::mcset et DATE_TIME_FORMAT "%e-%m-%Y %k:%M:%S %z"
}
