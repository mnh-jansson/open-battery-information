# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset sq DAYS_OF_WEEK_ABBREV [list \
        "Die"\
        "Hën"\
        "Mar"\
        "Mër"\
        "Enj"\
        "Pre"\
        "Sht"]
    ::msgcat::mcset sq DAYS_OF_WEEK_FULL [list \
        "e diel"\
        "e hënë"\
        "e martë"\
        "e mërkurë"\
        "e enjte"\
        "e premte"\
        "e shtunë"]
    ::msgcat::mcset sq MONTHS_ABBREV [list \
        "Jan"\
        "Shk"\
        "Mar"\
        "Pri"\
        "Maj"\
        "Qer"\
        "Kor"\
        "Gsh"\
        "Sht"\
        "Tet"\
        "Nën"\
        "Dhj"\
        ""]
    ::msgcat::mcset sq MONTHS_FULL [list \
        "janar"\
        "shkurt"\
        "mars"\
        "prill"\
        "maj"\
        "qershor"\
        "korrik"\
        "gusht"\
        "shtator"\
        "tetor"\
        "nëntor"\
        "dhjetor"\
        ""]
    ::msgcat::mcset sq BCE "p.e.r."
    ::msgcat::mcset sq CE "n.e.r."
    ::msgcat::mcset sq AM "PD"
    ::msgcat::mcset sq PM "MD"
    ::msgcat::mcset sq DATE_FORMAT "%Y-%m-%d"
    ::msgcat::mcset sq TIME_FORMAT_12 "%l:%M:%S.%P"
    ::msgcat::mcset sq DATE_TIME_FORMAT "%Y-%m-%d %l:%M:%S.%P %z"
}
