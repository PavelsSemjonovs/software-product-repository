# Prison Management System

University software engineering project.

## Product Idea

Prison Management System is a desktop application built with Python, Tkinter, and SQLite for managing prison-related data through a graphical interface.

The system allows users to manage:
- prisons,
- prisoners,
- guards,
- audit records,
- and computed cell assignments.

## Problem

Managing prison records manually is inefficient and error-prone.  
This project provides a centralized system for storing and managing prison data with validation and audit functionality.

## Target Users

- Prison administration staff
- Educational/demo users
- Database management students

## Technologies Used

- Python
- Tkinter
- SQLite

## Core Features

- Prison management
- Prisoner management
- Guard management
- Audit logging using database triggers
- Search functionality
- Capacity validation
- Computed cell assignment display
- Desktop graphical interface

## Project Structure

- `db_core.py` — database logic and SQLite operations
- `gui_app.py` — Tkinter graphical user interface
- `docs/` — project management and roadmap documentation
- `AGENTS.md` — instructions and constraints for AI assistants

## MVP Goals

The MVP focuses on:
- stable CRUD operations,
- validation,
- database integrity,
- and a functional desktop interface.

Advanced features such as authentication, reporting, and cloud storage are planned for future versions.
