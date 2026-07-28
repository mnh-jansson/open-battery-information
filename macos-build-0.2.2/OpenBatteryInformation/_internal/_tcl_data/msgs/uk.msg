# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset uk DAYS_OF_WEEK_ABBREV [list \
        "нд"\
        "пн"\
        "вт"\
        "ср"\
        "чт"\
        "пт"\
        "сб"]
    ::msgcat::mcset uk DAYS_OF_WEEK_FULL [list \
        "неділя"\
        "понеділок"\
        "вівторок"\
        "середа"\
        "четвер"\
        "п'ятниця"\
        "субота"]
    ::msgcat::mcset uk MONTHS_ABBREV [list \
        "січ"\
        "лют"\
        "бер"\
        "квіт"\
        "трав"\
        "черв"\
        "лип"\
        "серп"\
        "вер"\
        "жовт"\
        "лист"\
        "груд"\
        ""]
    ::msgcat::mcset uk MONTHS_FULL [list \
        "січня"\
        "лютого"\
        "березня"\
        "квітня"\
        "травня"\
        "червня"\
        "липня"\
        "серпня"\
        "вересня"\
        "жовтня"\
        "листопада"\
        "грудня"\
        ""]
    ::msgcat::mcset uk BCE "до н.е."
    ::msgcat::mcset uk CE "після н.е."
    ::msgcat::mcset uk DATE_FORMAT "%e/%m/%Y"
    ::msgcat::mcset uk TIME_FORMAT "%k:%M:%S"
    ::msgcat::mcset uk DATE_TIME_FORMAT "%e/%m/%Y %k:%M:%S %z"
}
