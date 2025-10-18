# Army Management System

A desktop application for managing military personnel and equipment built with Python and Tkinter.

## Features

- Personnel management (add, edit, delete personnel records)
- Search functionality
- Unit management
- Equipment tracking
- Medical status tracking
- Reporting capabilities
- Persistent data storage using JSON
- Modern and clean user interface
- Form validation

## Requirements

- Python 3.x (Tkinter is included in the standard library)
- No additional packages required

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Run the application using Python:

```bash
python main.py
```

## Usage

- Use the search box to filter personnel
- Click "Add Personnel" to create a new personnel record
- Select a personnel from the list to view/edit their details
- Click "Save" to save changes
- Use the "Delete Personnel" button to remove a personnel record
- Access reports and additional options through the menu bar

## Data Fields

The system tracks the following information for each personnel:
- ID
- Name
- Rank
- Unit
- Date of Birth
- Date of Enlistment
- Specialization
- Equipment
- Medical Status
- Notes

## Reports

The system includes two types of reports:
1. Unit Summary - Shows the number of personnel in each unit
2. Equipment Status - Shows the distribution of equipment among personnel

## Data Storage

Personnel data is stored in the `data/personnel.json` file. The application will create this directory automatically when first run.

## License

This project is open source and available under the MIT License. 