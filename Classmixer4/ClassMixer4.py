import os
import math
import random
from queue import PriorityQueue

class Student:
    def __init__(self, id, gender, language, sva, svast, supported, flagged, preferred):
        self.id = id
        self.gender = gender
        self.language = language
        self.sva = sva
        self.svast = svast
        self.supported = supported
        self.flagged = flagged
        self.preferred = preferred  # This is a list of student IDs

class Class:
    def __init__(self, name, max_sva, max_svast, max_spanska, max_franska, max_tyska):
        self.name = name
        self.max_sva = max_sva
        self.max_svast = max_svast
        self.max_spanska = max_spanska
        self.max_franska = max_franska
        self.max_tyska = max_tyska
        self.students = []

    def can_add(self, student):
        if len(self.students) >= 32:
            return False
        if bool(student.sva) and sum(bool(s.sva) for s in self.students) >= self.max_sva:
            return False
        if bool(student.svast) and sum(bool(s.svast) for s in self.students) >= self.max_svast:
            return False
        if student.language == 'Spanska' and sum(s.language == 'Spanska' for s in self.students) >= self.max_spanska:
            return False
        if student.language == 'Franska' and sum(s.language == 'Franska' for s in self.students) >= self.max_franska:
            return False
        if student.language == 'Tyska' and sum(s.language == 'Tyska' for s in self.students) >= self.max_tyska:
            return False
        return True

    def add(self, student):
        self.students.append(student)

def get_students():
    students = []
    print("Enter the details for each student as a comma-separated list (id, gender, language, sva, svast, supported, flagged, preferred), or 'q' to quit:")
    while True:
        line = input()
        if line.lower() == 'q':
            break
        parts = line.split(',', 7)  # Split the line into 8 parts
        if len(parts) != 8:
            print("Invalid input. Please enter exactly 8 fields.")
            continue
        id, gender, language, sva, svast, supported, flagged, preferred = parts
        try:
            id = int(id)
            sva = int(sva)
            svast = int(svast)
            supported = int(supported)
            flagged = int(flagged)
            preferred = [int(i.strip(' []')) for i in preferred.split(',') if i.strip(' []')]
        except ValueError:
            print("Invalid input. sva, svast, supported, and flagged should be integers (1 or 0).")
            continue
        students.append(Student(id, gender, language, sva, svast, supported, flagged, preferred))
    return students

def assign_students(students, classes):
    unassigned_students = students.copy()  # Start with all students unassigned
    def assign_student(course, student, unassigned_students, newly_assigned_students):
        course.add(student)
        newly_assigned_students.append(student)
        unassigned_students.remove(student)

    while unassigned_students:  # Continue until all students are assigned
        newly_assigned_students = []  # Keep track of students assigned in each round

        # First, try to assign students based on language quotas
        for language in ['Spanska', 'Franska', 'Tyska']:
            for student in [s for s in unassigned_students if s.language == language]:
                for c in classes:
                    if c.can_add(student):
                        assign_student(c, student, unassigned_students, newly_assigned_students)
                        break

        # Then, try to assign students to the same class as their preferred peers
        for student in unassigned_students.copy():
            student_is_assigned = False
            for preferred_id in student.preferred:
                if student_is_assigned:
                    break
                preferred_peer = next((s for s in students if s.id == preferred_id), None)
                if preferred_peer:
                    for c in classes:
                        if preferred_peer in c.students and c.can_add(student):
                            assign_student(c, student, unassigned_students, newly_assigned_students)
                            student_is_assigned = True
                            break

        # Finally, assign the remaining students randomly
        random.shuffle(unassigned_students)
        for student in unassigned_students.copy():
            for c in classes:
                if c.can_add(student):
                    assign_student(c, student, unassigned_students, newly_assigned_students)
                    break

        # If no new students were assigned in this round, break the loop
        if not newly_assigned_students:
            break

    # Return the list of students who could not be assigned
    return unassigned_students

def check_classes(classes):
    for c in classes:
        # Check if the students list in the class is populated
        if not c.students:
            print(f"Class {c.name} is empty.")
            continue

        # If the class is not empty, proceed with the existing code
        spanska = sum(s.language == 'Spanska' for s in c.students)
        franska = sum(s.language == 'Franska' for s in c.students)
        tyska = sum(s.language == 'Tyska' for s in c.students)
        print(f'Class {c.name}: Spanska={spanska}, Franska={franska}, Tyska={tyska}')

def balance_students(students, classes):
    # Calculate the average number of students per class
    avg_students = math.ceil(len(students) / len(classes))

    changes_made = True
    while changes_made:  # Continue until no more changes can be made
        changes_made = False  # Reset the flag

        # Find the largest and smallest classes
        largest_class = max(classes, key=lambda c: len(c.students))
        smallest_class = min(classes, key=lambda c: len(c.students))

        # If the largest class is over the average, try to move a student to the smallest class
        if len(largest_class.students) > avg_students:
            for student in largest_class.students:
                if smallest_class.can_add(student):
                    largest_class.students.remove(student)
                    smallest_class.add(student)
                    changes_made = True  # A change was made, so we'll need to loop again
                    break  # Exit the loop early since we made a change

def evenly(students, classes):
    # Calculate the ideal number of students per class
    ideal_students = round(len(students) / len(classes))

    # While any class is over the ideal size, move students from the largest class to the smallest class
    while max(len(c.students) for c in classes) > ideal_students:
        largest_class = max(classes, key=lambda c: len(c.students))
        smallest_class = min(classes, key=lambda c: len(c.students))

        # Find a student in the largest class who can be moved to the smallest class
        for student in largest_class.students.copy():  # Create a copy for iteration
            if smallest_class.can_add(student):
                largest_class.students.remove(student)
                smallest_class.students.append(student)
                break
        else:
            # If we couldn't move any students, break the loop
            break

def check_preferences(students, classes):
    for student in students:
        # Find the class that the student is in
        student_class = next((c for c in classes if student in c.students), None)

        # If the student hasn't been assigned to a class, print a message and continue with the next student
        if student_class is None:
            print(f'Student {student.id} has not been assigned to a class.')
            continue

        # Check if any of the student's preferred peers are in the same class
        preferred_peers_in_class = any(preferred_id in [s.id for s in student_class.students] for preferred_id in student.preferred)

        if not preferred_peers_in_class:
            print(f'Student {student.id} is not in a class with any of their preferred peers.')
if __name__ == '__main__':
    # Create students and classes here
    students = [
    ]
    classes = [
        Class('A', 16, 0, 32, 16, 0),
        Class('B', 16, 0, 32, 16, 0),
        Class('C', 0, 0, 32, 10, 0),
        Class('D', 16, 16, 16, 10, 16),
        Class('E', 16, 16, 16, 10, 16)
    ]

    students = get_students()
    assign_students(students, classes)
    check_classes(classes)
    balance_students(students, classes)
    evenly(students, classes)
    check_preferences(students, classes)

    # Export the classes to a .txt file
    filename = 'classes.txt'
    filepath = os.path.join(os.getcwd(), filename)
    print(f'Writing to file: {filepath}')
    with open(filepath, 'w') as f:
        for c in classes:
            f.write(f'Class {c.name}:\n')
            for s in c.students:
                f.write(f'{s.id},{s.gender},{s.language},{s.sva},{s.svast},{s.supported},{s.flagged},{s.preferred}\n')
