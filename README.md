# Flasker Blog Website
![alt text](https://github.com/mahmoudi-1798/flasker/blob/master/static/images/screenshot.png?raw=true)
This project is a Flask-based blog website that has been developed based on the course by [@flatplanet](https://github.com/flatplanet). The website is designed to allow users to create, read, and interact with blog posts. It utilizes the Flask web framework and employs a MySQL database to manage and store the blog content.

## Features

- Create new blog posts.
- View existing blog posts.
- User registration and authentication.
- MySQL database integration.

## Future Features 
- Interact with blog posts (likes, comments, etc.).

## Installation

1. Clone the repository to your local machine:

   ```
   git clone https://github.com/mahmoudi-1798/flasker
   ```

2. Create a virtual environment (optional but recommended):

   ```
   python -m venv venv
   source venv/bin/activate   
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up your MySQL database and update the configuration:

   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/dbname'
   ```

5. Initialize the database:

   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the Flask application:

   ```
   flask run
   ```

## Contributing

Contributions are welcome! If you find any issues or would like to add new features, feel free to submit a pull request.

