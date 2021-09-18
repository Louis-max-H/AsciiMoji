# coding=utf-8
from math import floor, ceil
from ncurses_function import *
import sys
import os
sys.path.append(os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))))

try:
    import curses
except ImportError:
    sys.exit("""You need curses, it's a default module on Linux, it's time to join the great side of the open-source project ! If needed: https://pypi.org/project/windows-curses/""")

try:
    import pyperclip
except ImportError:
    sys.exit("""You need pyperclip to get ascii emojies, try pip install pyperclip on your terminal""")


def main(stdscr):
    emojies_element = {
        "ears": [],
        "eyes": [],
        "mouth": []
    }
    preview_to_element = {}
    with open('emojies_elements.txt', 'r') as f:
        for category, elements, preview, comment in eval(f.read()):
            emojies_element[category].append((preview, comment))
            preview_to_element[preview] = elements

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
    taille = [floor(width // 3), ceil(width // 3), floor(width // 3)]
    menus = (
        ChoicePanel(height - 3, taille[0], 2, 0),
        ChoicePanel(height - 3, taille[1], 2, taille[0]),
        ChoicePanel(height - 3, taille[2], 2, taille[0] + taille[1])
    )

    EARS, EYES, MOUTH = 0, 1, 2
    for index, categorie in enumerate(("ears", "eyes", "mouth")):
        menus[index].set_content(emojies_element[categorie])

    focus_index = 0
    menus[focus_index].set_focus(True)

    def get_emojie(menus, force_preview=False, preview_ears=False, preview_eyes=False, preview_mouth=False):
        if force_preview:
            return get_emojie(menus, preview_ears=True, preview_eyes=True, preview_mouth=True)
        ears = preview_to_element.get(
            menus[EARS].mousse_selected() if preview_ears else
            menus[EARS].selected(), [""]
        )
        eyes = preview_to_element.get(
            menus[EYES].mousse_selected() if preview_eyes else
            menus[EYES].selected(), [""]
        )
        mouth = preview_to_element.get(
            menus[MOUTH].mousse_selected() if preview_mouth else
            menus[MOUTH].selected(), [""]
        )
        return ears[0] + eyes[0] + mouth[0] + eyes[-1] + ears[-1]

    k = 0
    while not (k == ord('q') and panel.win_select.focus):
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        shift = {curses.KEY_LEFT: -1, curses.KEY_RIGHT: 1}.get(k, 0)
        if shift != 0 and menus[focus_index].focus and not menus[focus_index].move_possible(k):
            old_index = focus_index
            focus_index = (focus_index + shift) % 3

            if menus[old_index].win_select.focus:  # Move cursor smoothly
                menus[focus_index].win_select.cursor_y = menus[old_index].win_select.cursor_y
                menus[focus_index].win_select.cursor_x = (0 if k == curses.KEY_RIGHT else float("inf"))
                menus[focus_index].win_select.check_cursor()

            # Set new focus
            menus[old_index].set_focus(False)
            menus[focus_index].last_focus = menus[old_index].last_focus
            menus[focus_index].set_focus(True)

        elif k == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()
            taille = [floor(width // 3), ceil(width // 3), floor(width // 3)]
            for index in range(3):
                menu[index].set_dimension(height - 3, taille[index], 2, sum(taille[0:index:])),

        else:
            for index in range(3):
                menus[index].add_keys(k)

        stdscr.addstr(2, 1, f"Ears")
        stdscr.addstr(2, 1 + taille[0], f"Eyes")
        stdscr.addstr(2, 1 + taille[0] + taille[1], f"Mouth")
        stdscr.addstr(0, taille[0] + 1, "Result: {} Preview: {}".format(
            get_emojie(menus),
            get_emojie(menus,
                       preview_ears=(focus_index == 0),
                       preview_eyes=(focus_index == 1),
                       preview_mouth=(focus_index == 2)
                       )
        ))

        stdscr.refresh()
        for menu in menus:
            menu.reload()
        stdscr.refresh()

        if k in (curses.KEY_ENTER, ord("\n")):
            pyperclip.copy(get_emojie(menus))

        k = stdscr.getch()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
