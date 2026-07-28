# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset vi DAYS_OF_WEEK_ABBREV [list \
        "Th 2"\
        "Th 3"\
        "Th 4"\
        "Th 5"\
        "Th 6"\
        "Th 7"\
        "CN"]
    ::msgcat::mcset vi DAYS_OF_WEEK_FULL [list \
        "Thứ hai"\
        "Thứ ba"\
        "Thứ tư"\
        "Thứ năm"\
        "Thứ sáu"\
        "Thứ bảy"\
        "Chủ nhật"]
    ::msgcat::mcset vi MONTHS_ABBREV [list \
        "Thg 1"\
        "Thg 2"\
        "Thg 3"\
        "Thg 4"\
        "Thg 5"\
        "Thg 6"\
        "Thg 7"\
        "Thg 8"\
        "Thg 9"\
        "Thg 10"\
        "Thg 11"\
        "Thg 12"\
        ""]
    ::msgcat::mcset vi MONTHS_FULL [list \
        "Tháng một"\
        "Tháng hai"\
        "Tháng ba"\
        "Tháng tư"\
        "Tháng năm"\
        "Tháng sáu"\
        "Tháng bảy"\
        "Tháng tám"\
        "Tháng chín"\
        "Tháng mười"\
        "Tháng mười một"\
        "Tháng mười hai"\
        ""]
    ::msgcat::mcset vi DATE_FORMAT "%d %b %Y"
    ::msgcat::mcset vi TIME_FORMAT "%H:%M:%S"
    ::msgcat::mcset vi DATE_TIME_FORMAT "%d %b %Y %H:%M:%S %z"
}
