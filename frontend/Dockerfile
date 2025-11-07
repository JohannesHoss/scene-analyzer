FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static files
COPY static/ /usr/share/nginx/html/

# Expose port
EXPOSE 80

# Nginx runs automatically via base image CMD
