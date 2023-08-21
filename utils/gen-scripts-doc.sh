#!/bin/bash

#SCRIPTS="dt-build-dub-timings dt-build-source-audio dt-build-video dt-burn-subtitles dt-chunk-source-audio dt-cp-lang dt-duration-stats dt-export-csv dt-export-manuscript dt-export-subtitles dt-extract-wav dt-find-slides dt-gap-stats dt-import-csv dt-import-manuscript dt-import-srt dt-import-words-srt dt-mark-phrase-changed dt-rebuild-phrases dt-replace-slides dt-reset-timings dt-stt dt-translate dt-tts-duration dt-tts-natural"

#for SCRIPT in $SCRIPTS; do
#  echo $SCRIPT
#  ./help-to-asciidoc.py ../$SCRIPT > ../doc/$SCRIPT.adoc
#done

./help-to-asciidoc.py .. ../doc scripts-doc.adoc
