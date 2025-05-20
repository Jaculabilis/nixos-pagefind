.PHONY: help
help: ## display this help
	@awk 'BEGIN{FS = ":.*##"; printf "\033[1m\nUsage\n \033[1;92m make\033[0;36m <target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } ' $(MAKEFILE_LIST)

data/nixpkgs.json: ## generate nixpkgs test data
	@mkdir -p data
	nix run .#staticgen -- --channel nixos-unstable --write-json data/nixpkgs.json

data/nixpkgs-small.json: data/nixpkgs.json  ## generate a smaller subset of test data for faster pagefind
	@mkdir -p data
	jq 'with_entries(select(.key | test("(^an)|(^h)")))' data/nixpkgs.json > data/nixpkgs-small.json

.PHONY: out
out: data/nixpkgs.json
	rm -rf out || true
	nix run .#staticgen -- --from-json data/nixpkgs.json --out out

.PHONY: out-small
out-small: data/nixpkgs-small.json
	rm -rf out || true
	nix run .#staticgen -- --from-json data/nixpkgs-small.json --out out

.PHONY: build
build:
	cp index.html out/index.html
	pagefind --site out --serve
