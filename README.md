# 🫡My National Service Project Automation on Duty Planning & Roll Call

## Introduction
This project aims to address inefficiencies and manpower wastage in daily military procedures by digitalizing and automating key tasks. The two main automations implemented are the Automated Attendance Taking system and the Automated Duty Roster system. These systems streamline processes that were previously manual, resulting in improved accuracy, efficiency, and user satisfaction.

## Learning and Development
To develop this project, I acquired proficiency in various programming languages and frameworks, including JavaScript, HTML, CSS, and Python. Flask, a Python web framework, served as the foundation for building the backend of the website, along with essential extensions such as Flask-SQLAlchemy and Flask-Login. Additionally, I gained expertise in cloud computing, utilizing Amazon Web Services (AWS) to host the website and ensure accessibility for all users.

## Features & Functions
### Security & Access
- Implemented Flask-Login for user authentication and role-based access control.
- Users are required to create accounts upon joining the battalion, with access privileges assigned based on their roles.
- Role-based access control ensures that users can only access information relevant to their responsibilities.

### Automated Attendance Taking
- Servicemen can submit their attendance status through the website, eliminating the need for manual submission via alternative means.
- Commanders can oversee attendance and finalize the roll call list through dedicated pages, improving transparency and efficiency.

### Automated Duty Roster
- Servicemen can submit block-off dates and reasons for inability to perform duty, facilitating duty planning.
- The Duty Roster System automates duty planning based on servicemen attributes, ensuring fairness and impartiality.
- Duty managers can make adjustments to the duty roster as needed, with changes reflected in real-time.

### Data Management
- Utilized Flask-SQLAlchemy and SQLite database to store servicemen data, role-based access control, attendance records, and duty roster information.
- Integrated Openpyxl framework to transfer data between the website and Excel spreadsheets, ensuring compatibility with military requirements.

## Report
- For a detailed report on the project, please refer to the [PDF Report](link-to-pdf-report-file.pdf).

## Testimonial
- Testimonial: [Testimonial PDF](link-to-testimonial-pdf-file.pdf)

## Usage
1. Clone the repository: git clone https://github.com/yourusername/military-automation.git
2. Install dependencies:pip install -r requirements.txt
3. Configure the application settings in `config.py`.
4. Initialize the database:
  flask db init
  flask db migrate
  flask db upgrade
5. Run the application:flask run

## Conclusion
The Military Automation System significantly improves the efficiency and accuracy of daily procedures in the military. By leveraging automation and digitalization, this project enhances user experience and optimizes resource allocation. Future enhancements include features to allow workshop-specific parade state downloads and servicemen's choice in duty scheduling.

## Technologies
- Flask: [Flask Framework](https://flask.palletsprojects.com/)
- AWS: [Amazon Web Services](https://aws.amazon.com/)
- Openpyxl: [Openpyxl Framework](https://openpyxl.readthedocs.io/en/stable/)

## Contact
For inquiries or feedback, please contact the project maintainer at [email@example.com](mailto:email@example.com).


