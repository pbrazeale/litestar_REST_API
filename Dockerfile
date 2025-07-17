# Set the python version
FROM python:3.12.3
# Set working directory
WORKDIR /app
# Copy required files from above set working directory
COPY . /app
# Install the requirements 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
# Expose the app port
EXPOSE 80
# Run app with Litestar CLI
CMD ["litestar", "run", "--host", "0.0.0.0", "--port", "80", "--reload"]
