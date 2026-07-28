# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset zh_HK DAYS_OF_WEEK_ABBREV [list \
        "日"\
        "一"\
        "二"\
        "三"\
        "四"\
        "五"\
        "六"]
    ::msgcat::mcset zh_HK MONTHS_ABBREV [list \
        "1月"\
        "2月"\
        "3月"\
        "4月"\
        "5月"\
        "6月"\
        "7月"\
        "8月"\
        "9月"\
        "10月"\
        "11月"\
        "12月"\
        ""]
    ::msgcat::mcset zh_HK DATE_FORMAT "%Y年%m月%e日"
    ::msgcat::mcset zh_HK TIME_FORMAT_12 "%P%I:%M:%S"
    ::msgcat::mcset zh_HK DATE_TIME_FORMAT "%Y年%m月%e日 %P%I:%M:%S %z"
}
