# Army Personnel & Inventory Management System

A comprehensive CRM system for managing army personnel and inventory with blockchain integration, role-based access control, and real-time alerts.

## Features

- **Blockchain Integration**: Secure data storage using Hyperledger Fabric
- **Role-Based Access Control**: Admin, Supply Officer, and Viewer roles
- **Inventory Management**: Track supplies with threshold alerts
- **Personnel Management**: Secure storage of personnel records
- **Real-time Alerts**: Email, SMS, and in-app notifications
- **Modern UI**: Built with CustomTkinter for a modern look and feel

## Prerequisites

- Python 3.8 or higher
- Hyperledger Fabric network (for blockchain integration)
- Twilio account (for SMS alerts)
- SMTP server (for email alerts)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/army-crm.git
cd army-crm
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:
- Blockchain network details
- Email server credentials
- Twilio account details
- Application settings

## Running the Application

1. Start the application:
```bash
python main.py
```

2. Login with your credentials:
- Default admin username: admin
- Default admin password: (set in .env file)

## Project Structure

- `main.py`: Main application entry point
- `models.py`: Data models and blockchain interactions
- `utils.py`: Utility functions for security, alerts, and validation
- `requirements.txt`: Project dependencies
- `.env`: Environment configuration

## Security Features

- End-to-end encryption for sensitive data
- Role-based access control
- JWT-based authentication
- Blockchain-based audit logging
- Secure password hashing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or create an issue in the repository. 