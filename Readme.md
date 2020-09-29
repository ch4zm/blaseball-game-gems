# blaseball-game-gems

This repo contains code to analyze blaseball game summaries
and look for notable or significant events.

It uses the [`game-summary`](https://github.com/ch4zm/blaseball-game-summary)
tool to get game summaries, and identifies significant or noteworthy
events from the game summary.

**Note:** This tool analyzes game summaries, not game events. The `game-summary` tool
processes the actual blaseball events returned by the blaseball-reference.com API,
this tool processes the output of the `game-summary` tool.

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

Use the `game-gems` script to analyze the JSON output from the
`game-summary` utility.

This tool has a command line flag to specify the input file (`-i/--input-file`)
and several flags to specify an output format (`--json`, `--text`, and `--markdown`).

Start by creating a game summary using the `game-finder` and `game-summary`
utilities. Here, we look up the perfect game by Patty Fox of the Millennials,
from Season 8 Day 61:

```
$ game-finder --season 8 --day 61 --team Millennials
c8acdfe9-d981-46ba-b202-e977c99b8a4c
```

Pipe this to `game-summary` and output the resulting JSON to a file:

```
$ game-finder --season 8 --day 61 --team Millennials | xargs game-summary > mils_s8_d61.json
```

Now call `game-gems` and pass it the JSON file containing a game summary output:

```text
$ game-gems -i mils_s8_d61.json
```

This command outputs a JSON object with various indicators of significant blaseball events:

```text
$ game-gems -i mils_s8_d61.json
{
    "info": {
        "season": 8,
        "day": 61,
        "homeTeamNickname": "Millennials",
        "awayTeamNickname": "Flowers",
        "homeTeamName": "New York Millennials",
        "awayTeamName": "Boston Flowers",
        "stadium": "Battin' Island, New York, NY",
        "weather": "Lots of Birds"
    },
    "box_score": {
        "home": [ 8, 9, 0 ],
        "away": [ 0, 0, 0 ]
    },
    "gems": [
        {
            "gem_type": "pitching_perfectgame",
            "gem_class": "pitching",
            "gem_description": "Patty Fox (Millennials) pitched a perfect game against the Flowers, recording 4 strikeouts.",
            "gem_team": "Millennials",
            "gem_player": "Patty Fox"
        },
        {
            "gem_type": "pitching_lowbb",
            "gem_class": "pitching",
            "gem_description": "Patty Fox (Millennials) allowed no walks against the Flowers.",
            "gem_team": "Millennials",
            "gem_player": "Patty Fox"
        },
        {
            "gem_type": "pitching_hitless",
            "gem_class": "pitching",
            "gem_description": "Patty Fox (Millennials) held the Flowers hitless for 9 innings (1 thru 9).",
            "gem_team": "Millennials",
            "gem_player": "Patty Fox"
        },
        {
            "gem_type": "pitching_scoreless",
            "gem_class": "pitching",
            "gem_description": "Patty Fox (Millennials) held the Flowers scoreless for 9 innings (1 thru 9).",
            "gem_team": "Millennials",
            "gem_player": "Patty Fox"
        }
    ]
}
```

## Python API

If you want to use the `game-gems` tool from Python instead of
using the command line tool, we provide a function that you can
import that will return the output of the command in a string.

To use the function, you pass the `game-summary` JSON as a string.
The first argument is a list of strings containing any flags you
want to pass to the command line flag parser. The second argument
is the string containing the contents of the game summary JSON.

You should not specify the input file flag. If your JSON is in a file,
Use Python to open the file and read its contents into a string.
If your JSON is a Python dictionary, use the `json.dumps()` function.

```
from game_gems import game_gems

with open("mils_s8_d61.json", "r") as f:
    game_summary = json.load(f)

# Pass no flags, using default output format (JSON)
result = game_gems([], flags)
print(result)

# Pass --text flag, using text output format
result = game_gems(["--text"], flags)
print(result)
```

