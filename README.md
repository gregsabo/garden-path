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
- [ ] Compress characters
- [ ] Generate 20 chapters
- [ ] Generate 20 moments for each chapter
- [ ] Generate prose for each moment
- [ ] See if we can stream output
