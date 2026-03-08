ARG APP_VERSION=0.0.1

LABEL name="MediaLyze"
LABEL org.opencontainers.image.source="https://github.com/frederikemmer/MediaLyze"
LABEL org.opencontainers.image.version="${APP_VERSION}"

ENV APP_VERSION=${APP_VERSION}
ENV NEXT_PUBLIC_APP_VERSION=${APP_VERSION}

WORKDIR /app

EXPOSE 8008
