# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset hr DAYS_OF_WEEK_ABBREV [list \
        "ned"\
        "pon"\
        "uto"\
        "sri"\
        "čet"\
        "pet"\
        "sub"]
    ::msgcat::mcset hr DAYS_OF_WEEK_FULL [list \
        "nedjelja"\
        "ponedjeljak"\
        "utorak"\
        "srijeda"\
        "četvrtak"\
        "petak"\
        "subota"]
    ::msgcat::mcset hr MONTHS_ABBREV [list \
        "sij"\
        "vel"\
        "ožu"\
        "tra"\
        "svi"\
        "lip"\
        "srp"\
        "kol"\
        "ruj"\
        "lis"\
        "stu"\
        "pro"\
        ""]
    ::msgcat::mcset hr MONTHS_FULL [list \
        "siječanj"\
        "veljača"\
        "ožujak"\
        "travanj"\
        "svibanj"\
        "lipanj"\
        "srpanj"\
        "kolovoz"\
        "rujan"\
        "listopad"\
        "studeni"\
        "prosinac"\
        ""]
    ::msgcat::mcset hr DATE_FORMAT "%Y.%m.%d"
    ::msgcat::mcset hr TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset hr DATE_TIME_FORMAT "%Y.%m.%d %H:%M:%S %z"
}
