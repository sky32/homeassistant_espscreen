# Han frequency ranking source

`han_frequency.txt` contains the 2,500 highest-scoring Han characters derived from the `zh` large word list in `wordfreq` 3.1.1. The ranking adds each word's estimated corpus frequency to each Han character it contains. The generator retains screen-translation characters and explicit room-label characters in addition to this list.

`wordfreq` is Copyright 2022 Robyn Speer and licensed under Apache License 2.0. Its frequency data is compiled by the Exquisite Corpus from multiple sources, including Wikipedia, NewsCrawl, Google Books Ngrams, OSCAR, Reddit, Twitter, SUBTLEX-CH and OPUS OpenSubtitles 2018. OPUS OpenSubtitles data requires attribution to the OpenSubtitles project: https://www.opensubtitles.org/ . See the wordfreq metadata for the full source list and notices: https://pypi.org/project/wordfreq/ .

The Han codepoint ranking is a derived selection list. It does not contain the source words or corpus text. Rebuild it with wordfreq 3.1.1 and the procedure described in `tools/build_han_font.py` when refreshing the font.