import random
import copy
from itertools import product
from functools import partial
from operator import attrgetter
from collections import namedtuple
from math import exp

Activity = namedtuple("Activity", ["id", "expected_enrollment", "preferred_facilitators", "other_facilitators"])
Room = namedtuple("Room", ["id", "capacity"])
Assignment = namedtuple("Assignment", ["activity", "room", "time", "facilitator"])
# Define the problem data (activities, rooms, facilitators, etc.)
activities = {
    "SLA100A": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA100B": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA191A": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA191B": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA201":  {"enrollment": 50, "preferred_facilitators": ["Glen", "Banks", "Zeldin", "Shaw"], "other_facilitators": ["Numen", "Richards", "Singer"]},
    "SLA291":  {"enrollment": 50, "preferred_facilitators": ["Lock", "Banks", "Zeldin", "Singer"], "other_facilitators": ["Numen", "Richards", "Shaw", "Tyler"]},
    "SLA303":  {"enrollment": 60, "preferred_facilitators": ["Glen", "Zeldin", "Banks"], "other_facilitators": ["Numen", "Singer", "Shaw"]},
    "SLA304":  {"enrollment": 25, "preferred_facilitators": ["Glen", "Banks", "Tyler"], "other_facilitators": ["Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin"]},
    "SLA394":  {"enrollment": 20, "preferred_facilitators": ["Tyler", "Singer"], "other_facilitators": ["Richards", "Zeldin"]},
    "SLA449":  {"enrollment": 60, "preferred_facilitators": ["Tyler", "Singer", "Shaw"], "other_facilitators": ["Zeldin", "Uther"]},
    "SLA451":  {"enrollment": 100, "preferred_facilitators": ["Tyler", "Singer", "Shaw"], "other_facilitators": ["Zeldin", "Uther", "Richards", "Banks"]},
}
rooms = {
    "Slater 003": 45,
    "Roman 216": 30,
    "Loft 206": 75,
    "Roman 201": 50,
    "Loft 310": 108,
    "Beach 201": 60,
    "Beach 301": 75,
    "Logos 325": 450,
    "Frank 119": 60,
}
facilitators = ["Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"]

times = ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM"]

# Define the initial population of schedules (random assignments)
def generate_random_schedule():
    schedule = {}
    for activity in activities:
        room = random.choice(list(rooms.keys()))
        time = random.choice(times)
        facilitator = random.choice(facilitators)
        schedule[activity] = {"room": room, "time": time, "facilitator": facilitator}
    return schedule

# define entire population of schedules
def generate_all_schedules():
  schedules = []
  for _ in range(500):
      schedules.append(generate_random_schedule())

  return schedules

# Generate the schedule
all_random_schedule = generate_all_schedules()

# calculating the fitness score of a single schedule
def fitness(schedule):
  schedule_score = 0
  # for loop adds the score of each activity to the schedule_score
  for activity_name in activities:
    schedule_score = schedule_score + overlap(schedule, activity_name)
    schedule_score = schedule_score + faciliator_load(schedule, schedule[activity_name]["facilitator"])
    schedule_score = schedule_score + room_size(schedule)
    schedule_score = schedule_score + preferred_facilitator(schedule)
    schedule_score = schedule_score + other_facilitator(schedule)
    schedule_score = schedule_score + rando_facilitator(schedule)

  activity_adjustment = activity_adjustments(schedule)
  schedule_score = schedule_score + activity_adjustment
  # print({"Activity Adjustment" + activity_adjustment})
  return schedule_score

def all_fitness_scores(all_schedules):
  all_scores = []
  i = 0
  for _ in range(500):
      all_scores.append(fitness(all_schedules[i]))
      i = i + 1
  return all_scores
  
# fitness calculator helpers
def overlap(schedule, activity_name):
  score_contribution = 0
  room = schedule[activity_name]["room"]
  time = schedule[activity_name]["time"]

  for activity in schedule:
    # if same time && same room as other activites -.5
    if schedule[activity]["room"] == room and schedule[activity]["time"] == time and activity != activity_name:
      score_contribution = score_contribution - 0.5

  return score_contribution
# room size requirement
def room_size(schedule):
  current_room_size = 0
  activity_enrollment = 0
  score_contribution = 0
  for activity in schedule:
    current_room_size = rooms.get(schedule[activity]["room"]) #grabs room size
    activity_enrollment = activities[activity]["enrollment"] #grabs people enrolled
    if current_room_size < activity_enrollment:
      score_contribution = score_contribution - 0.5
    elif current_room_size > (6 * activity_enrollment):
      score_contribution = score_contribution - 0.4
    elif current_room_size > (3 * activity_enrollment):
      score_contribution = score_contribution - 0.2
    else:
      score_contribution = score_contribution + 0.3
  return score_contribution

def preferred_facilitator(schedule):  
  score_contribution = 0
  for activity in schedule:
    if schedule[activity]["facilitator"] == activities[activity]["preferred_facilitators"]: # compares an activities facilitator and sees if the activities preferred facilitator is the same
      score_contribution = score_contribution + 0.5
  return score_contribution

def other_facilitator(schedule):
  score_contribution = 0
  for activity in schedule:
    if schedule[activity]["facilitator"] == activities[activity]["other_facilitators"]: # compares an activities facilitator and sees if the activities other facilitator is the same
      score_contribution = score_contribution + 0.2
  return score_contribution

def rando_facilitator(schedule):
  score_contribution = 0
  for activity in schedule:
    if schedule[activity]["facilitator"] != activities[activity]["other_facilitators"] and schedule[activity]["facilitator"] != activities[activity]["preferred_facilitators"]: # checks if facilitator is not a preferred or other facilitator
      score_contribution = score_contribution - 0.1
  return score_contribution

def faciliator_load(schedule, facilitator):
  score_contribution = 0
  time_slots = []
  time_and_locations = []
  total_appts = 0 #this will be used to check if scheduled more than 4
  is_double_booked = False
  indexes = []
  
  for activity in schedule:
    if schedule[activity]["facilitator"] == facilitator:
      time_slots.append(schedule[activity]["time"])
      time_and_locations.append(schedule[activity]["room"])
      total_appts += 1
  
  for time in time_slots:
    if time_slots.count(time) > 1:
      if(not is_double_booked):
        score_contribution = score_contribution - 0.2
      is_double_booked = True
    else:
      score_contribution = score_contribution + 0.2

  if total_appts > 4:
    score_contribution = score_contribution - 0.5
  elif total_appts < 3:
    score_contribution = score_contribution - 0.4

  for time in time_slots:
    if time in times:
      indexes.append(times.index(time))

  roomIndex = 0
  roomIndex2 = 0
  
  for index in indexes:
    for index2 in indexes:
      if index2 - index == 1 or index2 - index == -1:
        roomIndex = index
        roomIndex2 = index2
        score_contribution = score_contribution + 0.5
        break
  if roomIndex < len(time_and_locations) and roomIndex2 < len(time_and_locations):
    if time_and_locations[roomIndex] != time_and_locations[roomIndex2]:
      score_contribution = score_contribution - 0.4
    
  return score_contribution

#Activity specific adjustments
def activity_adjustments(schedule):
  ###############  REQUIRED DATA FOR ACTIVITY ADJUSTMENTS ################
  activity_adjustment_score = 0
  testing = 0
  # Sets up SLA 100 sesssions' data
  SLA100_times = [] #HOLDER OF SLA10O SESSIONS' DATA
  SLA100_time_slot_indexes = [] #HOLDER OF INDEX MAPPING
  SLA100_activity_locations = []
  for activity in schedule:
    if activity == "SLA100A" or activity == "SLA100B":
      SLA100_times.append({activity: schedule[activity]["time"]})
      SLA100_activity_locations.append(schedule[activity]["room"])
  SLA100_time_slot_indexes.append(times.index(SLA100_times[0]["SLA100A"]))
  SLA100_time_slot_indexes.append(times.index(SLA100_times[1]["SLA100B"]))
  # Sets up SLA 191 sesssions' data
  SLA191_times = [] #HOLDER OF SLA10O SESSIONS' DATA
  SLA191_time_slot_indexes = [] #HOLDER OF INDEX MAPPING
  SLA191_activity_locations = []
  for activity in schedule:
    if activity == "SLA191A" or activity == "SLA191B":
      SLA191_times.append({activity: schedule[activity]["time"]})
      SLA191_activity_locations.append(schedule[activity]["room"])
  SLA191_time_slot_indexes.append(times.index(SLA191_times[0]["SLA191A"]))
  SLA191_time_slot_indexes.append(times.index(SLA191_times[1]["SLA191B"]))

  ################## ACTIVITY ADJUSTMENTS ##########################
  # covers first 2 bullet points
  if abs(SLA100_time_slot_indexes[1] - SLA100_time_slot_indexes[0]) > 3:
    activity_adjustment_score = activity_adjustment_score + 0.4
  elif SLA100_time_slot_indexes[1] - SLA100_time_slot_indexes[0] == 0:
    activity_adjustment_score = activity_adjustment_score - 0.5

  # covers 3rd and 4th bullet point
  if abs(SLA191_time_slot_indexes[1] - SLA191_time_slot_indexes[0]) > 3:
    activity_adjustment_score = activity_adjustment_score + 0.4
  elif SLA191_time_slot_indexes[1] - SLA191_time_slot_indexes[0] == 0:
    activity_adjustment_score = activity_adjustment_score - 0.5

  # 5th bullet point
  for index in SLA191_time_slot_indexes:
    if index > 1:
      break
    if abs(index - SLA100_time_slot_indexes[0]) == 1:
      activity_adjustment_score = activity_adjustment_score + 0.5
      if(SLA100_activity_locations[0] != SLA191_activity_locations[index]):
        activity_adjustment_score = activity_adjustment_score - 0.4
      break
    if abs(index - SLA100_time_slot_indexes[1]) == 1:
      activity_adjustment_score = activity_adjustment_score + 0.5
      if(SLA100_activity_locations[1] != SLA191_activity_locations[index]):
        activity_adjustment_score = activity_adjustment_score - 0.4
      break

  # 6th bullet point
  for index in SLA191_time_slot_indexes:
    if index > 1:
      break
    if abs(index - SLA100_time_slot_indexes[0]) == 2:
      activity_adjustment_score = activity_adjustment_score + 0.25
      break
    if abs(index - SLA100_time_slot_indexes[1]) == 2:
      activity_adjustment_score = activity_adjustment_score + 0.25
      break

  # 7th bullet point
  for index in SLA100_time_slot_indexes:
    if index > 1:
      break
    if SLA100_time_slot_indexes[index] == SLA191_time_slot_indexes[0]:
      activity_adjustment_score = activity_adjustment_score - 0.25
      break
    if SLA100_time_slot_indexes[index] == SLA191_time_slot_indexes[1]:
      activity_adjustment_score = activity_adjustment_score - 0.25
      break 
      
  return activity_adjustment_score

def select_parents(all_fitness_scores, all_random_schedules):
  if len(all_fitness_scores) < 2:
      raise ValueError("The list should contain at least two scores")

  # Initialize variables to keep track of the top two scores and their indexes
  top_scores = [float('-inf'), float('-inf')]
  top_indexes = [-1, -1]

  for i, all_fitness_scores in enumerate(all_fitness_scores):
      if all_fitness_scores > top_scores[0]:
          top_scores[1] = top_scores[0]
          top_indexes[1] = top_indexes[0]
          top_scores[0] = all_fitness_scores
          top_indexes[0] = i
      elif all_fitness_scores > top_scores[1]:
          top_scores[1] = all_fitness_scores
          top_indexes[1] = i
        
  # Select the parents by selecting the two schedules with the highest fitness scores
  top_index1, top_index2 = top_indexes
  parent1 = all_random_schedules[top_index1]
  parent2 = all_random_schedules[top_index2]
  
  return parent1, parent2

def crossover(parent1, parent2):
  # Check if parent1 and parent2 are lists
  if not isinstance(parent1, dict) or not isinstance(parent2, dict):
      raise ValueError("Parent1 and parent2 must be dictionaries")
  
  # Perform crossover
  crossover_point = len(parent1) // 2
  keys = list(parent1.keys())

  offspring1 = {}
  offspring2 = {}

  for i, key in enumerate(keys):
      if i < crossover_point:
          offspring1[key] = parent1[key]
          offspring2[key] = parent2[key]
      else:
          offspring1[key] = parent2[key]
          offspring2[key] = parent1[key]
  return offspring1, offspring2


def mutate(schedule):
  mutation_rate = 0.1
  mutated_schedule = copy.deepcopy(schedule)

  for activity_name in mutated_schedule:
    if random.random() < mutation_rate:
        # Mutate the room
      mutated_schedule[activity_name]["room"] = random.choice(list(rooms.keys()))

    if random.random() < mutation_rate:
        # Mutate the time
      mutated_schedule[activity_name]["time"] = random.choice(times)

    if random.random() < mutation_rate:
        # Mutate the facilitator
      mutated_schedule[activity_name]["facilitator"] = random.choice(facilitators)

  return mutated_schedule
population_size = 500
generations = 100
def genetic_algorithm(population_size, generations):
     # Initialize a random population of schedules
     population = [generate_random_schedule() for _ in range(population_size)]

     for generation in range(generations):
         # Calculate fitness for each schedule in the population
         fitness_scores = [fitness(schedule) for schedule in population]

         # Select parents for crossover
         parents = select_parents(fitness_scores, population)

         # Create a new population of offspring schedules
         new_population = []

         for _ in range(population_size // 2):
             parent1, parent2 = parents[0], parents[1]
             offspring1, offspring2 = crossover(parent1, parent2)
             mutate(offspring1)
             mutate(offspring2)
             new_population.extend([offspring1, offspring2])

         # Replace the old population with the new population
         population = new_population
     # Find the best schedule in the final population
     best_schedule = max(population, key=fitness)

     return best_schedule

best_schedule = genetic_algorithm(population_size=500, generations=100)
# Open a file for writing (creates the file if it doesn't exist)
with open('output.txt', 'w') as file:
  file.write("Best Schedule: " + str(best_schedule))
  file.write("Fitness Score: " + str(fitness(best_schedule)))