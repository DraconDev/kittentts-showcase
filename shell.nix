{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python312
    stdenv.cc.cc.lib
    zlib
    glib
    libsndfile
    espeak-ng
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:${pkgs.glib.out}/lib:${pkgs.libsndfile.out}/lib:$LD_LIBRARY_PATH"
    
    if [ -f /home/dracon/Dev/kitten/.venv/bin/activate ]; then
        source /home/dracon/Dev/kitten/.venv/bin/activate
    fi
    
    echo "KittenTTS environment ready!"
  '';
}
