FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies including GDAL/GEOS for GeoDjango
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Make build script executable
RUN chmod +x build.sh

# Run build script
RUN ./build.sh

# Expose port
EXPOSE 10000

# Start command
CMD ["gunicorn", "djecommerce.wsgi:application", "--bind", "0.0.0.0:10000"]
