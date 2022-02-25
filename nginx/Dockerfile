FROM nginx:1.21-alpine

ENV DOCKERIZE_VERSION=v0.6.1 

RUN rm /etc/nginx/conf.d/default.conf \
    apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    bash \
    curl \
    # Defining build-time-only dependencies:
    # Installing `dockerize` utility:
    # https://github.com/jwilder/dockerize
    && wget "https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
    && tar -C /usr/local/bin -xzvf "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
    && rm "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" && dockerize --version \
CMD dockerize -template nginx.tmpl:/etc/nginx/nginx.conf -stdout /var/log/nginx/access.log -stderr /var/log/nginx/error.log -wait tcp://web:8000 nginx
# COPY nginx.conf /etc/nginx/conf.d
