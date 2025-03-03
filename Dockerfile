FROM python:3.12
# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copy the source code to the container
COPY application /application

# Copy the source code to the container
COPY streamlit_app.py streamlit_app.py


# # Change the working directory
# WORKDIR /app

# Expose the port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501"]
