# created by tools/loadICU.tcl -- do not edit
namespace eval ::tcl::clock {
    ::msgcat::mcset be DAYS_OF_WEEK_ABBREV [list \
        "нд"\
        "пн"\
        "ат"\
        "ср"\
        "чц"\
        "пт"\
        "сб"]
    ::msgcat::mcset be DAYS_OF_WEEK_FULL [list \
        "нядзеля"\
        "панядзелак"\
        "аўторак"\
        "серада"\
        "чацвер"\
        "пятніца"\
        "субота"]
    ::msgcat::mcset be MONTHS_ABBREV [list \
        "стд"\
        "лют"\
        "скв"\
        "крс"\
        "май"\
        "чрв"\
        "лпн"\
        "жнв"\
        "врс"\
        "кст"\
        "лст"\
        "снж"\
        ""]
    ::msgcat::mcset be MONTHS_FULL [list \
        "студзеня"\
        "лютага"\
        "сакавіка"\
        "красавіка"\
        "мая"\
        "чрвеня"\
        "ліпеня"\
        "жніўня"\
        "верасня"\
        "кастрычніка"\
        "листапада"\
        "снежня"\
        ""]
    ::msgcat::mcset be BCE "да н.е."
    ::msgcat::mcset be CE "н.е."
    ::msgcat::mcset be DATE_FORMAT "%e.%m.%Y"
    ::msgcat::mcset be TIME_FORMAT "%k.%M.%S"
    ::msgcat::mcset be DATE_TIME_FORMAT "%e.%m.%Y %k.%M.%S %z"
}
