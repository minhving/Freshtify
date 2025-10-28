# Use our customized image based on Node.js 20 slim image as a base
FROM node:22-bookworm

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash -d /usr/src/app appuser

# Set the working directory
WORKDIR /usr/src/app

# Ensure the non-root user owns the working directory
RUN chown -R appuser:appuser /usr/src/app

# Copy the application code as the non-root user
COPY --chown=appuser:appuser . .

# Install dependencies & build code
RUN	npm install && npm run build

CMD ["npm","run", "start"]