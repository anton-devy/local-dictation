#!/bin/sh
# Regenerate the English/German sanity-check fixtures using macOS's built-in `say`
# TTS voices, converted to 16kHz mono WAV. Run from anywhere; writes into this directory.
set -e
cd "$(dirname "$0")"

say -v Samantha -o english_sample.aiff "The quick brown fox jumps over the lazy dog while enjoying the morning sunshine."
say -v Anna -o german_sample.aiff "Über den Wolken müssen die Grüße größer sein, denn die Straße ist ein bisschen schön."

afconvert english_sample.aiff english_sample.wav -f WAVE -d LEI16@16000 -c 1
afconvert german_sample.aiff german_sample.wav -f WAVE -d LEI16@16000 -c 1

rm english_sample.aiff german_sample.aiff
echo "Generated english_sample.wav and german_sample.wav"
