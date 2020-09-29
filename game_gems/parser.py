import json
from itertools import groupby

"""
Should probably put together an analogous structure
to the game summary - i.e., have an info key, and a
gems key, so everything is kept together.

{
    info: {
        ...
    },
    box_score: {
        ...
    },
    gems: [
        {
            gem_type: ...,
            gem_description: ...,
            gem_class: (pitching|batting|baserunning|fielding),
            gem_player: ...,
            gem_team: ...,
        },
        ...
    ]
"""

class DataParser(object):

    # Set the min/max limits of what makes something a gem
    TEAM_HR = 5
    PLAYER_HR = 2
    GAME_HR = 8

    TEAM_GS = 2
    PLAYER_GS = 2
    GAME_GS = 2

    TEAM_H = 10
    GAME_H = 20
    PLAYER_H = 4

    RALLY = 3
    COMEFROMBEHIND = 3
    PLAYER_RBI = 5

    PITCHING_SO = 8
    PITCHING_LO_HIT = 4
    PITCHING_BB_LO = 1
    PITCHING_BB_HI = 8
    PITCHING_HITLESS = 6
    PITCHING_SCORELESS = 8

    def __init__(self, options):
        self.input_file = options.input_file
        with open(self.input_file, 'r') as f:
            self.data = json.load(f)

    def parse(self):
        # Assemble the final JSON object
        gems_json = {
            "info": {},
            "box_score": {},
            "gems": []
        }

        # Extract useful information from game summary,
        # populate info and box_score keys of gems_json
        data = self.data
        game_info = data['info']
        game_box = data['box_score']
        game_line = data['line_score']
        game_summary = data['game_summary']
        game_pitching = data['pitching_summary']

        gems_json['info'] = game_info
        gems_json['box_score'] = game_box

        season = game_info['season']
        day = game_info['day']
        ht = game_info['homeTeamNickname']
        at = game_info['awayTeamNickname']

        hruns = game_box['home'][0]
        aruns = game_box['away'][0]

        wt = ht if hruns > aruns else at
        lt = ht if aruns > hruns else at

        # This is kinda messy, but basically we go through each gem type,
        # one by one, and check if this game meets the gem criteria.
        # If it does, we tack on some information about this gem.

        # This will be assigned to the 'gems' key of the final JSON
        gem_list = []

        # -----------------------
        # Batting gems:

        # Home runs:

        # Team HR
        ht_hr = sum(game_summary['home']['batting']['HR'].values())
        at_hr = sum(game_summary['away']['batting']['HR'].values())

        def make_team_hr_gem(team_name, team_hr):
            d = dict(
                gem_type="team_hr",
                gem_class="batting",
                gem_description="The %s hit %d home runs!"%(team_name, team_hr),
                gem_team=team_name,
            )
            return d

        if ht_hr >= self.TEAM_HR:
            gem_list.append(make_team_hr_gem(ht, ht_hr))
        if at_hr >= self.TEAM_HR:
            gem_list.append(make_team_hr_gem(at, at_hr))

        # Total HR
        game_hr = ht_hr + at_hr

        def make_game_hr_gem(home_team, away_team, tot_hr):
            d = dict(
                gem_type="game_hr",
                gem_class="batting",
                gem_description="The %s and %s hit a combined %d home runs!"%(
                    home_team,
                    away_team,
                    tot_hr,
                ),
                gem_team=team_name,
            )
            return d

        if game_hr >= self.GAME_HR:
            gem_list.append(make_game_hr_gem(ht, at, game_hr))

        # Player HR
        def make_player_hr_gem(player_name, team_name, player_hr):
            d = dict(
                gem_type="player_hr",
                gem_class="batting",
                gem_description="%s (%s) hit %d home runs!"%(player_name, team_name, player_hr),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        for htat in ['home', 'away']:
            player_hrs = {k: v for k,v in game_summary[htat]['batting']['HR'].items() if v>=self.PLAYER_HR}
            if len(player_hrs)>0:
                k = "%sTeamNickname"%(htat)
                team_name = game_info[k]
                for player_name, player_hr in player_hrs.items():
                    gem_list.append(make_player_hr_gem(player_name, team_name, player_hr))

        # Grand Slams

        ht_gs = sum(game_summary['home']['batting']['GS'].values())
        at_gs = sum(game_summary['away']['batting']['GS'].values())

        def make_team_gs_gem(team_name, team_gs):
            d = dict(
                gem_type="team_gs",
                gem_class="batting",
                gem_description="The %s hit %d grand slams!"%(team_name, team_gs),
                gem_team=team_name,
            )
            return d

        if ht_gs >= self.TEAM_GS:
            gem_list.append(make_team_gs_gem(ht, ht_gs))
        if at_gs >= self.TEAM_GS:
            gem_list.append(make_team_gs_gem(at, at_gs))

        # Total GS
        game_gs = ht_gs + at_gs

        def make_game_gs_gem(home_team, away_team, tot_gs):
            d = dict(
                gem_type="game_gs",
                gem_class="batting",
                gem_description="The %s and %s hit a combined %d grand slams!"%(
                    home_team,
                    away_team,
                    tot_gs,
                ),
                gem_team=team_name,
            )
            return d

        if game_gs >= self.GAME_GS:
            gem_list.append(make_game_gs_gem(ht, at, game_gs))

        # Player GS
        def make_player_gs_gem(player_name, team_name, player_gs):
            d = dict(
                gem_type="player_gs",
                gem_class="batting",
                gem_description="%s (%s) hit %d grand slams!"%(player_name, team_name, player_gs),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        for htat in ['home', 'away']:
            player_gs = {k: v for k,v in game_summary[htat]['batting']['GS'].items() if v>=self.PLAYER_GS}
            if len(player_gs)>0:
                k = "%sTeamNickname"%(htat)
                team_name = game_info[k]
                for player_name, player_gs in player_gs.items():
                    gem_list.append(make_player_gs_gem(player_name, team_name, player_gs))

        # Hits

        # Team Hits
        ht_h = game_box['home'][1]
        at_h = game_box['away'][1]

        def make_team_h_gem(team_name, team_h):
            d = dict(
                gem_type="team_hr",
                gem_class="batting",
                gem_description="The %s got %d hits!"%(team_name, team_h),
                gem_team=team_name,
            )
            return d

        if ht_h >= self.TEAM_H:
            gem_list.append(make_team_h_gem(ht, ht_h))
        if at_h >= self.TEAM_H:
            gem_list.append(make_team_h_gem(at, at_h))

        # Total H
        game_h = ht_h + at_h

        def make_game_h_gem(home_team, away_team, tot_h):
            d = dict(
                gem_type="game_hr",
                gem_class="batting",
                gem_description="The %s and %s combined for %d hits!"%(
                    home_team,
                    away_team,
                    tot_h,
                ),
            )
            return d

        if game_h >= self.GAME_H:
            gem_list.append(make_game_h_gem(ht, at, game_h))

        # Player H
        def make_player_h_gem(player_name, team_name, player_h):
            d = dict(
                gem_type="player_hr",
                gem_class="batting",
                gem_description="%s (%s) collected %d hits!"%(player_name, team_name, player_h),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        HIT_TYPES = ['1B', '2B', '3B', 'HR']
        for htat in ['home', 'away']:
            k = "%sTeamNickname"%(htat)
            team_name = game_info[k]

            # Start by aggregating hits
            hits_d = {}
            for stat, stat_val in game_summary[htat]['batting'].items():
                if stat in HIT_TYPES:
                    for player_name, player_n in stat_val.items():
                        if player_name in hits_d.keys():
                            hits_d[player_n] += player_n
                        else:
                            hits_d[player_n] = player_n

            # Check if any player achieved threshold
            for player_name, player_n in hits_d.items():
                if player_n > self.PLAYER_H:
                    gem_list.append(make_player_h_gem(player_name, team_name, player_hr))

        # Runs and Rallies:

        # 9th inning/extra inning rallies:
        def make_rally_gem(team_name, home_or_away, inning, runs):
            tb = 'top' if home_or_away=='away' else 'bottom'
            d = dict(
                gem_type="team_rally",
                gem_class="batting",
                gem_description="The %s rallied for %d runs in the %s of inning %d!"%(team_name, runs, tb, inning),
                gem_team=team_name,
            )
            return d

        for htat in ['home', 'away']:
            line_score_row = game_line[htat]
            k = "%sTeamNickname"%(htat)
            team_name = game_info[k]
            # Only look at inning 9 and beyond (innings are zero-indexed)
            for i in range(8,len(line_score_row)):
                # Get number of runs scored this inning
                r = line_score_row[i]
                if r >= self.RALLY:
                    gem_list.append(make_rally_gem(team_name, htat, i+1, r))

        # Red-hot (hits every inning)
        def make_redhot_gem(team_name, team_runs):
            d = dict(
                gem_type="team_redhot",
                gem_class="batting",
                gem_description="The %s were red-hot! They got hits in every inning, scoring %d runs"%(
                    team_name,
                    team_runs
                ),
                gem_team=team_name,
            )
            return d

        for htat in ['home', 'away']:
            nhits = game_box[htat][1]
            k = "%sTeamNickname"%(htat)
            team_name = game_info[k]
            redhot = True
            hits_row = game_summary[htat]['batting']['H']
            for i in range(len(hits_row)):
                h = hits_row[i]
                if h==0:
                    redhot = False
                    break
            if redhot:
                gem_list.append(make_redhot_gem(team_name, nhits))

        # On fire (runs every inning):
        def make_onfire_gem(team_name, team_runs):
            d = dict(
                gem_type="team_redhot",
                gem_class="batting",
                gem_description="The %s were on fire! They scored runs in every inning, for a total of %d runs"%(
                    team_name,
                    team_runs
                ),
                gem_team=team_name,
            )
            return d

        for htat in ['home', 'away']:
            nruns = game_box[htat][0]
            k = "%sTeamNickname"%(htat)
            team_name = game_info[k]
            on_fire = True
            line_score_row = game_line[htat]
            for i in range(len(line_score_row)):
                r = line_score_row[i]
                if r==0:
                    on_fire = False
                    break
            if redhot:
                gem_list.append(make_onfire_gem(team_name, nruns))

        # Dramatic come-from-behind in final innings to tie it up or go ahead
        def make_comefrombehind_gem(team_name, home_or_away, wonlost, inning, deficit, runs):
            tb = 'top' if home_or_away=='away' else 'bottom'
            d = dict(
                gem_type="team_comefrombehind",
                gem_class="batting",
                gem_description="The %s came from behind in the %s of inning %d, down by %d and scoring %d runs! They ultimately %s the game."%(
                    team_name,
                    tb,
                    inning,
                    deficit,
                    runs,
                    wonlost,
                ),
                gem_team=team_name,
            )
            return d

        def make_tiefrombehind_gem(team_name, home_or_away, wonlost, inning, deficit, runs):
            tb = 'top' if home_or_away=='away' else 'bottom'
            d = dict(
                gem_type="team_tiefrombehind",
                gem_class="batting",
                gem_description="The %s came from behind in the %s of inning %d, down by %d, to tie it up! They ultimately %s the game."%(
                    team_name,
                    tb,
                    inning,
                    deficit,
                    runs,
                    wonlost,
                ),
                gem_team=team_name,
            )
            return d

        for htat in ['home', 'away']:
            them = 'home' if htat=='away' else 'away'
            us_line_score = game_line[htat]
            them_line_score = game_line[them]
            # Look from 7th to end
            for i in range(6, len(us_line_score)):
                inning = i+1
                them_before_inning = inning-1 if htat=='away' else inning
                us_before_inning = inning-1
                us_before = sum(us_line_score[:us_before_inning])
                them_before = sum(them_line_score[:them_before_inning])
                us_after = sum(us_line_score[:inning])
                deficit = them_before - us_before
                runs = us_after - us_before
                if deficit >= self.COMEFROMBEHIND:
                    wonlost = 'won' if game_box[htat][0] > game_box[them][0] else 'lost'
                    if runs==deficit:
                        gem_list.append(make_tiefrombehind_gem(
                            team_name, htat, wonlost, inning, deficit, runs
                        ))
                    elif runs>deficit:
                        gem_list.append(make_comefrombehind_gem(
                            team_name, htat, wonlost, inning, deficit, runs
                        ))

        # Lead changes multiple times
        def make_leadswap_gem(ht, at, n, wt):
            d = dict(
                gem_type="team_leadswap",
                gem_class="batting",
                gem_description="The %s and %s swapped the lead %d times! The %s ultimately won the game."%(
                    ht, at, n, wt
                ),
                gem_team=team_name,
            )
            return d

        # Count the number of times the lead changes
        ninnings = len(game_line['home'])
        lead_changes = 0
        for i in range(ninnings):
            # Top of inning
            if i==0:
                hma = -game_line['away'][i]
                hma_gt0 = hma > 0
            else:
                hsum = sum(game_line['home'][:i])
                asum = sum(game_line['away'][:i+1])
                hma = hsum - asum
                new_hma_gt0 = hma > 0
                lead_changed = (new_hma_gt0 and not hma_gt0) or (hma_gt0 and not new_hma_gt0)
                if lead_changed:
                    lead_changes += 1
                hma_gt0 = new_hma_gt0

            # Bottom of inning
            asum = sum(game_line['away'][:i+1])
            hsum = sum(game_line['home'][:i+1])
            hma = hsum - asum
            new_hma_gt0 = hma > 0
            lead_changed = (new_hma_gt0 and not hma_gt0) or (hma_gt0 and not new_hma_gt0)
            if lead_changed:
                lead_changes += 1
            hma_gt0 = new_hma_gt0

        if lead_changes > 6:
            gem_list.append(make_leadswap_gem(
                ht, at, lead_changes, wt
            ))

        # -----------------------
        # Player batting gems:
        def make_rbi_gem(team_name, player_name, rbis):
            d = dict(
                gem_type="player_rbi",
                gem_class="batting",
                gem_description="%s batted in %d runs for the %s in the game."%(player_name, rbis, team_name),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        for htat in ['home', 'away']:
            k = "%sTeamNickname"%(htat)
            team = game_info[k]
            rbis = game_summary[htat]['batting']['RBI']
            for player, n in rbis.items():
                make_rbi_gem(player, team, n)

        # -----------------------
        # Pitching gems:

        # Only the winning pitcher:

        def make_shutout_gem(player_name, team_name, versus_team_name, hits, strikeouts, walks):
            if walks==0:
                walks_text = "no walks"
            elif walks==1:
                walks_text = "just %d walk"%(walks)
            else:
                walks_text = "just %d walks"%(walks)

            if strikeouts==0:
                strikeouts_text = "no strikeouts"
            elif strikeouts==1:
                strikeouts_text = "%d strikeout"%(strikeouts)
            else:
                strikeouts_text = "%d strikeouts"%(strikeouts)

            if hits==0:
                hits_text = "no hits"
            elif hits==1:
                hits_text = "%d hit"%(hits)
            else:
                hits_text = "%d hits"%(hits)

            d = dict(
                gem_type="pitching_shutout",
                gem_class="pitching",
                gem_description="%s (%s) pitched a shutout against the %s, allowing %s and recording %s and %s."%(
                    player_name,
                    team_name,
                    versus_team_name,
                    hits_text,
                    strikeouts_text,
                    walks_text,
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        def make_nohitter_gem(player_name, team_name, versus_team_name, strikeouts, walks):
            if walks==0:
                walks_text = "no walks"
            elif walks==1:
                walks_text = "just %d walk"%(walks)
            else:
                walks_text = "just %d walks"%(walks)

            if strikeouts==0:
                strikeouts_text = "no strikeouts"
            elif strikeouts==1:
                strikeouts_text = "%d strikeout"%(strikeouts)
            else:
                strikeouts_text = "%d strikeouts"%(strikeouts)

            d = dict(
                gem_type="pitching_nohitter",
                gem_class="pitching",
                gem_description="%s (%s) pitched a no-hitter against the %s, recording %s and %s."%(
                    player_name,
                    team_name,
                    versus_team_name,
                    strikeouts,
                    walks
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        def make_perfectgame_gem(player_name, team_name, versus_team_name, strikeouts):
            d = dict(
                gem_type="pitching_perfectgame",
                gem_class="pitching",
                gem_description="%s (%s) pitched a perfect game against the %s, recording %d strikeouts."%(
                    player_name,
                    team_name,
                    versus_team_name,
                    strikeouts
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        # No-hitters/perfect games/shutouts only happen for the winning team
        wtlab = 'home' if game_box['home'][0]>game_box['away'][0] else 'away'
        ltlab = 'home' if game_box['away'][0]>game_box['home'][0] else 'away'
        pitcher_name = game_pitching['WP']
        hits = sum(game_summary[ltlab]['batting']['H'])
        runs = game_box[ltlab][0]
        strikeouts = sum(game_pitching['WP-K'])
        walks = sum(game_pitching['WP-BB'])
        hbp = sum(game_pitching['WP-HBP'])
        if hits==0:
            if walks==0 and hbp==0:
                gem_list.append(make_perfectgame_gem(
                    pitcher_name, wt, lt, strikeouts
                ))
            else:
                gem_list.append(make_no_hitter(
                    pitcher_name, wt, lt, strikeouts, walks
                ))
        elif runs==0:
            gem_list.append(make_shutout_gem(
                pitcher_name, wt, lt, hits, strikeouts, walks
            ))

        # Winning or losing pitcher:
        def make_so_gem(player_name, team_name, versus_team_name, strikeouts):
            """Strikeouts"""
            d = dict(
                gem_type="pitching_strikeouts",
                gem_class="pitching",
                gem_description="%s (%s) struck out %d %s."%(
                    player_name,
                    team_name,
                    strikeouts,
                    versus_team_name,
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        def make_lowhitter_gem(player_name, team_name, versus_team_name, hits, walks, strikeouts):
            """Low-hitters"""
            if walks==0:
                walks_text = "no walks"
            elif walks==1:
                walks_text = "just %d walk"%(walks)
            else:
                walks_text = "just %d walks"%(walks)

            if strikeouts==0:
                strikeouts_text = "no strikeouts"
            elif strikeouts==1:
                strikeouts_text = "%d strikeout"%(strikeouts)
            else:
                strikeouts_text = "%d strikeouts"%(strikeouts)

            d = dict(
                gem_type="pitching_lowhitter",
                gem_class="pitching",
                gem_description="%s (%s) threw a %d-hitter against the %s, recording %s and %s."%(
                    player_name,
                    team_name,
                    hits,
                    versus_team_name,
                    strikeouts_text,
                    walks_text,
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        def make_lobb_gem(player_name, team_name, versus_team_name, walks):
            """Low-walk games"""
            if walks==0:
                walks_text = "no walks"
            elif walks==1:
                walks_text = "just %d walk"%(walks)
            else:
                walks_text = "just %d walks"%(walks)

            d = dict(
                gem_type="pitching_lowbb",
                gem_class="pitching",
                gem_description="%s (%s) allowed %s against the %s."%(
                    player_name,
                    team_name,
                    walks_text,
                    versus_team_name,
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        def make_hibb_gem(player_name, team_name, versus_team_name, walks):
            """High-walk games"""
            d = dict(
                gem_type="pitching_highbb",
                gem_class="pitching",
                gem_description="%s (%s) allowed a whopping %d walks against the %s."%(
                    player_name,
                    team_name,
                    walks,
                    versus_team_name,
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        # NOTE: Add high HBP, to identify Jaylen games

        # Check for gems from both the winning and losing pitchers
        for plab in ['WP', 'LP']:
            pitcher_name = game_pitching[plab]
            if plab=='WP':
                pitcher_team = wt
                other_team = lt
            else:
                pitcher_team = lt
                other_team = wt
            if game_info['homeTeamNickname']==wt:
                tlab = 'home'
            else:
                tlab = 'away'
            wlab = plab + "-BB"
            klab = plab + "-K"
            hbplab = plab + "-HBP"
            walks = sum(game_pitching[wlab])
            strikeouts = sum(game_pitching[klab])
            hbp = sum(game_pitching[hbplab])
            hits = sum(game_summary[tlab]['batting']['H'])

            # Strikeout
            if strikeouts >= self.PITCHING_SO:
                gem_list.append(make_so_gem(
                    pitcher_name,
                    pitcher_team,
                    other_team,
                    strikeouts,
                ))

            # Low hitter
            if hits <= self.PITCHING_LO_HIT:
                gem_list.append(make_lowhitter_gem(
                    pitcher_name,
                    pitcher_team,
                    other_team,
                    hits,
                    walks,
                    strikeouts,
                ))

            # Low walk
            if walks <= self.PITCHING_BB_LO:
                gem_list.append(make_lobb_gem(
                    pitcher_name,
                    pitcher_team,
                    other_team,
                    walks,
                ))

            # High walk
            if walks >= self.PITCHING_BB_HI:
                gem_list.append(make_hibb_gem(
                    pitcher_name,
                    pitcher_team,
                    other_team,
                    walks,
                ))

        # Based on hit/run statistics:
        def make_hitless_gem(player_name, team_name, versus_team_name, inning_start, inning_end):
            """N consecutive hitless innings"""
            length = inning_end - inning_start + 1
            d = dict(
                gem_type="pitching_hitless",
                gem_class="pitching",
                gem_description="%s (%s) held the %s hitless for %d innings (%d thru %d)."%(
                    player_name,
                    team_name,
                    versus_team_name,
                    length,
                    inning_start,
                    inning_end,
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        def make_scoreless_gem(player_name, team_name, versus_team_name, inning_start, inning_end):
            """N consecutive scoreless innings"""
            length = inning_end - inning_start + 1
            d = dict(
                gem_type="pitching_scoreless",
                gem_class="pitching",
                gem_description="%s (%s) held the %s scoreless for %d innings (%d thru %d)."%(
                    player_name,
                    team_name,
                    versus_team_name,
                    length,
                    inning_start,
                    inning_end,
                ),
                gem_team=team_name,
                gem_player=player_name,
            )
            return d

        for htat in ['home', 'away']:
            them = 'home' if htat=='away' else 'away'
            runs = game_line[htat]
            hits = game_summary[htat]['batting']['H']

            # Hitless/scoreless happend to us, so pick the other pitcher
            if game_box[htat] > game_box[them]:
                pitcher_name = game_pitching['LP']
            else:
                pitcher_name = game_pitching['WP']

            team_name = game_info["%sTeamNickname"%(them)]  # them
            versus_name = game_info["%sTeamNickname"%(htat)]  # us

            # Hold on to your butts

            # Hitless:
            inning_counter0 = 0
            for k, g in groupby(hits):
                group = list(g)
                if k==0:
                    # This contains grouped consecutive scoreless innings
                    if len(group) > self.PITCHING_HITLESS:
                        # Rack it
                        inning_start0 = inning_counter0
                        inning_end0 = inning_counter0 + len(group) - 1
                        gem_list.append(make_hitless_gem(
                            pitcher_name,
                            team_name,
                            versus_name,
                            inning_start0 + 1,
                            inning_end0 + 1
                        ))
                inning_counter0 += len(group)

            # Runless:
            inning_counter0 = 0
            for k, g in groupby(runs):
                groups = list(g)
                if k==0:
                    # This contains grouped consecutive scoreless innings
                    if len(group) > self.PITCHING_SCORELESS:
                        # Rack it
                        inning_start0 = inning_counter0
                        inning_end0 = inning_counter0 + len(group) - 1
                        gem_list.append(make_scoreless_gem(
                            pitcher_name,
                            team_name,
                            versus_name,
                            inning_start0 + 1,
                            inning_end0 + 1
                        ))
                inning_counter0 += len(group)


        # -----------------------
        # Return the final result

        gems_json['gems'] = gem_list
        return gems_json
