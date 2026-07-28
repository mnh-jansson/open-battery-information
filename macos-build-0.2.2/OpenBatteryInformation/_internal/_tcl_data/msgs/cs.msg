# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset cs DAYS_OF_WEEK_ABBREV [list \
        "Ne"\
        "Po"\
        "Út"\
        "St"\
        "Čt"\
        "Pá"\
        "So"]
    ::msgcat::mcset cs DAYS_OF_WEEK_FULL [list \
        "Neděle"\
        "Pondělí"\
        "Úterý"\
        "Středa"\
        "Čtvrtek"\
        "Pátek"\
        "Sobota"]
    ::msgcat::mcset cs MONTHS_ABBREV [list \
        "I"\
        "II"\
        "III"\
        "IV"\
        "V"\
        "VI"\
        "VII"\
        "VIII"\
        "IX"\
        "X"\
        "XI"\
        "XII"\
        ""]
    ::msgcat::mcset cs MONTHS_FULL [list \
        "leden"\
        "únor"\
        "březen"\
        "duben"\
        "květen"\
        "červen"\
        "červenec"\
        "srpen"\
        "září"\
        "říjen"\
        "listopad"\
        "prosinec"\
        ""]
    ::msgcat::mcset cs BCE "př.Kr."
    ::msgcat::mcset cs CE "po Kr."
    ::msgcat::mcset cs AM "dop."
    ::msgcat::mcset cs PM "odp."
    ::msgcat::mcset cs DATE_FORMAT "%e.%m.%Y"
    ::msgcat::mcset cs TIME_FORMAT "%k:%M:%S"
    ::msgcat::mcset cs DATE_TIME_FORMAT "%e.%m.%Y %k:%M:%S %z"
}
