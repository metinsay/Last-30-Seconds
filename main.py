from expectiminimax import run_expectiminimax, Team, GameState


if __name__ == "__main__":

    cur_three_perc = .391 #0.354
    cur_two_perc = .560 #0.505
    cur_ft_perc = .815 #0.715
    cur_three_defen_perc = .357 #0.367
    cur_two_defen_perc = .490 #0.511
    opp_three_perc = 0.357
    opp_two_perc = 0.519
    opp_ft_perc = 0.804
    opp_three_defen_perc = 0.366
    opp_two_defen_perc = 0.534

    team1 = Team(cur_three_perc, cur_two_perc, cur_ft_perc, cur_three_defen_perc, cur_two_defen_perc)
    team2 = Team(opp_three_perc, opp_two_perc, opp_ft_perc, opp_three_defen_perc, opp_two_defen_perc)
    
    score_diff = -1 # Points
    time = 30 # Seconds left
    pos = 1 # We have the ball

    depth = float("inf") # Max depth the tree can go

    game_state = GameState(team1, team2, score_diff, time, pos)
    max_prob = run_expectiminimax(game_state, depth)
    print("The maximum expected win probability is " + str(max_prob) + ".")
