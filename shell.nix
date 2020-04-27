# Run nix-shell without arguments to enter an environment with all the
# project dependencies in place.
{
  pkgs ? import (builtins.fetchGit {
    url = "https://github.com/NixOS/nixpkgs-channels/";
    ref = "nixos-20.03";
  }) {}
}:

pkgs.mkShell {
  venvDir = "./venv";
  buildInputs = with pkgs; [
    git
    python36
    python36Packages.venvShellHook
  ];
  postShellHook = ''
    unset SOURCE_DATE_EPOCH
    pip install -e .\[dev,test\]
    pre-commit install
  '';
}
