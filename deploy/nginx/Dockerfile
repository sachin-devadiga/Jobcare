FROM nginx:1.25-alpine

RUN apk add --no-cache curl tzdata certbot-nginx

RUN rm -f /etc/nginx/conf.d/default.conf && \
    mkdir -p /etc/nginx/conf.d /var/www/certbot /var/www/frontend

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD nginx -t && curl --fail http://localhost:80/api/health/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
