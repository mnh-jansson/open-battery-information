# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset ko DAYS_OF_WEEK_ABBREV [list \
        "일"\
        "월"\
        "화"\
        "수"\
        "목"\
        "금"\
        "토"]
    ::msgcat::mcset ko DAYS_OF_WEEK_FULL [list \
        "일요일"\
        "월요일"\
        "화요일"\
        "수요일"\
        "목요일"\
        "금요일"\
        "토요일"]
    ::msgcat::mcset ko MONTHS_ABBREV [list \
        "1월"\
        "2월"\
        "3월"\
        "4월"\
        "5월"\
        "6월"\
        "7월"\
        "8월"\
        "9월"\
        "10월"\
        "11월"\
        "12월"\
        ""]
    ::msgcat::mcset ko MONTHS_FULL [list \
        "1월"\
        "2월"\
        "3월"\
        "4월"\
        "5월"\
        "6월"\
        "7월"\
        "8월"\
        "9월"\
        "10월"\
        "11월"\
        "12월"\
        ""]
    ::msgcat::mcset ko AM "오전"
    ::msgcat::mcset ko PM "오후"
    ::msgcat::mcset ko DATE_FORMAT "%Y-%m-%d"
    ::msgcat::mcset ko TIME_FORMAT_12 "%P %l:%M:%S"
    ::msgcat::mcset ko DATE_TIME_FORMAT "%Y-%m-%d %P %l:%M:%S %z"
    ::msgcat::mcset ko LOCALE_DATE_FORMAT "%Y년%B%Od일"
    ::msgcat::mcset ko LOCALE_TIME_FORMAT "%H시%M분%S초"
    ::msgcat::mcset ko LOCALE_DATE_TIME_FORMAT "%A %Y년%B%Od일%H시%M분%S초 %z"
}
