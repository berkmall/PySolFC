## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##


# imports
import os, sys, time, types

# PySol imports
from mfxutil import format_time
from settings import PACKAGE, VERSION
from gamedb import GI


# /***********************************************************************
# //
# ************************************************************************/

class PysolStatsFormatter:

    def getStatHeader(self):
        return (_("Game"),
                _("Played"),
                _("Won"),
                _("Lost"),
                _('Playing time'),
                _('Moves'),
                _("% won"))

    def getStatResults(self, player, sort_by='name'):
        app = self.app
        #
        sort_functions = {
            'name':    app.getGamesIdSortedByName,
            'played':  app.getGamesIdSortedByPlayed,
            'won':     app.getGamesIdSortedByWon,
            'lost':    app.getGamesIdSortedByLost,
            'time':    app.getGamesIdSortedByPlayingTime,
            'moves':   app.getGamesIdSortedByMoves,
            'percent': app.getGamesIdSortedByPercent,
            }
        sort_func = sort_functions[sort_by]
        g = sort_func(player=player)
        twon, tlost, tgames, ttime, tmoves = 0, 0, 0, 0, 0
        for id in g:
            name = app.getGameTitleName(id)
            #won, lost = app.stats.getStats(player, id)
            won, lost, time, moves = app.stats.getFullStats(player, id)
            twon, tlost = twon + won, tlost + lost
            ttime, tmoves = ttime+time, tmoves+moves
            if won + lost > 0: perc = "%.1f" % (100.0 * won / (won + lost))
            else: perc = "0.0"
            if won > 0 or lost > 0 or id == app.game.id:
                t = format_time(time)
                m = str(round(moves, 1))
                yield [name, won+lost, won, lost, t, m, perc, id]
                tgames = tgames + 1
        won, lost = twon, tlost
        if won + lost > 0:
            if won > 0:
                time = format_time(ttime/tgames)
                moves = round(tmoves/tgames, 1)
            else:
                time = format_time(0)
                moves = 0
            perc = "%.1f" % (100.0*won/(won+lost))
        else: perc = "0.0"
        self.total_games = len(g)
        self.played_games = tgames
        self.won_games = won
        self.lost_games = lost
        self.avrg_time = time
        self.avrg_moves = moves
        self.percent = perc
        #yield (_("Total (%d out of %d games)") % (tgames, len(g)),
        #       won+lost, won, lost, time, moves, perc, '')

    def getStatSummary(self):
        return self.total_games, \
               self.played_games, \
               self.won_games, \
               self.lost_games, \
               self.avrg_time, \
               self.avrg_moves, \
               self.percent

    def getLogHeader(self):
        return _("Game"), _("Game number"), _("Started at"), _("Status")

    def getLogResults(self, player, prev_games):
        twon, tlost = 0, 0
        for pg in prev_games:
            if type(pg) is not types.TupleType:
                continue
            if len(pg) == 5:
                pg = pg + ("", None, None, 1)
            elif len(pg) == 7:
                pg = pg + (None, 1)
            elif len(pg) == 8:
                pg = pg + (1,)
            if len(pg) < 8:
                continue
            gameid = pg[0]
            if type(gameid) is not types.IntType:
                continue
            gi = self.app.getGameInfo(gameid)
            if not gi:
                gi = self.app.getGameInfo(GI.PROTECTED_GAMES.get(gameid))
            if gi:
                name = gi.short_name
            else:
                name = _("** UNKNOWN %d **") % gameid
            f = pg[1]
            if len(f) == 16:
                ##gamenumber = "%s-%s-%s-%s" % (f[0:4], f[4:8], f[8:12], f[12:16])
                gamenumber = "%s-%s-%s" % (f[4:8], f[8:12], f[12:16])
            elif len(f) <= 20:
                gamenumber = f
            else:
                gamenumber = _("** ERROR **")
            date = time.strftime("%Y-%m-%d  %H:%M", time.localtime(pg[3]))
            if pg[2] >= 0:
                won = pg[2] > 0
                twon, tlost = twon + won, tlost + (1 - won)
            status = "*error*"
            if -2 <= pg[2] <= 2:
                status = (_("Loaded"), _("Not won"), _("Lost"), _("Won"), _("Perfect")) [pg[2]+2]
            #writer.plog(name, gamenumber, date, status, gameid=gameid, won=pg[2])
            yield [name, gamenumber, date, status, pg[2], gameid]

    #
    #
    #

    def writeStats(self, player, sort_by='name'):
        pass
    def writeFullLog(self, player):
        pass
    def writeSessionLog(self, player):
        pass


class FileStatsFormatter(PysolStatsFormatter):

    def __init__(self, app, file):
        self.app = app
        self.file = file

    def p(self, s):
        self.file.write(s.encode('utf-8'))

    def nl(self, count=1):
        self.p("\n" * count)

    def pheader(self, s):
        self.p(s)

    def pstats(self, *args, **kwargs):
        s = "%-30s %7s %7s %7s %7s %7s %7s\n" % args
        self.p(s)

    def plog(self, gamename, gamenumber, date, status, gameid=-1, won=-1):
        self.p("%-25s %-20s  %17s  %s\n" % (gamename, gamenumber, date, status))

    def writeHeader(self, header, pagewidth=72):
        date = time.ctime(time.time())
        date = time.strftime("%Y-%m-%d  %H:%M", time.localtime(time.time()))
        blanks = max(pagewidth - len(header) - len(date), 1)
        self.pheader(header + " "*blanks + date + "\n")
        self.pheader("-" * pagewidth + "\n")
        self.pheader("\n")

    def writeStats(self, player, sort_by='name'):
        if player is None: player = _('Demo')
        header = _("Statistics for ") + player
        self.writeHeader(header, 62)
        header = self.getStatHeader()
        self.pstats(*header)
        self.nl()
        for result in self.getStatResults(player, sort_by):
            gameid = result.pop()
            self.pstats(gameid=gameid, *result)
        self.nl()
        total, played, won, lost, time, moves, perc = self.getStatSummary()
        self.pstats(_("Total (%d out of %d games)") % (played, total),
                      won+lost, won, lost, time, moves, perc)
        self.nl(2)
        return played

    def writeLog(self, player, header, prev_games):
        if not player or not prev_games:
            return 0
        self.writeHeader(header, 71)
        header = self.getLogHeader()
        self.plog(*header)
        self.nl()
        for result in self.getLogResults(player, prev_games):
            gameid = result.pop()
            won = result.pop()
            self.plog(gameid=gameid, won=won, *result)
        self.nl(2)
        return 1

    def writeFullLog(self, player):
        if player is None: player = _('Demo')
        header = _("Full log for ") + player
        prev_games = self.app.stats.prev_games.get(player)
        return self.writeLog(player, header, prev_games)

    def writeSessionLog(self, player):
        if player is None: player = _('Demo')
        header = _("Session log for ") + player
        prev_games = self.app.stats.session_games.get(player)
        return self.writeLog(player, header, prev_games)

