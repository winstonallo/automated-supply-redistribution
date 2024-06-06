# Project: Bob
## This project is for creating orders for the BIPA shops to redistribute goods.

## Technologies Used
Docker: containerization platform (https://www.docker.com/)<br>
Docker Compose: tool for defining and running multi-container applications (https://docs.docker.com/compose/)<br>
Python: programming language used for the web application<br>
PostgreSQL: relational database management system (https://www.postgresql.org/docs/)<br>
## Getting Started
Install Docker: Follow the installation instructions for your operating system from the official Docker documentation (https://www.docker.com/ -> "Get Docker").<br>
Clone the project repository: Use `git clone` to clone the project repository to your local machine.<br>
Running the Project<br>
Build and run the application: Navigate to the source directory in your terminal and run `make run`. This command will use Docker Compose to build the Docker images for your application and database, start the containers, and run your web application. Then you can access web-page through (http://localhost:8000/)<br>
Important note: the first build can take up to 10 minutes.<br>

## (Optional) Debug the application
Use `make debug` to run the application in debug mode. This allows you to attach a debugger to the running container for easier troubleshooting.<br>

## Stopping the Project
Use `make stop` to gracefully stop the running containers.<br>

## Cleaning Up
Use `make clean` to remove all stopped containers, unused volumes, networks, and images created by Docker Compose. This can be helpful when you want to start from a fresh development environment.<br>

For a more thorough cleanup, including removing build cache and local project files, use `make fclean`. This command will also remove Python bytecode files (__pycache__), database migrations, and static files from your project directory.<br>

## Environment Variables
The project uses an `.env` file to store sensitive environment variables like database credentials. You can create a .env file in the project directory and populate it with the following values:<br>

`DB_NAME`: Name of the database (default: `db`)<br>
`DB_USER`: Username for accessing the database (default: `user`)<br>
`DB_PASSWORD`: Password for accessing the database (default: `password`)<br>
`DB_HOST`: Hostname or IP address of the database container (default: `db`) - in this case, it points to the db service within the docker-compose configuration.<br>
`DB_PORT`: Port on which the database service is listening (default: `5432`)<br>

## Additional Notes
This documentation assumes a basic understanding of Docker and Docker Compose.<br>
Refer to the `docker-compose.yml` and `Makefile` for more details about the project configuration.<br>
Feel free to contribute to the project!<br>

## Plans for the future
1. Add an authentication system for staff members and admin users.
2. Finish a statitistic page.
3. Connect our system with other BIPA's systems.
4. Improve our soultion after getting more data from other BIPA's systems.