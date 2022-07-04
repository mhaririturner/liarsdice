#!/usr/bin/env python

"""
dice.py: Main driver file for the Liar's Dice solver
"""

__author__ = "Max Hariri-Turner"
__email__ = "maxkht8@gmail.com"

import math
import random

wildcard_value = 1

def predict_probability(x, y, n, d, hand):
  """
  Computes probability of a bid(x, y, n, d) for a known hand being correct
  Uses statistics black magic math to compute probability in a non-brute force manner.
  :param x: face value [2,6]
  :param y: count [1,15]
  :param n: total number of die in play >0 (15)
  :param d: how many sides the die have (6)
  :return: The probability
  """
  ext_n = n - len(hand)
  friendly_die = len([0 for die in hand if die == wildcard_value or die == x])
  ext_y = y - friendly_die
  #print(f"External die needed to satisfy bid: {ext_y}")
  if ext_y <=0:
    return 1 # Our hand satisfies our bid
  probability = 0
  for i in range(0, ext_n + 1): # +1 because inclusive
    #print(f"Considering case when {i} wildcard(s)")
    wildcard_p = math.comb(ext_n, i) * (1/d)**i * ((d-1)/d)**(ext_n - i)
    #print(f"P(exactly {i} wildcard) = {wildcard_p}")
    cum_sub_p = 0
    if i >= ext_y:
      # print(" ! Wildcard count covers bid, skipping subprobability computation")
      probability += wildcard_p
      cum_sub_p = 1
    else:
      for j in range(ext_y - i, ext_n - i + 1): # +1 because inclusive
        #print(f"   Considering subcase when {j} target card(s)")
        sub_p = math.comb(ext_n - i, j) * (1/(d-1))**j * ((d-2)/(d-1))**(ext_n-i-j)
        #print(f"   P(exactly {j} target card GIVEN) = {sub_p}")
        cum_sub_p += sub_p
      probability += wildcard_p * cum_sub_p
    #print(f"P({ext_y - i} or more target card GIVEN {i} wildcard) = {round(cum_sub_p, 4)}")
    #print(f"P({ext_y - i} or more target card AND exactly {i} wildcard) = {round(wildcard_p * cum_sub_p, 4)}")
  return probability

def simulate_probability(x, y, n, d, hand, iterations):
  """
  Computes simulated probability of a bid(x, y, n, d) for a known hand being correct.
  Uses brute force to actually simulate a given number of games and returns the empirical probability that the stated bid was correct.
  :param x: face value [2,6]
  :param y: count [1,15]
  :param n: total number of die in play >0
  :param d: how many sides the die have
  :param iterations: how many times to run the simulation
  :return: The probability
  """
  ext_n = n - len(hand)
  friendly_die = len([0 for die in hand if die == wildcard_value or die == x])
  ext_y = y - friendly_die
  if ext_y <=0:
    return 1 # Our hand satisfies our bid
  bid_success_count = 0
  wildcard_buckets = [0] * 10
  wc_p_buckets = []
  for i in range(0, iterations):
    dice = [random.randint(1, d) for die in range(ext_n)]
    x_count = len([0 for die in dice if die == x])
    wildcard_count = len([0 for die in dice if die == wildcard_value])
    if x_count + wildcard_count >= ext_y:
      bid_success_count += 1
      wildcard_buckets[wildcard_count] += 1
  for i in range(10):
    wc_p_buckets.append(round(wildcard_buckets[i] / iterations, 4))
  # print(wc_p_buckets)
  # print(wildcard_buckets)
  return bid_success_count / iterations

def compare_prediction_vs_simulation(x, y, n, d, hand, iterations):
  """
  Compares simulated and predicted probability of a bid(x, y, n, d) for a known hand being correct.
  This method was created to empirically verify the statistical math used for the predict_probability() method.
  :param x: face value [2,6]
  :param y: count [1,15]
  :param n: total number of die in play >0 (15)
  :param d: how many sides the die have (6)
  :param iterations: how many times to run the simulation portion
  :return: The difference in probability between the two methods
  """
  prediction_p = predict_probability(x, y, n, d, hand)
  simulation_p = simulate_probability(x, y, n, d, hand, iterations)
  print(f"\npredicted: {prediction_p}")
  print(f"simulated: {simulation_p}")
  difference = abs(prediction_p - simulation_p)
  print(f"difference: {round(100 * difference, 2)}%")
  return difference

def random_comparison(rounds, iterations):
  """
  Generates a specified number of random bids for random hands.
  Used for stress testing/seeding the next move algorithm.
  :param rounds: The number of random bid events to generate
  :param iterations: The number of iterations to run FOR EACH round
  :return: None
  """
  results = []
  for i in range(rounds):
    d = 6 # random.randint(2, 10)
    x = random.randint(2, d)
    y = random.randint(1, 15)
    n = 15
    hand = [random.randint(1, d) for die in range(5)]
    computation = compare_prediction_vs_simulation(x, y, n, d, hand, iterations)
    results.append(computation)
    #if computation > .05 or computation <.001:
      #print(x, y, n, d, hand)
  print(f"largest difference: {round(100 * max(results), 2)}%")

def compute_optimal_next_move(prev_x, prev_y, n, d, hand):
  """
  Given the previous player's bid of (prev_x, prev_y), generates a full probability table for
  every possible legal bid as well as identifying and displaying the statistically optimal action.
  :param prev_x: The face value of the previous player's bid
  :param prev_y: The count of the specified face value of the previous player's bid
  :param n: The total number of dice in play
  :param d: The number of faces on the die/dice in play
  :param hand: Your (NOT the previous player's) hand
  :return: None, but visually displays the probability table and optimal actions
  """
  print(prev_x, prev_y, hand)
  p_liar = 1 - predict_probability(prev_x, prev_y, n, d, hand)
  print(f"P(bluff) = {p_liar}")
  table = [[0 for i in range(d-1)] for j in range(n)]
  for i in range(1, n+1):
    for j in range(2, d+1):
      p = predict_probability(j, i, n, d, hand)
      #print(i, j-2, p)
      table[i-1][j-2] = p
  display(table)

  best_I_p = p_liar
  best_I_act = "call previous player"
  best_II_p = p_liar
  best_II_act = "call previous player"
  best_III_p = p_liar
  best_III_act = "call previous player"

  for i in range(len(table)):
    for j in range(len(table[i])):
      if table[i][j] > best_I_p and (i+1>prev_y or (j+2>prev_x and i+1 == prev_y)):
        best_I_p = table[i][j]
        best_I_act = f"bid({j+2}, {i+1})"
      if table[i][j] > best_II_p and (j+2>prev_x or (i+1>prev_y and j+2 == prev_x)):
        best_II_p = table[i][j]
        best_II_act = f"bid({j+2}, {i+1})"
      if table[i][j] > best_III_p and ((j+2>prev_x and i+1 == prev_y) or (i+1>prev_y and j+2 == prev_x)):
        best_III_p = table[i][j]
        best_III_act = f"bid({j+2}, {i+1})"
  print(f"Mode I optimal action: {best_I_act} ({round(best_I_p, 4)})")
  print(f"Mode II optimal action: {best_II_act} ({round(best_II_p, 4)})")
  print(f"Mode III optimal action: {best_III_act} ({round(best_III_p, 4)})")
      

def display(table):
  """
  Helper method to display the probability table.
  Everything is hard-coded and scuffed and evil but it gets the job done.
  :param table: The probability table to display
  :return: None, but visually displays the table
  """
  print(" y \\ x", end="")
  for i in range(len(table[0])):
    print(f"   {i+2}*     ", end="")
  print()
  for r, row in enumerate(table):
    print("{:>2}   ".format(r+1), end="")
    for col in table[r]:
      print("    {:.4f}".format(col), end="") # Help I don't know how string formatting works aaaaaah
    print()

def test_random_optimal_next_move():
  """
  Helper method to randomly seed the optimal move algorithm
  :return: None
  """
  d = 6 # random.randint(2, 10)
  x = random.randint(2, d)
  y = random.randint(1, 15)
  n = 15
  hand = [random.randint(1, d) for die in range(5)]
  compute_optimal_next_move(x, y, n, d, hand)

print("\n\n")
# print(predict_probability(4, 7, 15, 6, [3, 4, 5, 2, 1]))
# print(simulate_probability(4, 7, 15, 6, [3, 4, 5, 2, 1], 100000))
# compare_prediction_vs_simulation(4, 7, 15, 6, [3, 4, 5, 2, 1], 10000)
# random_comparison(100, 1000)
compute_optimal_next_move(4, 7, 15, 6, [3, 4, 5, 2, 1])
# test_random_optimal_next_move()
