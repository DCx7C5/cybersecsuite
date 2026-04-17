FROM postgres:18-alpine


ENV TERM=xterm-256color

# Keep a tiny custom wrapper for project-specific startup logging,
# then delegate to the official postgres entrypoint for initdb/PGDATA handling.
RUN mkdir -p /etc/postgresql && chown -R postgres:postgres /etc/postgresql

COPY --chmod=640 postgresql.conf /etc/postgresql/postgresql.conf
RUN chown postgres:postgres /etc/postgresql/postgresql.conf

COPY --chmod=755 entrypoint.sh /usr/local/bin/cybersec-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/cybersec-entrypoint.sh"]
