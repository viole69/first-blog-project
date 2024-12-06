# Blog Application

A full-stack blog application built with **Flask**, **PostgreSQL**, and hosted on **Render**. The project features secure user authentication, an admin interface for post management, and a commenting system for blog posts.

## Features

- **User Authentication**: Users can sign up, log in, and log out with securely hashed and salted passwords.
- **Admin Dashboard**: Admin users can add, edit, and delete blog posts.
- **Comment System**: Registered users can leave comments on blog posts.
- **Database**: Uses **PostgreSQL** for storing user data, blog posts, and comments.
- **Security**: Implements password hashing and salting using **Werkzeug**.
- **Deployment**: Hosted on **Render**.

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS (Bootstrap Template), minimal JavaScript
- **Database**: PostgreSQL
- **Authentication**: Werkzeug (Password Hashing)
- **Deployment**: Render

## Installation

To run this project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/viole69/first-blog-project.git
   cd blog-project
   python3 -m venv venv
source venv/bin/activate  # For Windows use: venv\Scripts\activate
pip install -r requirements.txt
flask run

