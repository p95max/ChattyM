# ChattyM — Social Network (Django)

**ChattyM** is a learning project: a minimal social network built with **Django 5**, **PostgreSQL**, and **Bootstrap 5**.  
It demonstrates core web development skills: authentication, user profiles, content creation, and containerized deployment.

## Features

- 👤 **User Authentication**
  - Custom user model with email login
  - Registration, login, logout
  - Email confirmation & password reset (via console in dev)
- 📄 **User Profiles**
  - Editable profile with avatar, birthday, description
  - Profile creation date tracking
- 📝 **Content**
  - Create, edit, and delete posts
  - Comment system
  - Likes
- 🔔 **Subscriptions**
  - Follow/unfollow users
  - Personalized feed with posts from subscriptions
- ⚙️ **Admin**
  - Manage users, posts, comments
  - Basic moderation
- 🔌 **REST API**
  - DRF-based endpoints for:
    - Users & profiles
    - Posts, comments, likes
    - Subscriptions & feeds
  - Token/session authentication
  - Swagger/OpenAPI docs (`/api/docs/`)

## Tech Stack

- **Backend:** Django 5, Django ORM  
- **Frontend:** Django Templates (DTL), Bootstrap 5  
- **Database:** PostgreSQL  
- **Auth:** django-allauth 2.0  
- **Storage:** Local filesystem (MinIO/S3 optional)  
- **Deployment:** Docker + Docker Compose  
- **Testing:** Pytest / Unittest  

## User Authentication

The project uses **django-allauth 2.0** for authentication:  
- sign up & login with email,  
- password reset and recovery, 
- email verification (console output in dev),
- uses custom `User` model extends Django’s `AbstractUser` with email-based authentication.