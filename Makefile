DEPS :=awk docker-compose grep realpath poetry
AWS_OKTA_PROFILE :=

ifneq (${AWS_OKTA_PROFILE},)
	SHELL_CMD_PREFIX =aws-okta exec ${AWS_OKTA_PROFILE} --
endif

.PHONY: default
default: help

.PHONY: shell
shell: venv ## Activate the Python virtual environment in a subshell
	@${SHELL_CMD_PREFIX} poetry shell

.PHONY: venv-create
venv-create:
	@test -d .venv || { \
	     python -m venv .venv >/dev/null && \
		 .venv/bin/pip install --quiet --upgrade pip && \
		 make venv-install
	 }

.PHONY: venv-install
venv-install: ## Install Python dependencies in the virtual environment
	@poetry install --extras="devtools docs" --no-interaction --quiet

.PHONY: venv-update
venv-update: ## Update dependencies in the Python virtual environment
	poetry update --quiet --no-interaction


.PHONY: clean
clean:
	# @rm -rf .venv
	@find . -iname '*.pyc' -exec rm {} \;

.PHONY: test
test : deps
	@printf "${OK}%s...\n${CCEND}" "Starting motoserver"
	@docker-compose --log-level ERROR up --detach >/dev/null
	@pushd tests >/dev/null && ./test.sh && popd >/dev/null || popd >/dev/null

.PHONY: help 
help : deps ## Show help for available targets
	@echo "Available commands:"
	@echo
	@cat Makefile | grep -E '^\.PHONY: [a-zA-Z_-]+  ?## .*$$' | awk 'BEGIN {FS = ":  ?## "}; {printf "\033[36mmake %-30s\033[0m %s\n", $$1, $$2}'
	@echo

# Check that dependencies are installed. Upon failure, prints an error and
# the list of dependencies that were not found.
.PHONY: deps
deps :
	@\
deps_not_found=; \
for dep in ${DEPS}; do \
  if ! command -v $$dep &> /dev/null; then deps_not_found+="$$dep "; fi; \
done; \
if [ "$$deps_not_found" != "" ]; then \
  printf "${ERROR}%s${CCEND}\n" \
    "This script has unmet dependencies: $$deps_not_found"; \
  exit 1; \
fi

# Colors
OK    ="\\033[32m"
WARN  ="\\033[33m"
ERROR ="\\033[31m"
CCEND ="\\033[0m"
