from PIL import Image
import pytesseract
from datetime import datetime, timedelta
import argparse
import os.path
import os

from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
credentials = os.getenv("CREDENTIALS")

HEADERS = 4
SCOPES = ["https://www.googleapis.com/auth/calendar"]

class Course:
    def __init__(
            self,
            code=None,
            name=None,
            credit=None,
            section=None,
            midterm_start_time=None,
            midterm_end_time=None,
            final_start_time=None,
            final_end_time=None):
        self.code = code
        self.name = name
        self.credit = credit
        self.section = section
        self.midterm_start_time = midterm_start_time
        self.midterm_end_time = midterm_end_time
        self.final_start_time = final_start_time,
        self.final_end_time = final_end_time

# Format to standard to ISO
def format_exam_dates(dates, time):
    start_time = None
    end_time = None
    start_dates = []
    end_dates = []

    for i, j in zip(dates, time):
        if j != "-":
            start_time = i + " " + j.split(" - ")[0]
            end_time = i + " " + j.split(" - ")[1]

            start_dt = datetime.strptime(start_time, "%d %b %Y %I:%M %p")
            end_dt = datetime.strptime(end_time, "%d %b %Y %I:%M %p")

            offset = timedelta(hours=7)

            start_offset = start_dt + offset
            end_offset = end_dt + offset

            start_iso = start_offset.strftime("%Y-%m-%dT%H:%M:%S+07:00")
            end_iso = end_offset.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        else:
            start_iso = None
            end_iso = None

        start_dates.append(start_iso)
        end_dates.append(end_iso)

    return start_dates, end_dates

# Add events to calendar
def add_to_calendar(course, start_time, end_time):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials, SCOPES
            )
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": f"{course.name} Exam",
            "colorId": 6,
            "start": {
                "dateTime": start_time,
                "timeZone": "Asia/Bangkok"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Asia/Bangkok"
            }
        }

        event = service.events().insert(calendarId="primary", body=event).execute()

        print("Event created: ", event.get("htmlLink"))

    except HttpError as error:
        print(f"An error occurred: {error}")


def main():

    # Get user arguments
    parser = argparse.ArgumentParser(description="Process exam schedule image path.")
    parser.add_argument("--img", type=str, help="Exam schedule image path", required=True)
    parser.add_argument("--course", type=int, help="Number of courses", required=True)
    args = parser.parse_args()

    # Load the image
    img = Image.open(args.img)

    # Process with Tesseract
    text = pytesseract.image_to_string(img)

    calendar_dict = {
        "Course Code": [],
        "Course Name": [],
        "Credit": [],
        "Section": [],
        "Midterm": {
            "Date": [],
            "Time": [],
        },
        "Final": {
            "Date": [],
            "Time": [],
        }
    }

    data = [word for word in text.split('\n') if word != '']

    course_no = args.course

    # Generate courses
    courses = []
    for i in range(course_no):
        course = Course()
        courses.append(course)

    keys = list(calendar_dict.keys())

    # Add course data to calendar dict
    for i in range(0, len(data), course_no):
        if i < course_no*HEADERS:
            calendar_dict[keys[int(i/course_no)]] = data[i:i+course_no]

    # Populate courses
    for i in range(0, course_no):
        courses[i].code = calendar_dict["Course Code"][i]
        courses[i].name = calendar_dict["Course Name"][i]
        courses[i].credit = calendar_dict["Credit"][i]
        courses[i].section = calendar_dict["Section"][i]

    count = 0

    # Add exam dates to calendar dict
    for i in range(course_no*HEADERS, len(data), HEADERS):
        for j in data[i:i+HEADERS-2]:
            if count < course_no:
                calendar_dict["Midterm"][j.split(" : ")[0]].append(j.split(" : ")[1])
            else:
                calendar_dict["Final"][j.split(" : ")[0]].append(j.split(" : ")[1])
        count += 1

    # Format midterm exam dates
    start_dates, end_dates = format_exam_dates(
        calendar_dict["Midterm"]["Date"], calendar_dict["Midterm"]["Time"])

    for index, (start, end) in enumerate(zip(start_dates, end_dates)):
        courses[index].midterm_start_time = start
        courses[index].midterm_end_time = end

    # Format finals exam dates
    start_dates, end_dates = format_exam_dates(
        calendar_dict["Final"]["Date"], calendar_dict["Final"]["Time"])

    for index, (start, end) in enumerate(zip(start_dates, end_dates)):
        courses[index].final_start_time = start
        courses[index].final_end_time = end

    # Add events to calendar
    for course in courses:
        if course.midterm_start_time != None:
            add_to_calendar(course, course.midterm_start_time, course.midterm_end_time)
        if course.final_start_time != None:
            add_to_calendar(course, course.final_start_time, course.final_end_time)


if __name__ == "__main__":
    main()
