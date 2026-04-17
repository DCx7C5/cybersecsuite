FROM redis:7-alpine

# Minimal config: persistence off (forensic cache only), max 256MB
RUN echo "maxmemory 256mb" >> /usr/local/etc/redis/redis.conf \
    && echo "maxmemory-policy allkeys-lru" >> /usr/local/etc/redis/redis.conf \
    && echo "save ''" >> /usr/local/etc/redis/redis.conf \
    && echo "appendonly no" >> /usr/local/etc/redis/redis.conf

EXPOSE 6379

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD redis-cli ping || exit 1
