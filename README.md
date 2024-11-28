# CRAM MY CALENDAR
#### Video Demo: https://www.youtube.com/watch?v=8BBX_kpKjFg
#### Description:
This project simplifies the process of managing exam schedules by automating the extraction of text from an image and creating corresponding events in Google Calendar. Designed for students and educators, this script streamlines the process of organizing and tracking important academic dates.

## Features
- **OCR Integration**: Uses Tesseract OCR to read and process text from an image of the exam schedule.
- **Event Parsing**: Extracts details such as date, time, and subject from the text.
- **Google Calendar Integration**: Automatically creates events in your Google Calendar.


## How It Works

### 1. User Input
The user provides two arguments via the command line:
- `--img`: Specifies the path to the image containing the exam schedule.
- `--course`: Indicates the number of courses in the schedule.

### 2. Image Processing
The provided image is loaded and processed using Tesseract OCR to extract text. The OCR engine converts the visual content of the image into a plain text string, which can then be analyzed further.

### 3. Data Organization
The extracted text is parsed and structured into the `calendar_dict`. This dictionary categorizes data into predefined fields like course details and exam schedules. The organization ensures that all relevant details are accounted for and can be linked to individual courses.

### 4. Course Object Initialization
For each course in the schedule, a `Course` object is created. These objects store details such as:
- Course Code
- Course Name
- Credit Hours
- Section
- Midterm and Final Exam Dates and Times

Data from `calendar_dict` is mapped to these objects to ensure accurate representation of the schedule.

### 5. Date and Time Formatting
The script formats exam dates and times into ISO 8601 format, a standard used by Google Calendar. This formatting ensures compatibility and correct time-zone handling, making the events accurate and reliable.

### 6. Event Creation in Google Calendar
Using the Google Calendar API, the script creates events for each course’s midterm and final exams. The events include:
- **Title**: Course name with "Exam" appended.
- **Start and End Times**: Exact timings for each exam.
- **Time Zone**: Set to "Asia/Bangkok" for compatibility.

Each event is automatically added to the user's primary Google Calendar. Upon successful creation, the script outputs a confirmation message with a link to the event.

## Benefits

This script eliminates the hassle of manually entering exam dates into Google Calendar. By automating OCR, data parsing, and calendar integration, it saves users significant time and ensures accuracy. Its ability to handle multiple courses in one execution makes it especially useful for students with packed schedules.

## Prerequisites

- **Python 3.7+**
- Tesseract-OCR installed on your system ([Installation Guide](https://github.com/tesseract-ocr/tesseract))
- Google Calendar API enabled ([Guide](https://developers.google.com/calendar/quickstart/python))
- A `.env` file with your credentials file path.