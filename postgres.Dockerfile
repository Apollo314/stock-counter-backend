FROM postgres:latest

ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}
ENV LANG tr_TR.utf8

RUN localedef -i tr_TR -c -f UTF-8 -A /usr/share/locale/locale.alias tr_TR.UTF-8
