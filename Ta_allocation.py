import csv
import argparse

degree_order={
    "UG-1": -1,
    "UG-2": 0,
    "UG-3":1,
    "UG-4":2,
    "M.Tech-1":3,
    "PhD-1":3,
    "M.Tech-PhD-1":3,
    "M.Tech-2":4,
    "PhD-2":5,
    "M.Tech-PhD-2":5,
    "PhD-3":5,
    "M.Tech-PhD-3":5,
    "PhD-4":5,
    "M.Tech-PhD-4":5,
    "PhD-5":5,
    "M.Tech-PhD-5":5
}

class TA():
    '''
    Class to store TA data

    Attributes:
    rollno: Roll number of the TA
    name: Name of the TA
    degree: Degree of the TA
    year: Year of the TA
    branch: Branch of the TA
    value: Value of the TA
    preferences: List of preferences of the TA
    allocated: Boolean value to check if the TA is allocated or not
    allocated_to: Course to which the TA is allocated
    '''
    def __init__(self,rollno,name,degree, year,branch,preferences) -> None:
        self.rollno = rollno
        self.name = name
        self.degree = degree
        self.year = year
        self.branch = branch
        self.value = degree_order[degree+"-"+year]
        self.preferences = preferences
        self.allocated = False
        self.allocated_to = None

    def __repr__(self) -> str:
        return f"RollNo: {self.rollno}, Name: {self.name}"
    
class course():
    '''
    Class to store course data

    Attributes:
    course_code: Course code of the course
    course_name: Name of the course
    offered_for: Degree for which the course is offered
    required_TA: Number of TA required for the course
    no_of_students: Number of students enrolled in the course
    students_per_TA: Number of students per TA
    '''
    def __init__(self,course_code,course_name,offered_for,credits,no_of_students,students_per_TA) -> None:
        self.course_code = course_code
        self.course_name = course_name
        self.offered_for = max([degree_order[i] for i in offered_for.split('|')])
        self.required_TA = 0 if no_of_students<20 else (credits*no_of_students//students_per_TA+1)
        self.no_of_students = no_of_students
    
    def __repr__(self) -> str:
        return f"Course Name: {self.course_name}"

def get_TA_data(csvfile):
    '''
    Function to read TA data from csv file

    parameters:
    csvfile: path to csv file

    Returns:
    TA_data: List of TA objects
    '''
    TA_data = []
    with open(csvfile,'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            #print(row)
            roll_no=row[1]
            name=row[2]
            degree=row[3].split('-')[0] if len(row[3].split('-'))==2 else row[3].split('-')[0]+"-"+row[3].split('-')[1]
            year=row[3].split('-')[-1]
            branch=row[4]
            preferences=[]
            counter=1
            for i in range(5,len(row),2):
                    preferences.append((counter,row[i],row[i+1]))
                    counter+=1
            TA_data.append(TA(roll_no,name,degree,year,branch,preferences))
    return TA_data

def get_course_data(csvfile):
    '''
    Function to read course data from csv file

    parameters:
    csvfile: path to csv file
    
    Returns:
    course_data: List of course objects
    '''
    course_data = []
    with open(csvfile,'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            course_code = row[1]
            course_name = row[2]
            offered_for = row[3]
            credits = int(int(row[4].split('-')[0])+int(row[4].split('-')[2])//2)
            no_of_students = int(row[5])
            course_data.append(course(course_code,course_name,offered_for,credits,no_of_students,90))
    return course_data

def check_preference(TA,course):
    '''
    Function to check if the TA has preference for the course
    
    Parameters:
    TA: TA object
    course: Course object

    Returns:
    preference: Preference of the TA for the course
    '''
    for preference in TA.preferences:
        if preference[1]==course.course_name:
            return preference[0]
    return 0

def check_grade(TA,course):
    '''
    Function to check if the TA has grade for the course

    Parameters:
    TA: TA object
    course: Course object

    Returns:
    grade: Grade of the TA for the course
    '''
    for preference in TA.preferences:
        if preference[1]==course.course_name:
            return preference[2]
    return 0

def complete_assignment(assignment,csp):
    '''
    Function to check if the assignment is complete
    
    Parameters:
    assignment: Dictionary of course and TA assigned to it
    csp: Dictionary of course and list of TA objects

    Returns:
    True if the assignment is complete else False
    '''
    for course in csp.keys():
        if course.required_TA>0:
            if course not in assignment.keys():
                return False
            if len(assignment[course])!=course.required_TA:
                return False
    return True

def select_unassigned_variable(csp,assignment):
    '''
    Function to select the next unassigned variable

    Parameters:
    csp: Dictionary of course and list of TA objects
    assignment: Dictionary of course and TA assigned to it

    Returns:
    Variable with minimum remaining values and degree
    '''
    courses=[]
    for course in csp.keys():
        if course in assignment.keys() and course.required_TA>len(assignment[course]):
           courses.append(course) 
        if course not in assignment.keys() and course.required_TA>0:
            courses.append(course)
    courses = sorted(courses, key=lambda x: (len(csp[x]),x.required_TA))
    #print(len(courses))
    return courses[0]

def order_domain_values(var,csp):
    '''
    Function to order the domain values

    Parameters:
    var: Variable
    csp: Dictionary of course and list of TA objects

    Returns:
    List of TA objects
    '''
    return csp[var]

def is_consistent(var,value,assignment):
    '''
    Function to check if the assignment is consistent

    Parameters:
    var: Variable
    value: TA object
    assignment: Dictionary of course and TA assigned to it

    Returns:
    True if the assignment is consistent else False
    '''
    if value.allocated==True:
        #print("allocated")
        return False
    for course in assignment.keys():
        counter_mp=0
        counter_ug=0
        for i in assignment[course]:
            if i.degree=="PhD" or i.degree=="M.Tech-PhD":
                counter_mp+=1
            if i.degree=="UG":
                counter_ug+=1
        if len(assignment[course])!=0 and course.required_TA-len(assignment[course])<course.no_of_students//100-counter_mp:
            #print(course.no_of_students//100,counter_mp,course)
            #print("mp")
            return False
        if counter_ug>0.6*course.required_TA:
            #print("ug")
            return False
    if var.offered_for>=value.value:
        #print("offered")
        return False
    return True

def recursive_backtracking(assignment,csp,counter):
    '''
    Function to recursively call backtracking

    Parameters:
    assignment: Dictionary of course and TA assigned to it
    csp: Dictionary of course and list of TA objects
    counter: Counter to check the number of calls
    
    Returns:
    assignment: Dictionary of course and TA assigned to it
    csp: Dictionary of course and list of TA objects
    '''
    counter+=1
    #print("counter: ",counter)
    if complete_assignment(assignment,csp):
        return assignment,csp
    #print(sum(1 for i in assignment.keys() if len(assignment[i])>0), assignment.keys(), sum(1 for i in assignment.keys() if len(assignment[i])==i.required_TA), sum(len(assignment[i]) for i in assignment.keys()))  
    var = select_unassigned_variable(csp,assignment)
    if var not in assignment:
        assignment[var]=[]
    for value in order_domain_values(var,csp):
        if is_consistent(var,value,assignment):
            assignment[var].append(value)
            value.allocated=True
            value.allocated_to=var
            #print(assignment)
            result = recursive_backtracking(assignment,csp,counter)
            if result!=None:
                return result
            assignment[var].remove(value)
            value.allocated=False
            value.allocated_to=None
    #print("backtrack")
    return None

def backtracking_search(csp):
    '''
    Function to call recursive backtracking

    Parameters:
    csp: Dictionary of course and list of TA objects

    Returns:
    assignment: Dictionary of course and TA assigned to it
    csp: Dictionary of course and list of TA objects
    '''
    counter=0
    return recursive_backtracking({},csp,counter)



def main(ta_csv,course_csv):
    TA_data = get_TA_data(ta_csv)
    course_data = get_course_data(course_csv)
    csp={}
    for course in course_data:
        Ta_preference = {}
        for TA in TA_data:
            if TA.allocated==False:
                preference = check_preference(TA,course)
                grade=check_grade(TA,course)
                if preference!=0 and (grade=="A"or grade=="A-"):
                    Ta_preference[TA]=5-preference
        Ta_preference = sorted(Ta_preference.items(), key=lambda x: (x[1],x[0].value), reverse=True)
        csp[course]=[Ta_preference[i][0] for i in range(len(Ta_preference))] 
    mydict,csp_ass=backtracking_search(csp)
    unass_tas=[]
    for i in csp.keys():
        for ta in csp_ass[i]:
            if ta.allocated==False and ta not in unass_tas:
                unass_tas.append(ta)
        if i not in mydict.keys():
            mydict[i]=["NO TA REQUIRED"]
    with open('assinged_TAs.csv','w',newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        counter=1
        ta_no=0
        for key, value in mydict.items():
            list=[counter,key.course_code,key.course_name]
            list.extend([i for i in value])
            ta_no+=(len(list)-3)
            csvwriter.writerow(list)
            counter+=1
        #print(ta_no)
    with open('unassigned_TAs.csv','w',newline='') as csvfile:
        csvwriter=csv.writer(csvfile)
        csvwriter.writerow(['S. No.','Roll No.',"Name",'Program','Branch','Preference-1','Grade-1','Preference-2','Grade-2','Preference-3','Grade-3','Preference-4','Grade-4','Preference-5','Grade-5'])
        counter=1
        for i in unass_tas:
            pref=[]
            for j in i.preferences:
                pref.append(j[1])
                pref.append(j[2])
                list=[counter,i.rollno,i.name,i.degree+"-"+i.year,i.branch]
                list.extend(pref)
            csvwriter.writerow(list)
            counter+=1

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--TA_csv',help='Path to TA csv file')
    parser.add_argument('--course_csv',help='Path to course csv file')
    args=parser.parse_args()
    main(args.TA_csv,args.course_csv)
                
        