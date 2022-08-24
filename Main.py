import pandas as pd
import sys, os
import argparse
from Scheduler import Scheduler


class Main(object):

    @classmethod
    def main(self, cmd_args):
        '''
        The main function sets up the haplotype assembly, loads in data, and starts the algorithm.
        :param cmd_args: command line parameters
        :return: None
        '''
        self.init(cmd_args)
        (class_times, lab_minmax) = self.load_input(self.class_filename, self.instructor_filename)
        scheduler = Scheduler(class_times, lab_minmax)
        scheduler.run()

    @classmethod
    def init(self, cmd_args):
        self.class_filename = "data/class_times_withtas.tsv"
        self.instructor_filename = "data/num_labs_ta_assignment.tsv"

        parser = Main.getParser()
        args = parser.parse_args(cmd_args[1:])

        self.class_filename = args.classes
        self.instructor_filename = args.instructors
        self.filter = args.filter

    @classmethod
    def load_input(self, class_filename, instructor_filename):
        class_times = pd.read_csv(class_filename, "\t")
        class_times = class_times[class_times['Class'].notna()]
        class_times_filt = class_times
        if self.filter != None:
            class_times_filt = class_times[class_times['Class'].str.contains(self.filter)]

        class_times_filt = class_times_filt[class_times_filt["Days & Times"] != "TBA"]

        if class_times.shape[0]!=class_times_filt.shape[0]:
            print("Outputting a filtered classes TSV...")
            class_times_filt.to_csv(os.path.splitext(class_filename)[0] + '_filtered.tsv', sep="\t", index=False)

        # name, min labs, max labs
        lab_minmax = pd.read_csv(instructor_filename, sep='\t', comment='#', header=None)
        lab_minmax.columns = ['name', 'minlabs', 'maxlabs']

        return (class_times_filt, lab_minmax)

    @classmethod
    def getParser(cls):
        parser = argparse.ArgumentParser(description='Instructor scheduler using constraint programming.')

        parser.add_argument("-i", "--instructors", required=True,
                            help="Instructor file (see README) (string)",
                            default=None)
        parser.add_argument("-c", "--classes", required=True,
                            help="which assembly algorithm to run (string)",
                            default=None)
        parser.add_argument("-f", "--filter", required=False,
                            help="filter for class names (e.g. '1010' will include all cse 1010 sections ) (string)",
                            default=None)
        return parser

if __name__ == '__main__':
    Main.main(sys.argv)