# blaseball-game-gems

blaseball-game-gems is a command line tool that analyzes a blaseball game to
look for notable or significant events. 

A list of conditions that this tool looks for (not comprehensive):

* batting gems:

    * multiple home runs (total, team, player)
    * multiple grand slams
    * bottom of the 9th home runs or grand slams (we can't do this right now, unless we look at events)
    * (record for most home runs in a single game?)
    * multiple RBIs
    * more than 4 hits
    * hit for the cycle

* pitching gems:

    * no hitter
    * near miss no hitter
    * perfect game
    * near miss perfect game
    * 10 or more strikeouts

## Quick Start

Start by installing blaseball

```text
pip install blaseball-game-gems
```

Now call game-gems and pass it a blaseball game ID:

```text
game-gems [game-id]
```

This outputs a JSON object with various indicators of
significant blaseball events:

```text
[
    {
        gem_type: ...,
        gem_descr: ...,
        gem_class: (pitching|batting|baserunning|fielding),
        gem_player: ...,
    },
    {
        ...
    }
]
```



