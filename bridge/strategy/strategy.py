"""Верхнеуровневый код стратегии"""

# pylint: disable=redefined-outer-name

# @package Strategy
# Расчет требуемых положений роботов исходя из ситуации на поле


import math

# !v DEBUG ONLY
from enum import Enum
from time import time
from typing import Optional

import bridge.router.waypoint as wp
from bridge import const
from bridge.auxiliary import aux, fld, rbt
from bridge.processors.referee_state_processor import Color as ActiveTeam
from bridge.processors.referee_state_processor import State as GameStates
from bridge.strategy import ref_states

class Strategy:
    """Основной класс с кодом стратегии"""

    def __init__(
        self,
        dbg_game_status: GameStates = GameStates.RUN,
    ) -> None:

        self.game_status = dbg_game_status
        self.active_team: ActiveTeam = ActiveTeam.ALL


    def process(self, field: fld.Field) -> list[wp.Waypoint]:
        """
        Рассчитать конечные точки для каждого робота
        """
        waypoints: list[wp.Waypoint] = []
        for i in range(const.TEAM_ROBOTS_MAX_COUNT):
            waypoints.append(
                wp.Waypoint(
                    field.allies[i].get_pos(),
                    field.allies[i].get_angle(),
                    wp.WType.S_ENDPOINT
                )
            )

#ROBOT_NUMBERS_________________________________________________________________________________________________________________________________________________________________________________________________________________________________
        enemy_attack = 1
        ally_attack = 1
        enemy_goalkeeper = 0
        ally_goalkeeper = 0
        enemy_defender = 2
        ally_defender = 2

#VARIABLES_____________________________________________________________________________________________________________________________________________________________________________________________________________________________________
        vec = aux.Point(0, 380)
        wall_vec = aux.Point(0, const.ROBOT_R)
        enemy_GK = field.enemies[enemy_goalkeeper].get_pos()
        ally_GK = field.allies[ally_goalkeeper].get_pos()
        enemy_defender_pos = field.enemies[enemy_defender].get_pos()
        enemy_goal = field.enemy_goal.center
        st_kick = enemy_goal + vec
        nd_kick = enemy_goal - vec
        goal_pos = field.ally_goal.center
        goalk_pos = aux.Point(1400 * field.polarity, goal_pos.y)
        ally_attacker_pos = field.allies[ally_attack].get_pos()
        ally_defender_pos = field.allies[ally_defender].get_pos()
        ball_pos = field.ball.get_pos()
        point1 = aux.Point(1400 * field.polarity, 480)
        point2 = aux.Point(1400 * field.polarity, -480)
        ball_predict = ball_pos + field.ball.get_vel()
        enemy_attacker_pos = field.enemies[enemy_attack].get_pos()
        if aux.dist(field.ally_goal.center, enemy_attacker_pos) < aux.dist(field.ally_goal.center, enemy_defender_pos): the_closest_enemy_number = enemy_attack
        else: the_closest_enemy_number = enemy_defender
        the_closest_enemy_pos = field.enemies[the_closest_enemy_number].get_pos()
        attacker_angle = field.enemies[the_closest_enemy_number].get_angle()
        look_vec = aux.rotate(aux.Point(1400, 0), field.enemies[enemy_attack].get_angle())
        my_pos = field.allies[ally_goalkeeper].get_pos()
        vec_sides = aux.rotate(aux.Point(500, 0), (ball_pos - my_pos).arg())
        goal_up = aux.Point(goal_pos.x, (goal_pos.y))
        goal_down  = aux.Point(goal_pos.x, (goal_pos.y))
        bite = 0
        pas = 0
        if (ally_attacker_pos - ball_pos).mag() < (ally_defender_pos - ball_pos).mag(): biter = ally_attack
        else: biter = ally_defender
        biter_pos = field.allies[biter].get_pos()
        if biter_pos.x * field.polarity > enemy_attacker_pos.x * field.polarity: bite += 1
        if biter_pos.x * field.polarity > enemy_defender_pos.x * field.polarity: bite += 2
        if biter_pos.x * field.polarity > enemy_GK.x * field.polarity: bite += 4
        if min(aux.dist(ball_pos, ally_attacker_pos), aux.dist(ball_pos, ally_attacker_pos)) == aux.dist(ball_pos, ally_attacker_pos):
            closest_to_ball_ally = ally_attack
            farest_to_ball_ally = ally_defender
        else:
            closest_to_ball_ally = ally_defender
            farest_to_ball_ally = ally_attack
        closest_to_ball_ally_pos = field.allies[closest_to_ball_ally].get_pos()
        farest_to_ball_ally_pos = field.allies[farest_to_ball_ally].get_pos()
       

#GOALKEAPER____________________________________________________________________________________________________________________________________________________________________________________________________________________________________
        if aux.dist(ball_pos, ally_attacker_pos) > aux.dist(ball_pos, ally_defender_pos): to_who_pas = ally_defender
        else: to_who_pas = ally_attack
        ally_to_pas = field.allies[to_who_pas].get_pos()

        if field.is_ball_stop_near_goal():
            pas = 2
            if min(aux.dist2line(ally_GK, ally_to_pas, enemy_attacker_pos), aux.dist2line(ally_GK, ally_to_pas, enemy_defender_pos), aux.dist2line(ally_GK, ally_to_pas, enemy_GK) < const.ROBOT_R):
                waypoints[ally_goalkeeper] = wp.Waypoint(ball_pos, (ally_to_pas - ball_pos).arg(), wp.WType.S_BALL_KICK_UP)
            else:
                waypoints[ally_goalkeeper] = wp.Waypoint(ball_pos, (ally_to_pas - ball_pos).arg(), wp.WType.S_BALL_KICK)
        else:
            # if not field.is_ball_moves():st_kick = enemy_goal + vec
            #     pas = 0
            waypoints[ally_goalkeeper] = wp.Waypoint(goalk_pos, (the_closest_enemy_pos - ally_GK).arg(), wp.WType.S_ENDPOINT)
        if field.is_ball_moves() and ball_pos.x * field.polarity > 0:
            if aux.closest_point_on_line(ball_pos, ball_predict, my_pos) is not None:
                goalk_pos = aux.closest_point_on_line(ball_pos, ball_predict, my_pos)
            else:
                goalk_pos = ball_pos
        else:
            if the_closest_enemy_pos.x * field.polarity > 0 and ball_pos.x  * field.polarity > 0: 
                goalk_pos = the_closest_enemy_pos + aux.rotate(aux.Point(400, 0), attacker_angle)
            elif aux.get_line_intersection(point1, point2, the_closest_enemy_pos, look_vec) is not None and abs(the_closest_enemy_pos.y) < 500: 
                goalk_pos = aux.Point(aux.get_line_intersection(point1, point2, the_closest_enemy_pos, look_vec).x, aux.get_line_intersection(point1, point2, the_closest_enemy_pos, look_vec).y)
            if ball_pos.y < -500 * field.polarity:
                goalk_pos = goal_down + vec_sides
            elif ball_pos.y > 500 * field.polarity: 
                goalk_pos = goal_up + vec_sides

#FIELD ROBOTS__________________________________________________________________________________________________________________________________________________________________________________________________________________________________
        if abs(ally_defender_pos.y) > 300:
            waypoints[ally_defender] = wp.Waypoint(aux.Point(ball_pos.x + 500, -ally_attacker_pos.y), (ball_pos - ally_defender_pos).arg(),  wp.WType.S_ENDPOINT)
        if abs(ally_attacker_pos.y) > 300:
            waypoints[ally_attack] = wp.Waypoint(aux.Point(ball_pos.x + 500, -ally_defender_pos.y), (ball_pos - ally_attacker_pos).arg(),  wp.WType.S_ENDPOINT)
        
        if min(aux.dist(ball_pos, enemy_attacker_pos), aux.dist(ball_pos, enemy_defender_pos), aux.dist(ball_pos, enemy_GK)) < min(aux.dist(ball_pos, ally_attacker_pos), aux.dist(ball_pos, ally_defender_pos), aux.dist(ball_pos, ally_GK)) and pas != 2:
            if min(aux.dist(ball_pos, enemy_attacker_pos), aux.dist(ball_pos, enemy_defender_pos), aux.dist(ball_pos, enemy_GK)) == aux.dist(ball_pos, enemy_GK):
                if enemy_GK.x * field.polarity < enemy_attacker_pos.x * field.polarity:
                    if enemy_GK.x * field.polarity < enemy_defender_pos.x * field.polarity:
                        if min((enemy_GK - field.ally_goal.up).arg(), (enemy_GK - field.ally_goal.down).arg()) == (enemy_GK - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_GK, field.ally_goal.up, ally_defender_pos, 'S') + wall_vec
                            attacker_need_pos = defender_need_pos - wall_vec - wall_vec
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_GK, field.ally_goal.down, ally_defender_pos, 'S') + wall_vec
                            attacker_need_pos = defender_need_pos - wall_vec - wall_vec
                    else:
                        attacker_need_pos = aux.closest_point_on_line(enemy_GK, enemy_defender_pos, ally_attacker_pos, 'S')
                        if min((enemy_GK - field.ally_goal.up).arg(), (enemy_GK - field.ally_goal.down).arg()) == (enemy_GK - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_GK, field.ally_goal.up, ally_defender_pos, 'S')
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_GK, field.ally_goal.down, ally_defender_pos, 'S')
                else:
                    if enemy_GK.x * field.polarity < enemy_defender_pos.x * field.polarity:
                        attacker_need_pos = aux.closest_point_on_line(enemy_GK, enemy_attacker_pos, ally_attacker_pos, 'S')
                        if min((enemy_GK - field.ally_goal.up).arg(), (enemy_GK - field.ally_goal.down).arg()) == (enemy_GK - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_GK, field.ally_goal.up, ally_defender_pos, 'S')
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_GK, field.ally_goal.down, ally_defender_pos, 'S')
                    else:
                        attacker_need_pos = aux.closest_point_on_line(enemy_GK, enemy_defender_pos, ally_attacker_pos, 'S')
                        defender_need_pos = aux.closest_point_on_line(enemy_attacker_pos, enemy_GK, ally_defender_pos, 'S')
                        
                    

            elif min(aux.dist(ball_pos, enemy_attacker_pos), aux.dist(ball_pos, enemy_defender_pos), aux.dist(ball_pos, enemy_GK)) == aux.dist(ball_pos, enemy_defender_pos):
                if enemy_defender_pos.x * field.polarity > enemy_attacker_pos.x * field.polarity:
                    if enemy_defender_pos.x * field.polarity > enemy_GK.x * field.polarity:
                        if min((enemy_defender_pos - field.ally_goal.up).arg(), (enemy_defender_pos - field.ally_goal.down).arg()) == (enemy_defender_pos - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_defender_pos, field.ally_goal.up, ally_defender_pos, 'S') + wall_vec
                            attacker_need_pos = defender_need_pos - wall_vec - wall_vec
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_defender_pos, field.ally_goal.down, ally_defender_pos, 'S') + wall_vec
                            attacker_need_pos = defender_need_pos - wall_vec - wall_vec
                    else:
                        attacker_need_pos = aux.closest_point_on_line(enemy_defender_pos, enemy_GK, ally_attacker_pos, 'S')
                        if min((enemy_defender_pos - field.ally_goal.up).arg(), (enemy_defender_pos - field.ally_goal.down).arg()) == (enemy_defender_pos - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_defender_pos, field.ally_goal.up, ally_defender_pos, 'S')
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_defender_pos, field.ally_goal.down, ally_defender_pos, 'S')
                else:
                    if enemy_defender_pos.x * field.polarity < enemy_GK.x * field.polarity:
                        attacker_need_pos = aux.closest_point_on_line(enemy_defender_pos, enemy_attacker_pos, ally_attacker_pos, 'S')
                        if min((enemy_defender_pos - field.ally_goal.up).arg(), (enemy_defender_pos - field.ally_goal.down).arg()) == (enemy_defender_pos - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_defender_pos, field.ally_goal.up, ally_defender_pos, 'S')
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_defender_pos, field.ally_goal.down, ally_defender_pos, 'S')
                    else:
                        attacker_need_pos = aux.closest_point_on_line(enemy_defender_pos, enemy_GK, ally_attacker_pos, 'S')
                        defender_need_pos = aux.closest_point_on_line(enemy_defender_pos, enemy_attacker_pos, ally_defender_pos, 'S')



            else:
                if enemy_attacker_pos.x * field.polarity > enemy_defender_pos.x * field.polarity:
                    if enemy_attacker_pos.x * field.polarity > enemy_GK.x * field.polarity:
                        if min((enemy_attacker_pos - field.ally_goal.up).arg(), (enemy_attacker_pos - field.ally_goal.down).arg()) == (enemy_attacker_pos - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_attacker_pos, field.ally_goal.up, ally_defender_pos, 'S') + wall_vec
                            attacker_need_pos = defender_need_pos - wall_vec - wall_vec
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_attacker_pos, field.ally_goal.down, ally_defender_pos, 'S') + wall_vec
                            attacker_need_pos = defender_need_pos - wall_vec - wall_vec
                    else:
                        attacker_need_pos = aux.closest_point_on_line(enemy_attacker_pos, enemy_GK, ally_attacker_pos, 'S')
                        if min((enemy_attacker_pos - field.ally_goal.up).arg(), (enemy_attacker_pos - field.ally_goal.down).arg()) == (enemy_attacker_pos - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_attacker_pos, field.ally_goal.up, ally_defender_pos, 'S')
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_attacker_pos, field.ally_goal.down, ally_defender_pos, 'S')
                else:
                    if enemy_attacker_pos.x * field.polarity > enemy_GK.x * field.polarity:
                        attacker_need_pos = aux.closest_point_on_line(enemy_attacker_pos, enemy_defender_pos, ally_attacker_pos, 'S')
                        if min((enemy_attacker_pos - field.ally_goal.up).arg(), (enemy_attacker_pos - field.ally_goal.down).arg()) == (enemy_attacker_pos - field.ally_goal.up).arg():
                            defender_need_pos = aux.closest_point_on_line(enemy_attacker_pos, field.ally_goal.up, ally_defender_pos, 'S')
                        else:
                            defender_need_pos = aux.closest_point_on_line(enemy_attacker_pos, field.ally_goal.down, ally_defender_pos, 'S')
                    else:
                        attacker_need_pos = aux.closest_point_on_line(enemy_attacker_pos, enemy_GK, ally_attacker_pos, 'S')
                        defender_need_pos = aux.closest_point_on_line(enemy_attacker_pos, enemy_defender_pos, ally_defender_pos, 'S')

            waypoints[ally_defender] = wp.Waypoint(defender_need_pos, (ball_pos - ally_defender_pos).arg(), wp.WType.S_ENDPOINT)
            waypoints[ally_attack] = wp.Waypoint(attacker_need_pos, (ball_pos - ally_attacker_pos).arg(), wp.WType.S_ENDPOINT)
            

        elif min(aux.dist(ball_pos, enemy_attacker_pos), aux.dist(ball_pos, enemy_defender_pos), aux.dist(ball_pos, enemy_GK)) < 500 and (ally_attacker_pos - ally_defender_pos).mag() > 500:
            if min(aux.dist2line(closest_to_ball_ally_pos, farest_to_ball_ally_pos, enemy_attacker_pos), aux.dist2line(closest_to_ball_ally_pos, farest_to_ball_ally_pos, enemy_defender_pos), aux.dist2line(closest_to_ball_ally_pos, farest_to_ball_ally_pos, enemy_GK) < const.ROBOT_R):
                waypoints[closest_to_ball_ally] = wp.Waypoint(ball_pos, (farest_to_ball_ally_pos - ball_pos).arg(), wp.WType.S_BALL_KICK_UP)
            else:
                waypoints[closest_to_ball_ally] = wp.Waypoint(ball_pos, (farest_to_ball_ally_pos - ball_pos).arg(), wp.WType.S_BALL_KICK)

        
        
        else:
            defender_and_attaker = aux.Point((enemy_defender_pos.x + enemy_attacker_pos.x) / 2, (enemy_defender_pos.y + enemy_attacker_pos.y) / 2)
            defender_and_goalkeaper = aux.Point((enemy_defender_pos.x + enemy_GK.x) / 2, (enemy_defender_pos.y + enemy_GK.y) / 2)
            attaker_and_goalkeaper = aux.Point((enemy_GK.x + enemy_attacker_pos.x) / 2, (enemy_GK.y + enemy_attacker_pos.y) / 2)
            
            gate_intersection_defender_and_attaker = aux.get_line_intersection(ball_pos, defender_and_attaker, field.enemy_goal.down, field.enemy_goal.up, "RS")
            gate_intersection_defender_and_goalkeaper = aux.get_line_intersection(ball_pos, defender_and_goalkeaper, field.enemy_goal.down, field.enemy_goal.up, "RS")
            gate_intersection_attaker_and_goalkeaper = aux.get_line_intersection(ball_pos, attaker_and_goalkeaper, field.enemy_goal.down, field.enemy_goal.up, "RS")

            if bite == 0:
                angle_to_shot = (field.enemy_goal.center - ball_pos).arg()

            if bite == 7:
                    if enemy_attacker_pos.x > enemy_defender_pos.x and enemy_attacker_pos.x < enemy_GK.x:
                        central = enemy_attack
                        the_hiest = enemy_goalkeeper
                        the_lowest = enemy_defender
                    elif enemy_attacker_pos.x < enemy_defender_pos.x and enemy_attacker_pos.x > enemy_GK.x:
                        central = enemy_attack
                        the_hiest = enemy_defender
                        the_lowest = enemy_goalkeeper
                    elif enemy_defender_pos.x < enemy_attacker_pos.x and enemy_defender_pos.x > enemy_GK.x:
                        central = enemy_defender
                        the_hiest = enemy_attack
                        the_lowest = enemy_goalkeeper
                    elif enemy_defender_pos.x > enemy_attacker_pos.x and enemy_defender_pos.x < enemy_GK.x:
                        central = enemy_defender
                        the_hiest = enemy_goalkeeper
                        the_lowest = enemy_attack
                    elif enemy_GK.x > enemy_attacker_pos.x and enemy_GK.x < enemy_defender_pos.x:
                        central = enemy_goalkeeper
                        the_hiest = enemy_defender
                        the_lowest = enemy_attack
                    else:
                        central = enemy_goalkeeper
                        the_hiest = enemy_attack
                        the_lowest = enemy_defender

                    central_pos = field.enemies[central].get_pos()
                    hiest_pos = field.enemies[the_hiest].get_pos()
                    lowest_pos = field.enemies[the_lowest].get_pos()

                    hiest_and_central = aux.Point((hiest_pos.x + central_pos.x) / 2, (hiest_pos.y + central_pos.y) / 2)
                    lowest_and_central = aux.Point((lowest_pos.x + central_pos.x) / 2, (lowest_pos.y + central_pos.y) / 2)

                    gate_intersection_hiest_and_central = aux.get_line_intersection(ball_pos, hiest_and_central, goal_down, goal_up, 'RS')
                    gate_intersection_lowest_and_central = aux.get_line_intersection(ball_pos, lowest_and_central, goal_down, goal_up, 'RS')

                    if gate_intersection_hiest_and_central is not None and gate_intersection_lowest_and_central is not None:
                        angle_between_hiest_and_central = (hiest_and_central - ball_pos).arg()
                        angle_between_lowest_and_central = (lowest_and_central - ball_pos).arg()
                        hiest_dist = aux.dist2line(ball_pos, gate_intersection_hiest_and_central, hiest_pos)
                        lowest_dist = aux.dist2line(ball_pos, gate_intersection_lowest_and_central, lowest_pos)
                        up_central_dist = aux.dist2line(ball_pos, gate_intersection_hiest_and_central, central)
                        dn_central_dist = aux.dist2line(ball_pos, gate_intersection_lowest_and_central, central)
                        if aux.dist2line(ball_pos, st_kick, hiest_pos) < aux.dist2line(ball_pos, st_kick, central_pos): st_closest = hiest_pos
                        else: st_closest = central_pos
                        if aux.dist2line(ball_pos, nd_kick, lowest_pos) < aux.dist2line(ball_pos, nd_kick, central_pos): nd_closest = lowest_dist
                        else: nd_closest = central_pos
                        st_dist = aux.dist2line(ball_pos, st_kick, st_closest)
                        nd_dist = aux.dist2line(ball_pos, nd_kick, nd_closest)
                        max_dist = max(min(hiest_dist, up_central_dist), min(lowest_dist, dn_central_dist), st_dist, nd_dist)
                        if max_dist == hiest_dist or max_dist == up_central_dist: angle_to_shot = angle_between_lowest_and_central
                        elif max_dist == lowest_dist or max_dist == dn_central_dist: angle_to_shot = angle_between_hiest_and_central
                        elif max_dist == st_dist: angle_to_shot = (st_kick - ball_pos).arg()
                        else: angle_to_shot = (nd_kick - ball_pos).arg()

                    elif gate_intersection_hiest_and_central is None:
                        if gate_intersection_lowest_and_central is not None:
                            if the_hiest == enemy_attack:bite = 5
                            elif the_hiest == enemy_goalkeeper:bite = 3
                            else:bite = 6
                        else:
                            if central == enemy_goalkeeper:bite = 4
                            elif central == enemy_attack:bite = 1
                            else: bite = 2
                    else:
                        if the_lowest == enemy_attack:bite = 5
                        elif the_lowest == enemy_goalkeeper:bite = 3
                        else:bite = 6


            if bite == 3:
                if gate_intersection_defender_and_attaker is not None:
                    angle_between = (defender_and_attaker - ball_pos).arg()

                    defender_dist = aux.dist2line(ball_pos, gate_intersection_defender_and_attaker, enemy_defender_pos)
                    attacker_dist = aux.dist2line(ball_pos, gate_intersection_defender_and_attaker, enemy_attacker_pos)
                    if aux.dist2line(ball_pos, st_kick, enemy_attacker_pos) < aux.dist2line(ball_pos, st_kick, enemy_defender_pos): st_closest = enemy_attacker_pos
                    else: st_closest = enemy_defender_pos
                    if aux.dist2line(ball_pos, nd_kick, enemy_attacker_pos) < aux.dist2line(ball_pos, nd_kick, enemy_defender_pos): nd_closest = enemy_attacker_pos
                    else: nd_closest = enemy_defender_pos
                    st_dist = aux.dist2line(ball_pos, st_kick, st_closest)
                    nd_dist = aux.dist2line(ball_pos, nd_kick, nd_closest)
                    max_dist = max(defender_dist, attacker_dist, min(st_dist, nd_dist))
                    if max_dist == defender_dist or max_dist == attacker_dist: angle_to_shot = angle_between
                    elif max_dist == st_dist: angle_to_shot = (st_kick - ball_pos).arg()
                    else: angle_to_shot = (nd_kick - ball_pos).arg()

                else:
                    if aux.get_line_intersection(biter_pos, enemy_defender_pos, goal_down, goal_up, 'RS') is not None:bite = 2
                    else:bite = 1

            if bite == 5:
                if gate_intersection_defender_and_goalkeaper is not None:
                    angle_between = (defender_and_goalkeaper - ball_pos).arg()

                    defender_dist = aux.dist2line(ball_pos, gate_intersection_defender_and_goalkeaper, enemy_defender_pos)
                    goalkeaper_dist = aux.dist2line(ball_pos, gate_intersection_defender_and_goalkeaper, enemy_GK)
                    if aux.dist2line(ball_pos, st_kick, enemy_GK) < aux.dist2line(ball_pos, st_kick, enemy_defender_pos): st_closest = enemy_GK
                    else: st_closest = enemy_defender_pos
                    if aux.dist2line(ball_pos, nd_kick, enemy_GK) < aux.dist2line(ball_pos, nd_kick, enemy_defender_pos): nd_closest = enemy_GK
                    else: nd_closest = enemy_defender_pos
                    st_dist = aux.dist2line(ball_pos, st_kick, st_closest)
                    nd_dist = aux.dist2line(ball_pos, nd_kick, nd_closest)
                    max_dist = max(defender_dist, goalkeaper_dist, min(st_dist, nd_dist))
                    if max_dist == defender_dist or max_dist == goalkeaper_dist: angle_to_shot = angle_between
                    elif max_dist == st_dist: angle_to_shot = (st_kick - ball_pos).arg()
                    else: angle_to_shot = (nd_kick - ball_pos).arg()

                else:
                    if aux.get_line_intersection(biter_pos, enemy_defender_pos, goal_down, goal_up, 'RS') is not None:bite = 1
                    else:bite = 4

            if bite == 6:
                if gate_intersection_attaker_and_goalkeaper is not None:
                    angle_between = (attaker_and_goalkeaper - ball_pos).arg()

                    goalkeaper_dist = aux.dist2line(ball_pos, gate_intersection_attaker_and_goalkeaper, enemy_GK)
                    attacker_dist = aux.dist2line(ball_pos, gate_intersection_attaker_and_goalkeaper, enemy_attacker_pos)
                    if aux.dist2line(ball_pos, st_kick, enemy_attacker_pos) < aux.dist2line(ball_pos, st_kick, enemy_GK): st_closest = enemy_attacker_pos
                    else: st_closest = enemy_GK
                    if aux.dist2line(ball_pos, nd_kick, enemy_attacker_pos) < aux.dist2line(ball_pos, nd_kick, enemy_GK): nd_closest = enemy_attacker_pos
                    else: nd_closest = enemy_GK
                    st_dist = aux.dist2line(ball_pos, st_kick, st_closest)
                    nd_dist = aux.dist2line(ball_pos, nd_kick, nd_closest)
                    max_dist = max(attacker_dist, goalkeaper_dist, min(st_dist, nd_dist))
                    if max_dist == attacker_dist or max_dist == goalkeaper_dist: angle_to_shot = angle_between
                    elif max_dist == st_dist: angle_to_shot = (st_kick - ball_pos).arg()
                    else: angle_to_shot = (nd_kick - ball_pos).arg()

                else:
                    if aux.get_line_intersection(biter_pos, enemy_GK, goal_down, goal_up, 'RS') is not None:bite = 4
                    else:bite = 2


            if bite == 4 or bite == 2 or bite == 1:
                if bite == 4:
                    angle1 = abs(aux.get_angle_between_points(enemy_GK, ball_pos, st_kick))
                    angle2 = abs(aux.get_angle_between_points(enemy_GK, ball_pos, nd_kick))
                elif bite == 2:
                    angle1 = abs(aux.get_angle_between_points(enemy_defender_pos, ball_pos, st_kick))
                    angle2 = abs(aux.get_angle_between_points(enemy_defender_pos, ball_pos, nd_kick))
                else:
                    angle1 = abs(aux.get_angle_between_points(enemy_attacker_pos, ball_pos, st_kick))
                    angle2 = abs(aux.get_angle_between_points(enemy_attacker_pos, ball_pos, nd_kick))
                if angle1 > angle2:angle_to_shot = (st_kick - ball_pos).arg()
                else:angle_to_shot = (nd_kick - ball_pos).arg()
            

            waypoints[biter] = wp.Waypoint(ball_pos, angle_to_shot, wp.WType.S_BALL_KICK)


        # elif field.is_ball_stop_near_goal():
        #     waypoints[ally_defender] = wp.Waypoint(aux.Point(0, 0), (ally_defender_pos - ball_pos).arg(),  wp.WType.S_ENDPOINT)
        #     waypoints[ally_attack] = wp.Waypoint(field.enemy_goal.center, (ally_attacker_pos - ball_pos).arg(),  wp.WType.S_ENDPOINT)
        
        # elif (ally_attacker_pos - ball_pos).mag() < (ally_defender_pos - ball_pos).mag():
        #     if abs(ally_attacker_pos.y) > 200:
        #         waypoints[ally_defender] = wp.Waypoint(aux.Point(ball_pos.x, -ally_attacker_pos.y), 0,  wp.WType.S_ENDPOINT)
        #     if angle1 > angle2:
        #         angle_to_shot = (st_kick - ball_pos).arg()
        #         waypoints[ally_attack] = wp.Waypoint(ball_pos, angle_to_shot, wp.WType.S_BALL_KICK)
        #     else:
        #         angle_to_shot = (nd_kick - ball_pos).arg()
        #         waypoints[ally_attack] = wp.Waypoint(ball_pos, angle_to_shot, wp.WType.S_BALL_KICK)

        # else:
        #     if abs(ally_defender_pos.y) > 200:
        #         waypoints[ally_attack] = wp.Waypoint(aux.Point(ball_pos.x, -ally_defender_pos.y), 0,  wp.WType.S_ENDPOINT)

        #     if angle1 > angle2:
        #         angle_to_shot = (st_kick - ball_pos).arg()
        #         waypoints[ally_defender] = wp.Waypoint(ball_pos, angle_to_shot, wp.WType.S_BALL_KICK)
        #     else:
        #         angle_to_shot = (nd_kick - ball_pos).arg()
        #         waypoints[ally_defender] = wp.Waypoint(ball_pos, angle_to_shot, wp.WType.S_BALL_KICK)

        if pas == 2:
            waypoints[to_who_pas] = wp.Waypoint(aux.Point(0 * field.polarity, ball_pos.y), (ally_to_pas - ally_GK).arg() + math.pi, wp.WType.S_ENDPOINT)
            if field.ball.get_vel().mag() < 0.1:
                pas = 0

        
        
        return waypoints