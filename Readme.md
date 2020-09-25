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

## Instructions

Use the `game-gems` script to analyze the JSON output from the
`game-summary` utility.

Call `game-gems` and pass it a JSON file containing a game summary
output:

```text
./game-gems --input-file [input-json]
./game-gems -i [input-json]
```

This command outputs a JSON object with various indicators of
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

