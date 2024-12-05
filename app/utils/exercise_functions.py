import math

class WorkoutPlanner:
    def __init__(self):
        self.TIME_PER_REP = 1  # seconds
        self.WARM_UP_TIME = 300  # 5 minutes in seconds
        self.COOL_DOWN_TIME = 300  # 5 minutes in seconds

    def allocate_workout_time(self, total_time_minutes):
        total_time_seconds = total_time_minutes * 60
        exercise_time = total_time_seconds - self.WARM_UP_TIME - self.COOL_DOWN_TIME

        if total_time_seconds < 1800:  # Workouts shorter than 30 minutes
            compound_ratio = 0.8
        elif total_time_seconds < 3600:  # Workouts between 30 and 60 minutes
            compound_ratio = 0.7
        else:  # Workouts longer than 60 minutes
            compound_ratio = 0.65

        compound_time = math.floor(exercise_time * compound_ratio)
        isolation_time = exercise_time - compound_time

        return {
            "warm_up": self.WARM_UP_TIME,
            "compound": compound_time,
            "isolation": isolation_time,
            "cool_down": self.COOL_DOWN_TIME
        }

    def calculate_sets_reps(self, time_allocation, goal):
        goals = {
            "strength": {"rep_range": (3, 6), "rest_time": 90},
            "hypertrophy": {"rep_range": (8, 12), "rest_time": 60},
            "endurance": {"rep_range": (12, 20), "rest_time": 30}
        }

        goal_params = goals.get(goal.lower(), goals["hypertrophy"])

        def calc_for_period(period_time, is_compound):
            max_reps = goal_params["rep_range"][1]
            min_reps = goal_params["rep_range"][0]
            rest_time = goal_params["rest_time"]
            
            if is_compound:
                target_reps = min_reps
                target_sets = 4
            else:
                target_reps = max_reps
                target_sets = 3

            time_per_set = (target_reps * self.TIME_PER_REP) + rest_time
            max_sets = math.floor(period_time / time_per_set)

            if max_sets < target_sets:
                # If we can't fit the target sets, reduce reps
                while target_reps > min_reps and max_sets < target_sets:
                    target_reps -= 1
                    time_per_set = (target_reps * self.TIME_PER_REP) + rest_time
                    max_sets = math.floor(period_time / time_per_set)

            num_exercises = max(1, math.floor(max_sets / target_sets))
            sets_per_exercise = math.floor(max_sets / num_exercises)

            return {
                "exercises": num_exercises,
                "sets": sets_per_exercise,
                "reps": target_reps,
                "rest": rest_time
            }

        compound_plan = calc_for_period(time_allocation["compound"], True)
        isolation_plan = calc_for_period(time_allocation["isolation"], False)

        return {
            "compound": compound_plan,
            "isolation": isolation_plan
        }

    def plan_workout(self, total_time_minutes, goal):
        time_allocation = self.allocate_workout_time(total_time_minutes)
        workout_plan = self.calculate_sets_reps(time_allocation, goal)

        # Calculate actual time used
        compound_time_used = workout_plan["compound"]["exercises"] * workout_plan["compound"]["sets"] * \
                             ((workout_plan["compound"]["reps"] * self.TIME_PER_REP) + workout_plan["compound"]["rest"])
        isolation_time_used = workout_plan["isolation"]["exercises"] * workout_plan["isolation"]["sets"] * \
                              ((workout_plan["isolation"]["reps"] * self.TIME_PER_REP) + workout_plan["isolation"]["rest"])

        return {
            "time_allocation": time_allocation,
            "workout_plan": workout_plan,
            "compound_time_used": compound_time_used,
            "isolation_time_used": isolation_time_used,
            "total_time_used": self.WARM_UP_TIME + compound_time_used + isolation_time_used + self.COOL_DOWN_TIME
        }


