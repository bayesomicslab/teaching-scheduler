from ortools.sat.python import cp_model
import pandas as pd
import datetime
import time

NUM_COLS_IN_STUDENTADMIN_TABLE=7

class Scheduler(object):
    def __init__(self, class_times, lab_minmax):
        self.class_times = class_times
        self.lab_minmax = lab_minmax

    def run(self):
        # first 7 fields: Day	Lab	Start	End	Campus	Room	Description
        # then a list of students
        ta_constraints = self.class_times
        num_tas = ta_constraints.shape[1] - NUM_COLS_IN_STUDENTADMIN_TABLE
        num_classes = ta_constraints.shape[0]
        all_tas_names = [x for x in ta_constraints][7:]
        all_tas = range(num_tas)
        all_classes = range(num_classes)
        class_requests = ta_constraints.fillna(0).iloc[:, 7:].transpose().astype('int32').values.tolist()

        # Creates the model.
        model = cp_model.CpModel()

        # Creates shift variables.
        # classes[(n, d, s)]: TA 'n' works class 'c' on day 'd'.
        classes = {}
        for n in all_tas:
            for c in all_classes:
                classes[(n, c)] = model.NewBoolVar('class_n%ic%i' % (n, c))

        # Each class is assigned to exactly one ta in .
        for c in all_classes:
            model.Add(sum(classes[(n, c)] for n in all_tas) == 1)

        # Each TA works at most three classes.
        for n in all_tas:
            model.Add(sum(classes[(n, c)] for c in all_classes) <= 3)

        # Try to distribute the shifts evenly, if the solution is infeasible, you might need to play with these bounds
        for n in all_tas:
            minmax = self.lab_minmax[self.lab_minmax['name'] == all_tas_names[n]]
            #print(all_tas_names[n])
            min_classes_per_ta = int(minmax['minlabs'].values[0])
            max_classes_per_ta = int(minmax['maxlabs'].values[0])

            num_classes_worked = 0
            for c in all_classes:
                num_classes_worked += classes[(n, c)]
            model.Add(min_classes_per_ta <= num_classes_worked)
            model.Add(num_classes_worked <= max_classes_per_ta)

        ta_constraints["Days & Times"]=ta_constraints["Days & Times"].replace({'Su': '0'}, regex=True)
        ta_constraints["Days & Times"]=ta_constraints["Days & Times"].replace({'Mo': '1'}, regex=True)
        ta_constraints["Days & Times"]=ta_constraints["Days & Times"].replace({'Tu': '2'}, regex=True)
        ta_constraints["Days & Times"]=ta_constraints["Days & Times"].replace({'We': '3'}, regex=True)
        ta_constraints["Days & Times"]=ta_constraints["Days & Times"].replace({'Th': '4'}, regex=True)
        ta_constraints["Days & Times"]=ta_constraints["Days & Times"].replace({'Fr': '5'}, regex=True)
        ta_constraints["Days & Times"]=ta_constraints["Days & Times"].replace({'Sa': '6'}, regex=True)

        for c in all_classes:
            for c2 in range(c + 1, len(all_classes)):
                times = ta_constraints.iloc[c]["Days & Times"].split(" - ")
                start = time.strptime(times[0], '%w %I:%M%p')
                times2 = ta_constraints.iloc[c2]["Days & Times"].split(" - ")
                start2 = time.strptime(times2[0], '%w %I:%M%p')
                if start.tm_wday==start2.tm_wday:
                    end = time.strptime(times[1], '%I:%M%p')
                    end2 = time.strptime(times2[1], '%I:%M%p')
                    dstart = int(start.tm_hour) * 3600 + int(start.tm_min)
                    dstart2 = int(start2.tm_hour) * 3600 + int(start2.tm_min)
                    dend = int(end.tm_hour) * 3600 + int(end.tm_min)
                    dend2 = int(end2.tm_hour) * 3600 + int(end2.tm_min)
                    if (start >= start2 and start <= end2) or (start2 >= start and start2 <= end):
                        for n in all_tas:
                            model.Add(classes[(n, c)] + classes[(n, c2)] <= 1)

        # pylint: disable=g-complex-comprehension
        model.Maximize(
            sum(class_requests[n][c] * classes[(n, c)] for n in all_tas
                for c in all_classes))
        # Creates the solver and solve.
        solver = cp_model.CpSolver()
        solver.Solve(model)

        if solver.StatusName()!='INFEASIBLE':
            for n in all_tas:
                for c in all_classes:
                    if solver.Value(classes[(n, c)]) == 1:
                        if class_requests[n][c] == 1:
                            print(all_tas_names[n], 'teaches class', ta_constraints.iloc[c]["Class"],ta_constraints.iloc[c]["Days & Times"], '(requested).')
                        else:
                            print(all_tas_names[n], 'teaches class', ta_constraints.iloc[c]["Class"],ta_constraints.iloc[c]["Days & Times"], '(not requested).')

            # Statistics.
            print()
            print('Statistics')
            print('  - Number of class requests met = %i' % solver.ObjectiveValue(),
                  '(out of', num_classes, ')')
        else:
            print("INFEASIBLE -- try adjusting availability of instructors or the minimum and maximum bounds for each instructor.")
        print('  - wall time       : %f s' % solver.WallTime())
