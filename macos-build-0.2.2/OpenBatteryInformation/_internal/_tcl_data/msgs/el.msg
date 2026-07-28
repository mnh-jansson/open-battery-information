# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset el DAYS_OF_WEEK_ABBREV [list \
        "Κυρ"\
        "Δευ"\
        "Τρι"\
        "Τετ"\
        "Πεμ"\
        "Παρ"\
        "Σαβ"]
    ::msgcat::mcset el DAYS_OF_WEEK_FULL [list \
        "Κυριακή"\
        "Δευτέρα"\
        "Τρίτη"\
        "Τετάρτη"\
        "Πέμπτη"\
        "Παρασκευή"\
        "Σάββατο"]
    ::msgcat::mcset el MONTHS_ABBREV [list \
        "Ιαν"\
        "Φεβ"\
        "Μαρ"\
        "Απρ"\
        "Μαϊ"\
        "Ιουν"\
        "Ιουλ"\
        "Αυγ"\
        "Σεπ"\
        "Οκτ"\
        "Νοε"\
        "Δεκ"\
        ""]
    ::msgcat::mcset el MONTHS_FULL [list \
        "Ιανουάριος"\
        "Φεβρουάριος"\
        "Μάρτιος"\
        "Απρίλιος"\
        "Μάϊος"\
        "Ιούνιος"\
        "Ιούλιος"\
        "Αύγουστος"\
        "Σεπτέμβριος"\
        "Οκτώβριος"\
        "Νοέμβριος"\
        "Δεκέμβριος"\
        ""]
    ::msgcat::mcset el AM "πμ"
    ::msgcat::mcset el PM "μμ"
    ::msgcat::mcset el DATE_FORMAT "%e/%m/%Y"
    ::msgcat::mcset el TIME_FORMAT_12 "%l:%M:%S %P"
    ::msgcat::mcset el DATE_TIME_FORMAT "%e/%m/%Y %l:%M:%S %P %z"
}
