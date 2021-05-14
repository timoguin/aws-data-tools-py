DEPS :=awk docker-compose grep realpath

#==============================================================================
define INFO

name:         Generic boilerplace wrapper
version:      0.1.0
maintainers:  timoguin@gmail.com
git:          https://github.com/timoguin/makefiles//boilerplate/Makefile

dependencies: ${DEPS}

endef
export INFO
#==============================================================================


test : deps ## 
	@printf "${OK}%s...\n${CCEND}" "Starting localstack"
	@docker-compose --log-level ERROR up --detach >/dev/null
	@pushd tests >/dev/null && ./test.sh && popd >/dev/null || popd >/dev/null

.PHONY: help 
help : deps ## Show help for available targets
	@echo "Available commands:"
	@echo
	@cat Makefile* | grep -E '^[a-zA-Z_-]+ ?:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36mmake %-30s\033[0m %s\n", $$1, $$2}'
	@echo

.PHONY: info
info : ## Show metadata info about this Makefile
	@echo "Makefile metadata:"
	@echo "$$INFO"

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
