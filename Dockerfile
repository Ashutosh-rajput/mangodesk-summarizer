# Step 1: Use an official Python runtime as a parent image
# python:3.11-slim is a good balance of size and functionality.
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
# This is where your application code will live.
WORKDIR /app

# Step 3: Copy the requirements file into the container
# This is done first to leverage Docker's layer caching.
# The dependencies layer will only be rebuilt if requirements.txt changes.
COPY requirements.txt .

# Step 4: Install the Python dependencies
# --no-cache-dir keeps the image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of your application code into the container
# This includes main.py and the 'frontend' directory.
COPY . .

# Step 6: Expose the port the app runs on
# Your app will listen on port 80 inside the container.
EXPOSE 8080

# Step 7: Define the command to run your application
# Use 0.0.0.0 to make the server accessible from outside the container.
# This command runs when the container starts.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]