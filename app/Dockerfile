FROM python:alpine3.7
# RUN apk add --update curl && \
#     rm -rf /var/cache/apk/*
RUN adduser -D 101

ARG SOURCE
ARG DEST
ARG TOKEN

COPY . /app
WORKDIR /app
RUN pip install -r requirement.txt
USER 101
ENTRYPOINT [ "python3" ]
CMD ["work_log.py","-st","$SOURCE","-t","$TOKEN","-dt","$DEST"]





# RUN pip install --proxy=https://pkg.proxy.prod.jp.local:10080 -r requirement.txt
