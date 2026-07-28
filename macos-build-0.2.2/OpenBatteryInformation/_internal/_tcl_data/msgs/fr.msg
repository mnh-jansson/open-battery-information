# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset fr DAYS_OF_WEEK_ABBREV [list \
        "dim."\
        "lun."\
        "mar."\
        "mer."\
        "jeu."\
        "ven."\
        "sam."]
    ::msgcat::mcset fr DAYS_OF_WEEK_FULL [list \
        "dimanche"\
        "lundi"\
        "mardi"\
        "mercredi"\
        "jeudi"\
        "vendredi"\
        "samedi"]
    ::msgcat::mcset fr MONTHS_ABBREV [list \
        "janv."\
        "févr."\
        "mars"\
        "avr."\
        "mai"\
        "juin"\
        "juil."\
        "août"\
        "sept."\
        "oct."\
        "nov."\
        "déc."\
        ""]
    ::msgcat::mcset fr MONTHS_FULL [list \
        "janvier"\
        "février"\
        "mars"\
        "avril"\
        "mai"\
        "juin"\
        "juillet"\
        "août"\
        "septembre"\
        "octobre"\
        "novembre"\
        "décembre"\
        ""]
    ::msgcat::mcset fr BCE "av. J.-C."
    ::msgcat::mcset fr CE "ap. J.-C."
    ::msgcat::mcset fr DATE_FORMAT "%e %B %Y"
    ::msgcat::mcset fr TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset fr DATE_TIME_FORMAT "%e %B %Y %H:%M:%S %z"
}
