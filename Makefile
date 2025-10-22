# Makefile for Nextcloud Calendar AI Agent

.PHONY: build deploy test clean validate

# Build the SAM application
build:
	sam build

# Deploy with guided setup
deploy-guided:
	sam deploy --guided

# Deploy with existing config
deploy:
	sam deploy

# Validate SAM template
validate:
	sam validate

# Test locally
test-local:
	sam local start-api

# Test the deployed agent
test:
	python3 test_agent.py

# Clean build artifacts
clean:
	rm -rf .aws-sam/

# Package for deployment
package:
	sam package --s3-bucket $(S3_BUCKET) --output-template-file packaged.yaml

# Delete the stack
delete:
	sam delete

# Show stack outputs
outputs:
	aws cloudformation describe-stacks --stack-name nextcloud-calendar-ai --query 'Stacks[0].Outputs'

# Tail logs
logs:
	sam logs -n NextcloudCalendarFunction --stack-name nextcloud-calendar-ai --tail

# Help
help:
	@echo "Available commands:"
	@echo "  build         - Build the SAM application"
	@echo "  deploy-guided - Deploy with guided setup"
	@echo "  deploy        - Deploy with existing config"
	@echo "  validate      - Validate SAM template"
	@echo "  test-local    - Test locally"
	@echo "  test          - Test deployed agent"
	@echo "  clean         - Clean build artifacts"
	@echo "  delete        - Delete the stack"
	@echo "  outputs       - Show stack outputs"
	@echo "  logs          - Tail function logs"