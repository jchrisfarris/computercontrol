

# Static, not sure if needed??
PYTHON=python3
PIP=pip3

FILES =	skill-endpoint.py

DEPENDENCIES =  ask_sdk_runtime \
				chardet \
				requests \
				ask_sdk \
				bin \
				dateutil \
				urllib3 \
				ask_sdk_core \
				boto3 \
				docutils \
				s3transfer \
				ask_sdk_dynamodb \
				botocore \
				idna \
				ask_sdk_model \
				certifi \
				jmespath \
				six.py

package: test clean deps zipfile

#
# Lambda function management
#

clean:
	rm -rf __pycache__ *.zip *.dist-info $(DEPENDENCIES)

# # Create the package Zip. Assumes all tests were done
zipfile:  $(FILES) $(DEPENDENCIES)
	zip -r $(LAMBDA_PACKAGE) $^

test: $(FILES)
	for f in $^; do $(PYTHON) -m py_compile $$f; if [ $$? -ne 0 ] ; then echo "$$f FAILS" ; exit 1; fi done

deps:
	$(PIP) install -r requirements.txt -t . --upgrade
