#
# Aqua theme (OSX native look and feel)
#

namespace eval ttk::theme::aqua {

    # ttk::theme::aqua::setInactiveSelectBgColor --
    #
    # Sets the default selection background color for the widget styles
    # TEntry, TCombobox, and TSpinbox in the "!focus" state.

    proc setInactiveSelectBgColor {} {
	lassign [winfo rgb . systemUnemphasizedSelectedTextBackgroundColor] \
	    r g b
	if {$r != 32767} {
	    # macOS 10.14+
	    set inactiveSelBg systemUnemphasizedSelectedTextBackgroundColor
	} else {
	    # macOS 10.13
	    set inactiveSelBg systemWindowBackgroundColor2
	}

	# For Entry, Combobox and Spinbox widgets the selected text background
	# is the "Highlight color" selected in preferences when the widget has
	# focus.  It is a light gray color when the widget does not have focus
	# or is in background state.  (The background state implies !focus so
	# we only need to specify !focus.)
	#
	foreach style {TEntry TCombobox TSpinbox} {
	    ttk::style map $style -selectbackground [list !focus $inactiveSelBg]
	}

	# Override the dark gray color produced on macOS 10.13 by the
	# default value systemUnemphasizedSelectedTextBackgroundColor
	# of the text widget's -inactiveselectbackground option
	#
	option add *Text.inactiveSelectBackground \
	    $inactiveSelBg widgetDefault
    }

    # ttk::theme::aqua::setTreeviewAndListboxSelectColors --
    #
    # Sets the default selection background and foreground colors for
    # ttk::treeview and listbox widgets.

    proc setTreeviewAndListboxSelectColors {} {
	if {[catch {winfo rgb . systemSelectedContentBackgroundColor}] == 0} {
	    # macOS 10.14+
	    set selectedBg	systemSelectedContentBackgroundColor
	    set inactiveSelBg	systemUnemphasizedSelectedContentBackgroundColor
	} else {
	    # macOS 10.13
	    set selectedBg	systemHighlightAlternate
	    set inactiveSelBg	systemWindowBackgroundColor2
	}
	set selectedFg		systemAlternateSelectedControlTextColor
	set inactiveSelFg	systemSelectedControlTextColor

	# The treeview uses the "background" state for selected
	# items when the widget has lost the focus.  Hence the
	# following code sets different default selection colors
	# depending on whether the widget has the focus or not.
	#
	ttk::style map Treeview \
	    -background [list background $inactiveSelBg selected $selectedBg] \
	    -foreground [list background $inactiveSelFg selected $selectedFg]

	option add *Listbox.selectBackground	$selectedBg widgetDefault
	option add *Listbox.selectForeground	$selectedFg widgetDefault
    }

    ttk::style theme settings aqua {

	ttk::style configure . \
	    -font TkDefaultFont \
	    -background systemWindowBackgroundColor \
	    -foreground systemLabelColor \
	    -selectbackground systemSelectedTextBackgroundColor \
	    -selectforeground systemSelectedTextColor \
	    -insertwidth 1

	ttk::style map . \
	    -foreground {
		disabled systemDisabledControlTextColor
		background systemLabelColor} \
	    -selectbackground {
		background systemSelectedTextBackgroundColor
		!focus systemSelectedTextBackgroundColor} \
	    -selectforeground {
		background systemSelectedTextColor
		!focus systemSelectedTextColor}

	# Button
	ttk::style configure TButton -anchor center \
	    -foreground systemControlTextColor
	ttk::style map TButton \
	    -foreground {
		pressed white
		{alternate !pressed !background} white
		disabled systemDisabledControlTextColor}

	# Menubutton
	ttk::style configure TMenubutton -anchor center -padding {2 0 0 2}

	# Toolbutton
	ttk::style configure Toolbutton -anchor center

	# Inline Button
	ttk::style configure InlineButton -anchor center -font TkHeadingFont \
	    -foreground systemTextBackgroundColor
	ttk::style map InlineButton \
	    -foreground {
		disabled systemWindowBackgroundColor
	    }

	# Image Button
	ttk::style configure ImageButton -anchor center -width 1 \
	    -compound top
	ttk::style map ImageButton \
	    -foreground {
		pressed systemLabelColor
		!pressed systemSecondaryLabelColor
	    }

	# Recessed (radio) button
	font create RecessedFont -family EmphasizedSystem -size 11 -weight bold
	ttk::style configure RecessedButton \
	    -foreground systemControlTextColor
	ttk::style map RecessedButton \
	    -foreground {
		{disabled selected} systemWindowBackgroundColor3
		{disabled !selected} systemDisabledControlTextColor
		selected systemTextBackgroundColor
		active white
		pressed white
	    } \
	    -font {
		selected RecessedFont
		active RecessedFont
		pressed RecessedFont
	    }

	# Sidebar (radio) button
	font create SidebarFont -family .AppleSystemUIFont -size 11 \
	    -weight normal
	ttk::style configure SidebarButton \
	    -foreground systemControlTextColor \
	    -font SidebarFont
	ttk::style map SidebarButton \
	    -foreground {
		{disabled selected} systemWindowBackgroundColor3
		{disabled !selected} systemDisabledControlTextColor
		selected systemTextColor
		active systemTextColor
		pressed systemTextColor
	    }

	# Entry
	ttk::style configure TEntry \
	    -foreground systemTextColor \
	    -background systemTextBackgroundColor
	ttk::style map TEntry \
	    -foreground {disabled systemDisabledControlTextColor}

	# Combobox
	ttk::style map TCombobox \
	    -foreground {disabled systemDisabledControlTextColor}

	# Spinbox
	ttk::style configure TSpinbox \
	    -foreground systemTextColor \
	    -background systemTextBackgroundColor
	ttk::style map TSpinbox \
	    -foreground {disabled systemDisabledControlTextColor}

	setInactiveSelectBgColor	;# for TEntry, TCombobox, and TSpinbox

	# Workaround for #1100117:
	# Actually, on Aqua we probably shouldn't stipple images in
	# disabled buttons even if it did work...
	ttk::style configure . -stipple {}

	# Notebook
	ttk::style configure TNotebook -tabmargins {10 0} -tabposition n
	ttk::style configure TNotebook -padding {18 8 18 17}
	ttk::style configure TNotebook.Tab -padding {12 3 12 2}
	ttk::style configure TNotebook.Tab -foreground systemControlTextColor
	ttk::style map TNotebook.Tab \
	    -foreground {
		{background !selected} systemControlTextColor
		{background selected} black
		{!background selected} systemSelectedTabTextColor
		disabled systemDisabledControlTextColor}

	# Treeview
	ttk::style configure Heading \
	    -font TkHeadingFont \
	    -foreground systemTextColor \
	    -background systemWindowBackgroundColor
	ttk::style configure Treeview -rowheight 18 \
	    -background systemControlBackgroundColor \
	    -stripedbackground systemControlAlternatingRowColor \
	    -foreground systemTextColor \
	    -fieldbackground systemTextBackgroundColor
	setTreeviewAndListboxSelectColors

	# Enable animation for ttk::progressbar widget:
	ttk::style configure TProgressbar -period 100 -maxphase 120

	# For Aqua, labelframe labels should appear outside the border,
	# with a 14 pixel inset and 4 pixels spacing between border and label
	# (ref: Apple Human Interface Guidelines / Controls / Grouping Controls)
	#
	ttk::style configure TLabelframe \
	    -labeloutside true \
	    -labelmargins {14 0 14 2}

	ttk::style configure TLabelframe.Label \
	    -font TkSmallCaptionFont

	# TODO: panedwindow sashes should be 9 pixels (HIG:Controls:Split Views)
    }
}

# ttk::theme::aqua::configureNotebookStyle --
#
# Sets theme-specific option values for the ttk::notebook style $style and the
# style $style.Tab.  Invoked by ::ttk::configureNotebookStyle.

proc ttk::theme::aqua::configureNotebookStyle {style} {
    set tabPos [ttk::style lookup $style -tabposition {} nw]
    switch -- [string index $tabPos 0] {
	n {
	    ttk::style configure $style -tabmargins {10 0}
	    ttk::style configure $style.Tab -padding {12 3 12 2}
	}
	s {
	    ttk::style configure $style -tabmargins {10 0}
	    ttk::style configure $style.Tab -padding {12 2 12 3}
	}
	w {
	    ttk::style configure $style -tabmargins {0 10}
	    ttk::style configure $style.Tab -padding {3 12 2 12}
	}
	e {
	    ttk::style configure $style -tabmargins {0 10}
	    ttk::style configure $style.Tab -padding {2 12 3 12}
	}
	default {
	    ttk::style configure $style -tabmargins {10 0}
	    ttk::style configure $style.Tab -padding {12 3 12 2}
	}
    }
}
