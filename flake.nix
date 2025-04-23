{
  description = "indie-oidc-provider";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        # pkgs = nixpkgs.legacyPackages.${system};
        overlays = [ ];
        pkgs = import nixpkgs { inherit system overlays; };
        python = pkgs.python;

        nativeBuildInputs =
          with pkgs;
          [
            python313
            jq
            openssl
            pkg-config
          ]
          ++ (with pkgs.python313Packages; [
            requests
            pyjwt
            jwcrypto
            cryptography
            ipython
            pudb
            pyopenssl
            sqlite

            setuptools
            setuptools-scm
            pytest
            pytest-cov
            flit
          ]);
        propagatedBuildInputs = with pkgs.python313Packages; [
          noiseprotocol
          flask
          flask-sqlalchemy
          authlib
          cryptography
        ];

        buildInputs =
          with pkgs;
          [
            openssl
            pkg-config
          ]
          ++ (with pkgs.python313Packages; [ cryptography ]);
      in
      {
        devShells.default = pkgs.mkShell { inherit nativeBuildInputs propagatedBuildInputs buildInputs; };
        packages.default = pkgs.python313Packages.buildPythonApplication {
          pname = "indie-oidc-provider";
          version = "0.1.0";
          pyproject = true;
          # format = "setuptools";

          src = ./.;

          # There are no tests in the example OIDC provider
          doCheck = false;

          # installPhase = ''
          #   mkdir $out
          #   wrapProgram ${pkgs.python313Packages.flask}
          # '';

          inherit nativeBuildInputs propagatedBuildInputs buildInputs;
        };
      }
    );
}
