if {![package vsatisfies [package provide Tcl] 9.0]} return
    package ifneeded tk 9.0.4 [list load [file normalize [file join $dir .. libtcl9tk9.0.dylib]]]
package ifneeded Tk 9.0.4 [list package require -exact tk 9.0.4]
