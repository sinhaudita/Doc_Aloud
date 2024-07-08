import pyttsx3
import PyPDF2
import os

speaker = pyttsx3.init()
speaker.setProperty('rate', 150)  # Increase the rate for faster speech

def add_pdf_file(pdf_files):
    while True:
        speaker.say("Please enter the PDF of the book you want me to read, or type 'done' to finish adding files.")
        speaker.runAndWait()
        pdf_name = input("Enter the PDF file name or 'done' to finish: ")

        if pdf_name.lower() == 'done':
            break

        if os.path.exists(pdf_name) and pdf_name.lower().endswith('.pdf'):
            pdf_files.append(pdf_name)
        else:
            speaker.say("Invalid file. Please provide a valid PDF file.")
            speaker.runAndWait()

def choose_pdf_to_read(pdf_files):
    while True:
        speaker.say("Choose the PDF you want to read:")
        for i, pdf_name in enumerate(pdf_files):
            speaker.say("{}. {}".format(i + 1, pdf_name))

        speaker.runAndWait()
        choice = input("Enter the number of the PDF you want to read (or 'done' to finish): ")

        if choice.lower() == 'done':
            break

        try:
            choice = int(choice)
            if 1 <= choice <= len(pdf_files):
                pdf_name = pdf_files[choice - 1]
                book = open(pdf_name, 'rb')
                pdfReader = PyPDF2.PdfReader(book)
                pages = len(pdfReader.pages)

                speaker.say("Book '{}' has {} pages. From which page should I start reading?".format(pdf_name, pages))
                speaker.runAndWait()

                page_no = int(input(
                    "Input the page number from which you want to start listening to the book '{}': ".format(pdf_name)))

                speaker.say("can I start reading '{}'?".format(pdf_name))
                speaker.runAndWait()

                yes = input("Can I start Reading '{}' (yes/no): ".format(pdf_name))

                if yes.lower() == "yes":
                    for num in range(page_no - 1, pages):  # Subtract 1 from page_no
                        page = pdfReader.pages[num]
                        text = page.extract_text()

                        words = text.split()  # Split the text into words
                        page_text = ' '.join(words)  # Accumulate words on the page
                        speaker.say(page_text)  # Read the entire page content
                        speaker.runAndWait()  # Call runAndWait after each page
                else:
                    continue
            else:
                speaker.say("Invalid choice. Please enter a valid number.")
                speaker.runAndWait()
        except ValueError:
            speaker.say("Invalid input. Please enter a valid number.")
            speaker.runAndWait()

#else:
    #choose_pdf_to_read(pdf_files)

speaker.say("Please Enter Your Name")
speaker.runAndWait()
name = input("Enter your Name: ")

speaker.say('Hey {}! I am Pie, at your service. What would you like me to do?'.format(name))
speaker.runAndWait()

task = input("Please Enter what you want me to do: ")

if task.lower() == "read":
    speaker.say("Okay, I will read a book for you.")
    speaker.runAndWait()

    # Create a list of PDF files
    pdf_files = []
    add_pdf_file(pdf_files)

    choose_pdf_to_read(pdf_files)
else:
    speaker.say("I'm sorry, I can only read books. Please select the 'read a book' option.")
    speaker.runAndWait()

