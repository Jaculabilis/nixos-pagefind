.PHONY: help
help: ## display this help
	@awk 'BEGIN{FS = ":.*##"; printf "\033[1m\nUsage\n \033[1;92m make\033[0;36m <target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } ' $(MAKEFILE_LIST)

.PHONY: data
data: data/intake.json data/android-tools.json data/hello.json ## generate test data

data/intake.json:
	@mkdir -p data
	flake-info --json flake 'git+https://git.alogoulogoi.com/Jaculabilis/intake?ref=go' | jq > data/intake.json

data/android-tools.json:
	@mkdir -p data
	flake-info --json nixpkgs --attr android-tools unstable | jq > data/android-tools.json

data/hello.json:
	@mkdir -p data
	flake-info --json nixpkgs --attr hello unstable | jq > data/hello.json

data/nixpkgs.json:
	@mkdir -p data
	flake-info --json nixpkgs unstable | jq > data/nixpkgs.json

data/nixpkgs-small.json: data/nixpkgs.json
	@mkdir -p data
	jq '[ .[range(10; length; 100)] ]' data/nixpkgs.json > data/nixpkgs-small.json

.PHONY: out
out:
	rm -rf out || true
	python3 build.py out data/nixpkgs.json

.PHONY: build
build:
	cp index.html out/index.html
	pagefind --site out --serve
