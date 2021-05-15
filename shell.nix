let pkgs = import <nixpkgs> { };
in
let
  packageOverrides = pkgs.callPackage ./python-packages.nix { };
  python = pkgs.python3.override { inherit packageOverrides; };
  pythonWithPackages = python.withPackages (ps: [
    ps.quik
    pkgs.python3.pkgs.matplotlib
    pkgs.python3.pkgs.numpy
    pkgs.python3.pkgs.pandas
    pkgs.python3.pkgs.requests
  ]);
in
pkgs.mkShell {
  nativeBuildInputs = [ pythonWithPackages ];
}
