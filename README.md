# nixos-pagefind

This repo implements a package search for NixOS based on [`pagefind`](https://pagefind.app), a fully static search tool.
This enables the whole search stack to be served by static hosting with no search index backend.

## Implementation notes

### staticgen

`staticgen` implements the first two steps of the build process:
importing packages from nixpkgs and generating individual pages from each package description.
The results of the nixpkgs import can be cached to JSON for faster iteration on changes to the page generation.
The generated pages are annotated with `pagefind`-specific data attributes to enable filtering.
