# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset es DAYS_OF_WEEK_ABBREV [list \
        "dom"\
        "lun"\
        "mar"\
        "mié"\
        "jue"\
        "vie"\
        "sáb"]
    ::msgcat::mcset es DAYS_OF_WEEK_FULL [list \
        "domingo"\
        "lunes"\
        "martes"\
        "miércoles"\
        "jueves"\
        "viernes"\
        "sábado"]
    ::msgcat::mcset es MONTHS_ABBREV [list \
        "ene"\
        "feb"\
        "mar"\
        "abr"\
        "may"\
        "jun"\
        "jul"\
        "ago"\
        "sep"\
        "oct"\
        "nov"\
        "dic"\
        ""]
    ::msgcat::mcset es MONTHS_FULL [list \
        "enero"\
        "febrero"\
        "marzo"\
        "abril"\
        "mayo"\
        "junio"\
        "julio"\
        "agosto"\
        "septiembre"\
        "octubre"\
        "noviembre"\
        "diciembre"\
        ""]
    ::msgcat::mcset es BCE "a.C."
    ::msgcat::mcset es CE "d.C."
    ::msgcat::mcset es DATE_FORMAT "%e de %B de %Y"
    ::msgcat::mcset es TIME_FORMAT "%k:%M:%S"
    ::msgcat::mcset es DATE_TIME_FORMAT "%e de %B de %Y %k:%M:%S %z"
}
