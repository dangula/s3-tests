#!/usr/bin/env bash

if [ ! -z "$S3_HOST" ]; then
  echo "Connect to Castle Host $S3_HOST and create object store and users"
  # Create object store service and users on castle and generated s3test.conf file
  source s3-tests/virtualenv/bin/activate \
  && ./s3-tests/virtualenv/bin/python s3-tests/castle/castleSetup.py $S3_HOST
else
    echo "need S3_HOST env"
    exit 1
fi

#start s3Compatibility tests
echo 'Starting s3-tests ...'
source s3-tests/virtualenv/bin/activate \
&& S3TEST_CONF=/tmp/s3test.conf ./s3-tests/virtualenv/bin/nosetests -a '!fails_on_aws' -v -collect-only --with-xunit --xunit-file=/logs/s3tests/nosetest.xml"$@" 2>&1 | tee /logs/s3tests/nosetest.log