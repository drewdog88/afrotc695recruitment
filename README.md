# AFROTC 695 Recruitment Management System

This repository contains a comprehensive recruitment management system for AFROTC Detachment 695 at the University of Portland.

## Project Overview

This web application is designed to streamline and secure the recruitment process for Air Force ROTC Detachment 695. It provides tools for tracking potential recruits, managing existing cadre, coordinating with university contacts, and scheduling recruitment events.

## Features

### 1. Potential Recruit Tracking
- Track potential recruits from high schools and colleges
- Store: name, major, school, high school graduation year, expected college graduation year
- Generate reports and analytics

### 2. Cadre Management
- Manage existing AFROTC cadre information
- Track: graduation year, major, cadet rank, hometown, officer interest, enrollment status
- Record unenrollment reasons
- Form-based data entry with table display

### 3. University Contact Management
- Maintain contact list for recruitment coordination
- Calendar integration for recruitment events
- Event scheduling and tracking

### 4. Security & Administration
- Secure authentication system
- Role-based access control (Admin/User)
- Usage tracking and analytics
- Multi-administrator support

## Technology Stack

- **Frontend**: React.js with TypeScript
- **Backend**: Node.js with Express
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT tokens
- **Styling**: Tailwind CSS
- **Deployment**: Docker-ready

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/drewdog88/afrotc695recruitment.git
cd afrotc695recruitment
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
afrotc695recruitment/
├── client/                 # React frontend
├── server/                 # Node.js backend
├── database/              # Database schemas and migrations
├── docs/                  # Documentation
└── docker/                # Docker configuration
```

## Contributing

This project is for official AFROTC use. Please follow the established guidelines for contributing to this project.

## License

This project is for official AFROTC use. 