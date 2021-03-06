# Python Minesweeper

![screenshot](mines.png)

## Goal of the game

The goal of the game is to discover all positions of the mine field
except for those, that contain mines. In the beginning, all positions
are unknown, denoted with X. When a position is being discovered,
it can turn out to be a mine, an empty positions, or a clue. If you
discover a mine, you've lost the game. A clue is a number from 1 to 8
which tells, how many of the adjacent 8 positions contain mines.
With these clues, logical deduction and some luck, you shall be able
to discover all the positions of the mine field, leaving out only
positions with mines. That is the goal of the game.

Here is the meaning of the symbols displayed on each of the positions
(they have different colors, if available, for better recognition):

```
X       Not discovered yet
<empty> Empty position. None of its adjacent positions contain a mine.
1-8     Clue. That many adjacent positions contain mines.
!       Mine mark. Place this on a position that you belive that it
        contains a mine. Position marked with ! can't be discovered
        (not even accidentaly).
?       Doubt mark. You can use this mark for suspicious positions.
        The use of this mark is on you.
M       Mine. If you see this symbol, you've lost.
W       False mine. If you've lost, this symbol denotes a position
        that you claimed to be a mine (with a mine mark), but it
        actually wasn't.
```

## Playing the game

Current position on the mine field is hilighted (its coordinates
are yellow instead of white, and the position should be underlined,
if the terminal supports this).

In the top left corner of the screen, you can see the number of
mines that you have found (or the number of mine marks that you
have placed) and the total number of mines in the mine field.

### Controls:

* arrow keys - move the current position
* enter - discover the current position
* space - mark the current position with mine mark. More accurately, toggle the mine mark (i.e. clear the mark if it has been placed before). The mine mark also clears a doubt mark, if it has been placed on the current position. A position marked with a mine mark can't be discovered until the mark is removed (preventing the user from accidentaly tapping a mine)
* tab - toggle doubt mark on the current position. It also clears a mine mark, if it has been placed on the current position
* esc - quit the game immediately
* ^l (i.e. ctrl and l) - redraw the screen

Moreover, the game has a command interface. Letters, numbers and
exclamation and question marks can be used to enter commands.
After typing in a command, hit return (enter) to execute it.

Here is a list of commands:

```
quit - quit the game immediately
print - redraw the screen
<x><y> - discover the given position (column x, row y)
!<x><y> - toggle mine mark on given position
?<x><y> - toggle doubt mark on given position
```

The <x> parameter is a letter or a string of letters (lowercase
or uppercase) determining a column, <y> is integral index
of a row.

### Examples:

* `A1` - discover top left corner
* `!D3` - place a mine mark on position [4, 3]
* `?AB10` - place a doubt mark on position [28, 10]



