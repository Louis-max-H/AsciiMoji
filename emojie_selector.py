# coding=utf-8
import sys
from ncurses_function import *

try:
    import curses
except ImportError:
    sys.exit("""You need curses, it's a default module on Linux, it's time to join the great side of the open-source project ! If needed: https://pypi.org/project/windows-curses/""")

try:
    import pyperclip
except ImportError:
    sys.exit("""You need pyperclip to get ascii emojies, try pip install pyperclip on your terminal""")


def main(stdscr):
    with open('emojies.txt', 'r') as f:
        emojies = eval(f.read())
    emojies = [line for line in emojies if len(line) == 2]

    stdscr.clear()
    stdscr.refresh()
    stdscr.keypad(True)
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1 + 0 + 0, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Cursor
    curses.init_pair(0 + 2 + 0, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Focus
    curses.init_pair(1 + 2 + 0, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Cursor focus
    curses.init_pair(0 + 0 + 4, curses.COLOR_RED, curses.COLOR_BLACK)  # Selected
    curses.init_pair(1 + 0 + 4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Cursor selected
    curses.init_pair(0 + 2 + 4, curses.COLOR_RED, curses.COLOR_BLACK)  # Focus selected
    curses.init_pair(1 + 2 + 4, curses.COLOR_BLACK, curses.COLOR_MAGENTA)  # Cursor focus selected
    curses.init_pair(0 + 0 + 0 + 8, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Default
    stdscr.attron(curses.color_pair(8))

    height, width = stdscr.getmaxyx()
    panel = ChoicePanel(height, width, 0, 0)
    panel.set_content(emojies)
    panel.set_focus(True)

    k = 0
    while not (k == ord('q') and panel.win_select.focus):
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        panel.add_keys(k)

        stdscr.refresh()
        panel.reload()
        stdscr.refresh()

        if k in (curses.KEY_ENTER, ord("\n")):
            pyperclip.copy(panel.selected())

        k = stdscr.getch()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        sys.exit(1)
