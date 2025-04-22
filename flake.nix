{
  description = "oauthlib";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        # pkgs = nixpkgs.legacyPackages.${system};
        overlays = [ ];
        pkgs = import nixpkgs { inherit system overlays; };
        python = pkgs.python;

        nativeBuildInputs = with pkgs; [
          python313
          jq
          openssl
          pkg-config
        ] ++ (with pkgs.python313Packages; [
          requests
          pyjwt
          jwcrypto
          cryptography
          ipython
          sqlite
          pudb
          pyopenssl
          # pytest
          # pytest-cov
        ]);
        propagatedBuildInputs = with pkgs.python313Packages; [
          noiseprotocol
          flask
          flask-sqlalchemy
          authlib
          cryptography
        ];

        buildInputs = with pkgs; [
          openssl
          pkg-config
        ] ++ (with pkgs.python313Packages; [
          cryptography
        ]);
      in {
        devShells.default = pkgs.mkShell {
          inherit nativeBuildInputs propagatedBuildInputs buildInputs;
        };

        # packages.default = python.pkgs.buildPythonApplication {
        #   pname = "oauthlib";
        #   version = "0.1.0";
        #   format = "setuptools";

        #   src = ./.;

        #   # True if tests
        #   doCheck = true;

        #   inherit nativeBuildInputs propagatedBuildInputs buildInputs;
        # };
      }
    );
}
