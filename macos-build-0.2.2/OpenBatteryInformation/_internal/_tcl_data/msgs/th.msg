# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset th DAYS_OF_WEEK_ABBREV [list \
        "อา."\
        "จ."\
        "อ."\
        "พ."\
        "พฤ."\
        "ศ."\
        "ส."]
    ::msgcat::mcset th DAYS_OF_WEEK_FULL [list \
        "วันอาทิตย์"\
        "วันจันทร์"\
        "วันอังคาร"\
        "วันพุธ"\
        "วันพฤหัสบดี"\
        "วันศุกร์"\
        "วันเสาร์"]
    ::msgcat::mcset th MONTHS_ABBREV [list \
        "ม.ค."\
        "ก.พ."\
        "มี.ค."\
        "เม.ย."\
        "พ.ค."\
        "มิ.ย."\
        "ก.ค."\
        "ส.ค."\
        "ก.ย."\
        "ต.ค."\
        "พ.ย."\
        "ธ.ค."\
        ""]
    ::msgcat::mcset th MONTHS_FULL [list \
        "มกราคม"\
        "กุมภาพันธ์"\
        "มีนาคม"\
        "เมษายน"\
        "พฤษภาคม"\
        "มิถุนายน"\
        "กรกฎาคม"\
        "สิงหาคม"\
        "กันยายน"\
        "ตุลาคม"\
        "พฤศจิกายน"\
        "ธันวาคม"\
        ""]
    ::msgcat::mcset th BCE "ลที่"
    ::msgcat::mcset th CE "ค.ศ."
    ::msgcat::mcset th AM "ก่อนเที่ยง"
    ::msgcat::mcset th PM "หลังเที่ยง"
    ::msgcat::mcset th DATE_FORMAT "%e/%m/%Y"
    ::msgcat::mcset th TIME_FORMAT "%k:%M:%S"
    ::msgcat::mcset th DATE_TIME_FORMAT "%e/%m/%Y %k:%M:%S %z"
}
