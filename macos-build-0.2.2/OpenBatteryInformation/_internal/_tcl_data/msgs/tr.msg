# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset tr DAYS_OF_WEEK_ABBREV [list \
        "Paz"\
        "Pzt"\
        "Sal"\
        "Çar"\
        "Per"\
        "Cum"\
        "Cmt"]
    ::msgcat::mcset tr DAYS_OF_WEEK_FULL [list \
        "Pazar"\
        "Pazartesi"\
        "Salı"\
        "Çarşamba"\
        "Perşembe"\
        "Cuma"\
        "Cumartesi"]
    ::msgcat::mcset tr MONTHS_ABBREV [list \
        "Oca"\
        "Şub"\
        "Mar"\
        "Nis"\
        "May"\
        "Haz"\
        "Tem"\
        "Ağu"\
        "Eyl"\
        "Eki"\
        "Kas"\
        "Ara"\
        ""]
    ::msgcat::mcset tr MONTHS_FULL [list \
        "Ocak"\
        "Şubat"\
        "Mart"\
        "Nisan"\
        "Mayıs"\
        "Haziran"\
        "Temmuz"\
        "Ağustos"\
        "Eylül"\
        "Ekim"\
        "Kasım"\
        "Aralık"\
        ""]
    ::msgcat::mcset tr DATE_FORMAT "%d.%m.%Y"
    ::msgcat::mcset tr TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset tr DATE_TIME_FORMAT "%d.%m.%Y %H:%M:%S %z"
}
