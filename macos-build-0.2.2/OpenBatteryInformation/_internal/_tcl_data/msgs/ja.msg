# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset ja DAYS_OF_WEEK_ABBREV [list \
        "日"\
        "月"\
        "火"\
        "水"\
        "木"\
        "金"\
        "土"]
    ::msgcat::mcset ja DAYS_OF_WEEK_FULL [list \
        "日曜日"\
        "月曜日"\
        "火曜日"\
        "水曜日"\
        "木曜日"\
        "金曜日"\
        "土曜日"]
    ::msgcat::mcset ja MONTHS_FULL [list \
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
        "12月"]
    ::msgcat::mcset ja BCE "紀元前"
    ::msgcat::mcset ja CE "西暦"
    ::msgcat::mcset ja AM "午前"
    ::msgcat::mcset ja PM "午後"
    ::msgcat::mcset ja DATE_FORMAT "%Y/%m/%d"
    ::msgcat::mcset ja TIME_FORMAT "%k:%M:%S"
    ::msgcat::mcset ja TIME_FORMAT_12 "%P %I:%M:%S"
    ::msgcat::mcset ja DATE_TIME_FORMAT "%Y/%m/%d %k:%M:%S %z"
    ::msgcat::mcset ja LOCALE_DATE_FORMAT "%EY年%m月%d日"
    ::msgcat::mcset ja LOCALE_TIME_FORMAT "%H時%M分%S秒"
    ::msgcat::mcset ja LOCALE_DATE_TIME_FORMAT "%EY年%m月%d日 (%a) %H時%M分%S秒 %z"
    ::msgcat::mcset ja LOCALE_ERAS "{-9223372036854775808 西暦 0} {-3061011600 明治 1867} {-1812186000 大正 1911} {-1357635600 昭和 1925} {600220800 平成 1988} {1556668800 令和 2018}"
}
