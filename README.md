# Garden Path

My experiments in generating a full-length novel with AI.

See the `/saved` directory for some example output.

The current algorithm simply generates a high-level concept, and then
re-prompts GPT-3.5 repeatedly with the last sentence of the previous
run. This persists very little context and can easily generate
texts of arbitrary length, although they are quite repetitive,
boring, and self-contradictory.

# TODO

- [x] Try pretty-printing saved XML files better
- [x] Compress characters
- [x] Generate 20 chapters
- [x] Generate 20 moments for each chapter
- [x] Figure out why resuming doesn't seem to work
- [x] Remove <prose> from schema when generating moments
- [x] Figure out why chapters are dissapearing
- [x] Include some previous moments
- [ ] Handle incomplete chapter generation.
- [ ] Generate cover and blurb
- [ ] Strip out prose except for previous
- [x] Generate prose for each moment
- [ ] See if we can stream output
