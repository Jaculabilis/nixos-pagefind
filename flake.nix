{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.flake-compat.url = "github:edolstra/flake-compat";
  inputs.nixos-search.url = "github:NixOS/nixos-search";
  inputs.nixos-search.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    {
      self,
      nixpkgs,
      flake-compat,
      nixos-search,
    }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      formatter.${system} = pkgs.nixfmt-rfc-style;

      packages.${system} = {
        staticgen = import ./staticgen { inherit pkgs; };
      };

      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.pagefind
          pkgs.jq
          nixos-search.packages.${system}.flake-info
          pkgs.uv
          pkgs.ruff
        ];
      };
    };
}
