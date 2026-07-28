# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset sk DAYS_OF_WEEK_ABBREV [list \
        "Ne"\
        "Po"\
        "Ut"\
        "St"\
        "Št"\
        "Pa"\
        "So"]
    ::msgcat::mcset sk DAYS_OF_WEEK_FULL [list \
        "Nedeľe"\
        "Pondelok"\
        "Utorok"\
        "Streda"\
        "Štvrtok"\
        "Piatok"\
        "Sobota"]
    ::msgcat::mcset sk MONTHS_ABBREV [list \
        "jan"\
        "feb"\
        "mar"\
        "apr"\
        "máj"\
        "jún"\
        "júl"\
        "aug"\
        "sep"\
        "okt"\
        "nov"\
        "dec"\
        ""]
    ::msgcat::mcset sk MONTHS_FULL [list \
        "január"\
        "február"\
        "marec"\
        "apríl"\
        "máj"\
        "jún"\
        "júl"\
        "august"\
        "september"\
        "október"\
        "november"\
        "december"\
        ""]
    ::msgcat::mcset sk BCE "pred n.l."
    ::msgcat::mcset sk CE "n.l."
    ::msgcat::mcset sk DATE_FORMAT "%e.%m.%Y"
    ::msgcat::mcset sk TIME_FORMAT "%k:%M:%S"
    ::msgcat::mcset sk DATE_TIME_FORMAT "%e.%m.%Y %k:%M:%S %z"
}
