FROM nginx:alpine

RUN apk add --no-cache curl

RUN rm -f /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d/default.conf

HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -f http://localhost/ || exit 1
