import json
from pathlib import Path
import bcrypt
import getpass
from typing import Dict, Any, Optional
from datetime import date, datetime
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class User:
    users_database = Path("users.json")
    scedule_database = Path("scedule.json")
    question_database = Path("questions.json")
    result_database = Path("result.json")
    exam_taken_database = Path("exam_taken.json")

    def __init__(self):
        self.today = date.today()
        self.formatted_date = self.today.strftime("%Y/%m/%d")
        self.users_data = []
        self.scedule_data = []
        self.question_data = []
        self.result_data = []
        self.exam_taken = []

        try:
            if (self.users_database.exists() and self.scedule_database.exists() and
                self.question_database.exists() and self.result_database.exists() and
                self.exam_taken_database.exists()):
                
                with open(self.users_database, "r") as f:
                    self.users_data = json.load(f)
                with open(self.scedule_database, "r") as f:
                    self.scedule_data = json.load(f)
                with open(self.question_database, "r") as f:
                    self.question_data = json.load(f)
                with open(self.result_database, "r") as f:
                    self.result_data = json.load(f)
                with open(self.exam_taken_database, "r") as f:
                    self.exam_taken = json.load(f)
            else:
                raise FileNotFoundError("One or more database files are missing.")
        except Exception as e:
            print(e)

    def check_credentials(self) -> Optional[Dict[str, Any]]:
        try:
            found = False
            user_name = getpass.getpass("Username-: ").strip()
            password = getpass.getpass("Enter your password: ").strip()
            password_bytes = password.encode('utf-8')
            user_bytes = user_name.encode('utf-8')
            for i in self.users_data:
                stored_hashed_bytes_pass = i["password"].encode('utf-8')
                stored_hashed_bytes_username = i["username"].encode('utf-8')
                if bcrypt.checkpw(user_bytes, stored_hashed_bytes_username) and bcrypt.checkpw(password_bytes, stored_hashed_bytes_pass):
                    found = True
                    return i, user_name

            if not found:
                print("❌ Incorrect password.\n")
                return None
        except Exception as e:
            print(e)

    @staticmethod
    def save(path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    def check_exam_id(self, *args) -> Optional[int]:
        try:
            for idx, exam in enumerate(self.question_data):
                if exam["exam_id"].capitalize() == args[0].capitalize():
                    print(len(args))
                    print("args",exam["exam_id"].capitalize())
                    if len(args) == 1:
                        return idx
                    elif len(args) >= 4:
                        question_index = args[1]
                        expected_question = args[3]
                        if exam["questions"][question_index]["question_id"].capitalize() == expected_question.capitalize():
                            return idx
                    else:
                        print("Please enter correct value")
            return None
        except (IndexError, KeyError, AttributeError) as e:
            print(f"Error: {e}\n")

    def top_scorer(self) -> None:
        exam_id = input("Enter Exam ID-: ")
        toppers = []
        highest_percentage = -1

        if not self.result_data:
            print("No data here!")
            return

        for scorer in self.result_data:
            if scorer["exam_id"].capitalize() == exam_id.capitalize():
                percentage = scorer["percentage"]
                if percentage > highest_percentage:
                    highest_percentage = percentage
                    toppers = [{
                        "username": scorer["username"],
                        "percentage": percentage
                    }]
                elif percentage == highest_percentage:
                    toppers.append({
                        "username": scorer["username"],
                        "percentage": percentage
                    })

        if toppers:
            print(f" Top Scorer(s) for exam '{exam_id}':")
            for person in toppers:
                print(f"{person['username']} with {person['percentage']}%")
        else:
            print(f"No data found for exam_id '{exam_id}'")

    def make_pdf(self, username) -> None:
        exam_id = input("Enter exam_id-: ")
        c = canvas.Canvas(f"{username}_certificate.pdf", pagesize=A4)
        c.setTitle("PDF of results")
        width, height = A4
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(width / 2, height - 100, "Result of ")
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width / 2, height - 220, username)
        c.line(100, height - 110, width - 100, height - 110)
        height = height - 250

        c.drawCentredString(width / 2, height, exam_id)
        found = False
        for result in self.result_data:
            if result["exam_id"].capitalize() == exam_id.capitalize() and result["username"] == username:
                found = True
                height = height - 50
                c.drawCentredString(width / 2, height, f"Percentage: {result['percentage']}%")
        date_str = datetime.now().strftime("%B %d, %Y")
        c.setFont("Helvetica", 14)
        c.drawString(100, 100, f"Date: {date_str}")
        c.setFont("Helvetica", 16)
        c.drawRightString(width - 100, 100, "Authorized Signature")
        if not found:
            print("Your Credentials is invalid")
        else:
            c.save()
            print(f"Certificate for {username} created!")

class Admin(User):
    def __init__(self):
        super().__init__()

    def check_credentials(self) -> Optional[Dict[str, Any]]:
        return super().check_credentials()

    @staticmethod
    def time_generate() -> Optional[str]:
        start_time = input("Enter start time (e.g., 8 AM or 14:00): ")
        try:
            time_obj = datetime.strptime(start_time, "%H:%M")
            return time_obj.strftime("%I %p")
        except ValueError:
            try:
                time_obj = datetime.strptime(start_time, "%I %p")
                return time_obj.strftime("%I %p")
            except ValueError:
                print("Invalid time format. Please try again.")

    def create_scedule(self) -> None:
        try:
            new_scdule = self.scedule_data.copy()
            new_examid = int(new_scdule[-1]["exam_id"][2:]) + 1
            if new_examid >9 and new_examid<100:
                new_examid = "0"+str(new_examid)
            elif new_examid >=100:
                new_examid = new_examid
            else:
                new_examid = "00"+str(new_examid)
            title = input("Enter title of the exam-: ").capitalize()
            start_time = self.time_generate()
            if start_time is not None:
                duration_minutes = input("Enter duration in minutes-: ")
                if not duration_minutes.isdigit() or int(duration_minutes) < 30:
                    raise ValueError("Please enter duration in positive and >= 30\n")
                scedule = {
                    "exam_id": "EX" + str(new_examid),
                    "title": title,
                    "date": self.formatted_date.replace("/", "-"),
                    "start_time": start_time,
                    "duration_minutes": int(duration_minutes)
                }
                new_scdule.append(scedule)
                self.scedule_data = new_scdule
                self.save(self.scedule_database, self.scedule_data)

        except Exception as e:
            print(e)

    @staticmethod
    def question_id_generate(i) -> Optional[str]:
        if i <= 9:
            return "Q" + "00" + str(i + 1)
        else:
            return "Q" + "0" + str(i + 1)

    def create_quesiton(self) -> None:
        try:
            if len(self.question_data) == len(self.scedule_data):
                print("❌ You havent sceduleded questions?\n")
            else:
                exam_id = self.scedule_data[-1]["exam_id"]
                data = {
                    "exam_id": exam_id,
                    "questions": []
                }
                for i in range(2):
                    question_id = self.question_id_generate(i)
                    if question_id:
                        text = input(f"Question of {question_id}-: ").capitalize()
                        options = []
                        for j in range(4):
                            option = input(f"Enter {i} th option-: ").capitalize()
                            options.append(option)
                        correct_option = input("Enter correct option number (1-4): ")
                        if not correct_option.isdigit() or not (1 <= int(correct_option) <= 4):
                            raise ValueError("Please enter integer correct option and not greater than 4")
                        else:
                            correct_option = int(correct_option)
                        questions = {
                            "question_id": question_id,
                            "text": text,
                            "options": options,
                            "correct_option": correct_option
                        }
                        data["questions"].append(questions)
                self.question_data.append(data)
                self.save(self.question_database, self.question_data)
                print(f"\n✅ All questions saved for Exam ID: {exam_id}\n")

        except Exception as e:
            print(e)

    def delete_exam(self) -> None:
        exam_id = input("Enter exam id-: ").capitalize()
        index = self.check_exam_id(exam_id)
        print(index)
        if index is not None:
            self.question_data.pop(index)
            self.scedule_data.pop(index)
            self.save(self.question_database, self.question_data)
            self.save(self.scedule_database, self.scedule_data)
            print(f"\n✅ Removed exam successfully\n")
        else:
            print("Your given exam_id doesn't exists\n")

    def update_exam_questions(self) -> None:
        try:
            option = input("\nEnter 1 to edit Question, 2 to edit options, 3 to edit correct option: ")
            if not option.isdigit() or not (1 <= int(option) <= 3):
                raise ValueError("Please enter a number from 1 to 3\n")

            option = int(option)
            exam_id = input("Enter exam id (e.g EX001): ").capitalize()
            question_id = input("Enter question id (e.g., Q002): ").capitalize()
            if question_id.startswith("Q"):
                question_index = int(question_id[1:]) - 1
                index = self.check_exam_id(exam_id, question_index, None, question_id)

                if index is not None:
                    if option == 1:
                        new_question = input("Enter your new question: ")
                        self.question_data[index]["questions"][question_index]["text"] = new_question
                        self.save(self.question_database, self.question_data)
                        print("Question updated!✅\n")
                    elif option == 2:
                        options = []
                        for i in range(4):
                            MCQ = input(f"Enter option for {i + 1}-: ")
                            options.append(MCQ)
                        self.question_data[index]["questions"][question_index]["options"] = options
                        self.save(self.question_database, self.question_data)
                    elif option == 3:
                        print("Edit correct option code...")  # You can complete this part
                else:
                    print("Exam ID or Question ID not found.")
            else:
                print("Please enter Question id in correct format..")

        except Exception as e:
            print("Error:", e)

    def exam_taken(self) -> None:
        for taken in self.exam_taken:
            print(f"Username: {taken['username']}\nPercentage: {taken['percentage']}\n")

class Student(User):
    def __init__(self):
        super().__init__()

    def view_exam(self) -> None:
        for i in self.scedule_data:
            print(f"\nExam id is: {i['exam_id']}\nTitle: {i['title']}\nDate: {i['date']}\nStart Time: {i['start_time']}\nDuration: {i['duration_minutes']} minutes")
            print(' ')

    def take_exam(self, user_name):
        try:
            score = 0
            exam_id = input("Enter exam id to take exam: ")
            index = self.check_exam_id(exam_id)
            if index is None:
                print("\n Invalid Exam ID. Please try again.\n")
                return
            total_questions = len(self.question_data[index]["questions"])
            start_time = time.time()
            questions = self.question_data[index]["questions"]

            for idx, question in enumerate(questions):
                current_time = time.time()
                elapsed = current_time - start_time
                if elapsed >= (self.scedule_data[index]["duration_minutes"] * 60):
                    print("\nTime over. Exam automatically submitted.\n")
                    break

                print(f"Time completed {int(elapsed)} seconds ")
                print(f"\nQ{idx + 1}: {question['text']}")
                for opt_idx, option in enumerate(question["options"], start=1):
                    print(f"  {opt_idx}. {option}")

                while True:
                    option = input("Enter your option (1-4): ")
                    if option.isdigit():
                        option = int(option)
                        if 1 <= option <= len(question["options"]):
                            if option == question["correct_option"] + 1:
                                print("Correct!\n")
                                score += 1
                            else:
                                print(f"Incorrect! Correct answer: {question['options'][question['correct_option']]}\n")
                            break
                        else:
                            print("Option out of range. Please enter between 1 and 4.")
                    else:
                        print("Invalid input. Please enter a number.")

            print(f"\nExam finished. Your Score: {score} out of {len(questions)}\n")

            result = {
                "username": user_name,
                "exam_id": exam_id.capitalize(),
                "score": score,
                "total_questions": total_questions,
                "correct_answers": score,
                "incorrect_answers": total_questions - score,
                "percentage": int((score / total_questions) * 100)
            }
            exam_taken = {
                "username": user_name,
                "percentage": result["percentage"]
            }
            self.result_data.append(result)
            self.exam_taken.append(exam_taken)
            self.save(self.result_database, self.result_data)
            self.save(self.exam_taken_database, self.exam_taken)
            print("Save successfully!")
        except Exception as e:
            print("An error occurred:", e)

    def view_result(self, username) -> None:
        for result in self.result_data:
            if result["username"] == username:
                print(f"Exam ID: {result['exam_id']}\nScore: {result['score']}\nIncorrect: {result['incorrect_answers']}\nPercentage: {result['percentage']}\n")


# Main program flow

admin = Admin()
student = Student()


try:
    option = input("""
PRESS
1 for Admin
2 for User

""")
    data = admin.check_credentials()
    if data:
        if not option.isdigit() or int(option) not in [1, 2]:
            raise ValueError("Value must be positive integer\n")
        else:
            option = int(option)
            if option == 1:
                if data[0]["role"] == "admin":
                    option_admin = input("""
                    1 for create scedule
                    2 for delete exam
                    3 for create questions
                    4 for update exam questions
                    5 for view exam taken students
                    6 for Top scorrer

                    """)
                    if not option_admin.isdigit() or not (1 <= int(option_admin) <= 6):
                        raise ValueError("Please enter correct value from 1 to 6")
                    else:
                        option_admin = int(option_admin)
                        if option_admin == 1:
                            admin.create_scedule()
                        elif option_admin == 2:
                            admin.delete_exam()
                        elif option_admin == 3:
                            admin.create_quesiton()
                        elif option_admin == 4:
                            admin.update_exam_questions()
                        elif option_admin == 5:
                            admin.exam_taken()
                        elif option_admin == 6:
                            admin.top_scorer()
                else:
                    print("Invalid credentials for admin..")
            elif option == 2:
                if data[0]["role"] == "student":
                    student_input = input("""
    1 for view exam
    2 for take exam
    3 for view result
    4 for Top scorrer
    5 For make pdf of result percentages

    """)
                    if int(student_input) == 1:
                        student.view_exam()
                    elif int(student_input) == 2:
                        student.take_exam(data[1])
                    elif int(student_input) == 3:
                        student.view_result(data[1])
                    elif int(student_input) == 4:
                        student.top_scorer()
                    elif int(student_input) == 5:
                        student.make_pdf(data[1])

except Exception as e:
    print(e)
