DEPS :=awk docker docker-compose grep poetry realpath sed
AWS_OKTA_PROFILE :=
PY_INSTALL_ARGS :=--extras="cli devtools docs"

ifneq (${AWS_OKTA_PROFILE},)
	SHELL_CMD_PREFIX =aws-okta exec ${AWS_OKTA_PROFILE} --
endif

.PHONY: default
default: help

.PHONY: shell ## Activate the Python virtual environment in a subshell
shell: .venv
	@${SHELL_CMD_PREFIX} poetry shell

.PHONY: test-integration ## Run the integration test suite
test-integration: run-test-server
	@printf "${OK}%s...\n${CCEND}" "Starting motoserver"
	@docker-compose --log-level ERROR up --detach >/dev/null
	@pushd tests >/dev/null && ./test.sh && popd >/dev/null || popd >/dev/null

.PHONY: run-test-server ## Start motoserver with docker-compose if it's not running
run-test-server:
	@CONTAINER_ID=$$(docker-compose ps --quiet motoserver 2>/dev/null);            \
	 CONTAINER_START=0;                                                            \
	 if [ "$$CONTAINER_ID" != "" ]; then                                           \
	   if ! $$(docker ps --quiet --no-trunc | grep --quiet "$$CONTAINER_ID"); then \
	     CONTAINER_START=1;                                                        \
	   fi;                                                                         \
	 else                                                                          \
	   CONTAINER_START=1;                                                          \
	 fi;                                                                           \
	 if [ $$CONTAINER_START -eq 1 ]; then                                          \
	   docker-compose up --detach --no-recreate --remove-orphans;                  \
	 fi

.PHONY: stop-test-server ## Stop motoserver container(s)
stop-test-server:
	@docker-compose down --remove-orphans --volumes

.PHONY: build ## Build the Python package for distribution
build: .venv
	@poetry build --quiet --no-interaction

# Ensures the Python venv exists and has dependencies installed
.venv:
	@python -m venv .venv >/dev/null
	@.venv/bin/pip install --quiet --upgrade pip
	@make python-install-deps

.PHONY: python-install-deps ## Install Python dependencies in the venv
python-install-deps: .venv
	@poetry install --quiet --no-interaction ${PY_INSTALL_ARGS}

.PHONY: python-update-deps ## Update Python dependencies in the venv
python-update-deps: .venv
	@poetry update --quiet --no-interaction

.PHONY: clean ## Remove temp files and build artifacts
clean:
	@find . \( -iname '*.pyc' -o -name '__pycache__' \) -path './aws_data_tools/*' -exec rm -rf {} \+ || true; >/dev/null 2>&1
	@poetry install --remove-untracked --quiet 

.PHONY: clean-all ## Run clean, remove the Python venv and untracked / ignored Git files
clean-all: clean
	@git clean --quiet --force -d -x -X
	@docker-compose down --rmi 'all' --volumes --remove-orphans

.PHONY: help
help:
	@echo "Available commands:"
	@echo
	@cat Makefile                                 \
	   | grep -E '^\.PHONY: [a-zA-Z_-]+ ## .*$$'  \
	   | sed 's/^\.PHONY: //'                     \
	   | awk 'BEGIN {FS = " ## "}; {printf "\033[36mmake %-30s\033[0m %s\n", $$1, $$2}'
	@echo

.PHONY: deps ## Check that dependencies are installed
deps:
	@deps_not_found=;                                                         \
	 for dep in ${DEPS}; do                                                   \
	   if ! command -v $$dep &> /dev/null; then deps_not_found+="$$dep "; fi; \
	 done;                                                                    \
	 if [ "$$deps_not_found" != "" ]; then                                    \
	   printf "${ERROR}%s${CCEND}\n"                                          \
	     "This script has unmet dependencies: $$deps_not_found";              \
	   exit 1;                                                                \
	 fi

# Colors
OK    ="\\033[32m"
WARN  ="\\033[33m"
ERROR ="\\033[31m"
CCEND ="\\033[0m"
