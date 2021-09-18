# coding=utf-8
import unicodedata
from math import ceil

try:
    import curses
except ImportError:
    sys.exit("""You need curses, it's a default module on Linux, it's time to join the great side of the open-source project ! If needed: https://pypi.org/project/windows-curses/""")


def get_color(cursor=False, focus=False, selected=False):
    idd = 1 * int(cursor) + 2 * int(focus) + 4 * int(selected)
    return (idd if idd > 0 else 8)


def isPrintable(k):
    if k in (
        curses.KEY_DOWN,
        curses.KEY_UP,
        curses.KEY_LEFT,
        curses.KEY_RIGHT,
        curses.KEY_ENTER,
        ord("\n"),
        curses.KEY_BACKSPACE,
        ord('\x7f'),
        curses.KEY_RESIZE
    ):
        return False
    return chr(k).isprintable()


def trim(string, max_length=15):
    string = str(string)
    extra_length = 0
    for char in string:
        if unicodedata.east_asian_width(char) == 'F':
            extra_length += 1

    diff = max_length - len(string) - extra_length
    if diff > 0:
        return string + diff * ' '
    elif diff < 0:
        return string[:max_length]

    return string


class customWindows():
    """common structure for other windows"""

    def __init__(self, h, w, y, x):
        self.win = curses.newwin(h, w, y, x)
        self.width = w
        self.height = h
        self.cursor_x = 0
        self.cursor_y = 0
        self.focus = False

    def check_cursor(self):
        self.cursor_x = 0
        self.cursor_y = 0

    def move_possible(self, k):
        """check if movement is possible"""
        self.check_cursor()
        return False

    def move_cursor(self, k):
        self.cursor_x += {curses.KEY_RIGHT: 1, curses.KEY_LEFT: -1}.get(k, 0)
        self.cursor_y += {curses.KEY_UP: -1, curses.KEY_DOWN: 1}.get(k, 0)
        self.check_cursor()

    def reload(self):
        self.win.clear()
        self.win.refresh()


class SearchBar(customWindows):
    """basic search bar with cursor
    when focus, keys pressed are add to SearchBar.letters accessible with SearchBar.content()"""

    def set_dimension(self, h, w, y, x):
        super(SearchBar, self).__init__(h, w, y, x)

    def __init__(self, h, w, y, x):
        self.set_dimension(h, w, y, x)
        self.dim = (h, w, y, x)
        self.letters = []
        self.message = "Looking for : "

    def check_cursor(self):
        self.cursor_y = 0
        self.cursor_x = max(self.cursor_x, 0)
        self.cursor_x = min(self.cursor_x, len(self.letters))

    def move_possible(self, k):
        self.check_cursor()
        if k in (curses.KEY_DOWN, curses.KEY_UP):
            return False
        if k == curses.KEY_RIGHT and self.cursor_x < len(self.letters):
            return True
        if k == curses.KEY_LEFT and self.cursor_x > 0:
            return True
        return False

    def add_keys(self, k, force_letters=False):
        if (force_letters or self.focus):
            if isPrintable(k):
                self.letters.insert(self.cursor_x, chr(k))
                self.cursor_x += 1
            if k in (curses.KEY_BACKSPACE, 127) and self.letters:
                del self.letters[self.cursor_x - 1]
                self.cursor_x -= 1

        if self.focus:
            self.move_cursor(k)
            self.check_cursor()

    def content(self):
        return "".join(self.letters)

    def reload(self):
        self.win.clear()
        self.win.addstr(0, 0, self.message + self.content())
        ajout = " " if self.focus else " "
        self.win.addstr(
            0,
            len(self.message) + self.cursor_x,
            (self.content() + ajout)[self.cursor_x:self.cursor_x + 1],
            curses.color_pair(get_color(focus=self.focus, cursor=True))
        )
        self.win.refresh()


class SelectionPanel(customWindows):
    def set_dimension(self, h, w, x, y):
        self.dim = (h, w, y, x)
        self.height = h
        self.width = w

        self.max_element_size = 0
        self.element_by_line = 0
        self.number_of_line = 0

        try:
            self.max_element_size = max([
                len(self.token_trim(token)) for token in self.content
            ])
            self.element_by_line = self.width // self.max_element_size
            self.number_of_line = ceil(len(self.content) / self.element_by_line)
        except ZeroDivisionError:
            self.win.addstr(1, 1, "Too small.")
        except ValueError:
            self.win.addstr(1, 1, "No value.")

    def token_trim(self, token, sep="   "):
        return sep + trim(token, max_length=min(self.width - 2 * len(sep), 45)) + sep

    def __init__(self, h, w, y, x):
        super(SelectionPanel, self).__init__(h, w, y, x)
        self.content = [""]
        self.set_dimension(h, w, y, x)
        self.selected_x = 0
        self.selected_y = 0
        self.scroll = 0
        self.progresse_bar = True

    def check_cursor(self):
        self.cursor_y = max(self.cursor_y, 0)
        self.cursor_y = min(self.cursor_y, self.number_of_line - 1)
        self.cursor_x = max(self.cursor_x, 0)
        self.cursor_x = min(self.cursor_x, self.element_by_line - 1)

        self.selected_y = max(self.selected_y, 0)
        self.selected_y = min(self.selected_y, self.number_of_line - 1)
        self.selected_x = max(self.selected_x, 0)
        self.selected_x = min(self.selected_x, self.element_by_line - 1)

    def move_possible(self, k):
        self.check_cursor()
        if k == curses.KEY_DOWN and self.cursor_y < self.number_of_line - 1:
            return True
        if k == curses.KEY_UP and self.cursor_y > 0:
            return True
        if k == curses.KEY_RIGHT and self.cursor_x < self.element_by_line - 1:
            return True
        if k == curses.KEY_LEFT and self.cursor_x > 0:
            return True
        return False

    def move_cursor(self, k):
        self.cursor_y += {curses.KEY_DOWN: 1, curses.KEY_UP: -1}.get(k, 0)
        self.cursor_x += {curses.KEY_RIGHT: 1, curses.KEY_LEFT: -1}.get(k, 0)

        if self.cursor_y - self.scroll <= 3 and self.scroll:
            self.scroll -= 1
        if self.cursor_y - self.scroll >= self.height - 3 and self.scroll < self.number_of_line - self.height + 1:
            self.scroll += 1

        self.check_cursor()

    def add_keys(self, k):
        if not self.focus:
            return  # skip key
        if k in (curses.KEY_ENTER, ord("\n")):
            self.selected_x = self.cursor_x
            self.selected_y = self.cursor_y

        self.move_cursor(k)

    def set_content(self, content):
        self.content = content
        self.check_cursor()
        self.set_dimension(*self.dim)

    def get_element(self, x, y):
        if x + y * self.element_by_line < len(self.content):
            return self.content[x + y * self.element_by_line]
        return "vide"

    def mousse_selected(self):
        self.check_cursor()
        return self.get_element(self.cursor_x, self.cursor_y)

    def selected(self):
        self.check_cursor()
        return self.get_element(self.selected_x, self.selected_y)

    def reload(self):
        self.win.clear()
        for y in range(min(self.number_of_line, self.height - 2)):
            for x in range(self.element_by_line):
                self.win.addstr(
                    y + 1,
                    x * self.max_element_size + 1,
                    self.token_trim(self.get_element(x, y + self.scroll)),
                    curses.color_pair(get_color(focus=self.focus, cursor=False))
                )

        if self.content:
            # Print cursor
            if 0 <= self.cursor_y - self.scroll < self.height:
                self.win.addstr(
                    self.cursor_y - self.scroll + 1,
                    self.cursor_x * self.max_element_size + 1,
                    self.token_trim(self.get_element(self.cursor_x, self.cursor_y)),
                    curses.color_pair(get_color(focus=self.focus, cursor=True))
                )

            # Print selected item
            if 0 <= self.selected_y - self.scroll < self.height - 1:
                self.win.addstr(
                    self.selected_y - self.scroll + 1,
                    self.selected_x * self.max_element_size + 1,
                    self.token_trim(self.get_element(self.selected_x, self.selected_y)),
                    curses.color_pair(get_color(
                        focus=self.focus,
                        selected=True,
                        cursor=(self.selected_x, self.selected_y) == (self.cursor_x, self.cursor_y)
                    ))
                )

        if len(self.content) - 1 < self.height - 1:
            self.win.addstr(len(self.content) + 1, 1, "End.")

        self.win.addstr(3, 1, f"{self.number_of_line} {self.element_by_line}")

        self.win.box()
        if self.progresse_bar:
            self.win.addstr(self.height - 1, 1, f"Line {self.cursor_y + 1} out of {len(self.content)}.")

        self.win.refresh()


class ChoicePanel():
    def set_dimension(self, h, w, y, x):
        self.win_search = SearchBar(1, w, y + 1, x + 1)
        self.win_select = SelectionPanel(h - 2, w, y + 2, x)

    def __init__(self, h, w, y, x):
        self.set_dimension(h, w, y, x)
        self.dim = (h, w, y, x)
        self.win_search.focus = True
        self.title = ""
        self.content = []
        self.focus = False
        self.last_focus = (True, False)

    def resize(h, w, y, x):
        self.win_select.set_dimension(height=h - 2, width=w)

    def selected(self):
        return self.win_select.selected()

    def mousse_selected(self):
        return self.win_select.mousse_selected()

    def set_content(self, content):
        self.content = content
        self.win_select.set_content([emo[0] for emo in self.content])

    def set_focus(self, focus):
        if focus == self.focus:
            return
        elif focus == False:  # Save focus
            self.focus = False
            self.last_focus = (self.win_search.focus, self.win_select.focus)
            self.win_search.focus = False
            self.win_select.focus = False
        elif focus == True:  # Restore focus
            self.focus = True
            self.win_search.focus = self.last_focus[0]
            self.win_select.focus = self.last_focus[1]

    def move_possible(self, k):
        return (self.win_select.focus and self.win_select.move_possible(k)) or (self.win_search.focus and self.win_search.move_possible(k))

    def add_keys(self, k):
        if not self.focus:
            return
        if self.win_select.focus and k == curses.KEY_UP and not self.win_select.move_possible(k):
            self.win_select.focus = False
            self.win_search.focus = True
        elif self.win_search.focus and k == curses.KEY_DOWN:
            self.win_search.focus = False
            self.win_select.focus = True
        else:
            self.win_search.add_keys(k, force_letters=True)
            self.win_select.set_content(
                [emo[0] for emo in self.content
                 if self.win_search.content() in emo[1]]
            )
            self.win_select.add_keys(k)

    def reload(self):
        self.win_search.reload()
        self.win_select.reload()
