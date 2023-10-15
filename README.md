# Garden Path

My experiments in generating a full-length novel with AI.

See the `/saved` directory for some example output.

The current algorithm simply generates a high-level concept, and then
re-prompts GPT-3.5 repeatedly with the last sentence of the previous
run. This persists very little context and can easily generate
texts of arbitrary length, although they are quite repetitive,
boring, and self-contradictory.
