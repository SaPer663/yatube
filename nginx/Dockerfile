FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf && addgroup nobody tty
COPY nginx.conf /etc/nginx/conf.d
