# instructor-scheduler
Python resource for scheduling instructor resources.

## Usage
```
usage: python Main.py [-h] -i INSTRUCTORS -c CLASSES [-f FILTER]
```

## Dependencies

pandas, numpy, OR tools

Either use the requirements.txt file
```
pip install -r requirements.txt
```
or install the packages manually. 
Install [pandas](https://pandas.pydata.org/docs/getting_started/install.html), 
[numpy](https://numpy.org/install/), and
[OR tools](https://developers.google.com/optimization/install).
E.g. installation is simply with conda: 
```
conda create -n instOpt python
source activate instOpt
conda install numpy
conda install pandas
conda install -c conda-forge ortools-python
```

## Input

###Create the INSTRUCTORS file.

Create a TSV file with 3 columns and each line being the instructors name, 
minimum classes they can cover, and maximum classes they can cover. See below for 
an example or the data/num_labs_ta_assignment.txt file.
```
#Instructor	min_sections	max_sections
Instructor Name1	1	2
Instructor Name2	1	2
Instructor Name3	1	2
Instructor Name4	1	2
Instructor Name5	1	3
```


###Create the CLASSES file.

- **Download your schedule from student admin.** Log into [student admin](https://student.studentadmin.uconn.edu/) and 
go to "My Schedule". Select the correct Term. Click the small spreadsheet icon to the right of the 
  "Personalize" and "View All" links. See the data/class_times.xls file.
- **Convert the XLS file to TSV.** E.g., open the XLS file in Excel and export to TSV (tab delimited 
  file -- use "save as" in the file menu). See the data/class_times.tsv file.
- **Add instructors and their availability in the TSV file.** Each instructor has their own column and a 1 in the row 
  if they can fill the section. I typically do this by opening the TSV in Google Sheets and asking TAs
  to fill in their availability, then convert back to TSV. You can also remove rows of classes you do not want to 
  include in the schedule or use the -f filter option, which will output a version of the TSV with suffix "_filtered.tsv". 
  See the data/class_times_withtas.tsv and data/class_times_withtas_filtered.tsv files.


###Filtering course names
If you only want to consider a single course (e.g. CSE 1010) then add a filter with -f, e.g., "-f 1010"

###Run the program
Example usage:
```
python Main.py -i data/num_labs_ta_assignment.tsv -c data/class_times_withtas.tsv -f 1010
```
or 
```
python Main.py -i data/num_labs_ta_assignment.tsv -c data/class_times_withtas_filtered.tsv
```