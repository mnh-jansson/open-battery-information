# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset ro DAYS_OF_WEEK_ABBREV [list \
        "D"\
        "L"\
        "Ma"\
        "Mi"\
        "J"\
        "V"\
        "S"]
    ::msgcat::mcset ro DAYS_OF_WEEK_FULL [list \
        "duminică"\
        "luni"\
        "marţi"\
        "miercuri"\
        "joi"\
        "vineri"\
        "sîmbătă"]
    ::msgcat::mcset ro MONTHS_ABBREV [list \
        "Ian"\
        "Feb"\
        "Mar"\
        "Apr"\
        "Mai"\
        "Iun"\
        "Iul"\
        "Aug"\
        "Sep"\
        "Oct"\
        "Nov"\
        "Dec"\
        ""]
    ::msgcat::mcset ro MONTHS_FULL [list \
        "ianuarie"\
        "februarie"\
        "martie"\
        "aprilie"\
        "mai"\
        "iunie"\
        "iulie"\
        "august"\
        "septembrie"\
        "octombrie"\
        "noiembrie"\
        "decembrie"\
        ""]
    ::msgcat::mcset ro BCE "d.C."
    ::msgcat::mcset ro CE "î.d.C."
    ::msgcat::mcset ro DATE_FORMAT "%d.%m.%Y"
    ::msgcat::mcset ro TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset ro DATE_TIME_FORMAT "%d.%m.%Y %H:%M:%S %z"
}
