From alpine
MAINTAINER "Divesh Angula" <divesh.angula@quantum.com>

RUN apk add --no-cache bash py-virtualenv git sudo gcc python2-dev python2-dev \
       libc-dev libxml2-dev libxslt-dev
RUN git clone https://github.com/dangula/s3-tests.git \
  && cd s3-tests \
  && ./bootstrap

ADD runS3Tests.sh /

ENTRYPOINT ["/runS3Tests.sh"]
