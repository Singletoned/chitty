- These signal a property:
  - structured input giving structured output;
  - a pair that undoes each other (parse and format, export and import): the
    round trip gives back the input;
  - an old implementation to match (refactor, optimise, "replace X with Y"):
    the new one gives the same results;
  - safe to repeat (retry, dedupe, normalise): doing it twice equals once;
  - order or grouping must not matter (batching, pages, merge);
  - nothing lost or made (split, partition, move): counts and totals match;
  - claims over a set of inputs or states: all, every, each, any, always,
    never, except, unless, unique, sorted, at most;
  - open inputs: free text, Unicode, dates and time zones, paths, user files,
    nested data;
  - parsers and validators: any input gives a result or a clear error, never
    a crash;
  - status changes and sequences of operations that must keep a rule;
  - limits: results stay in a range, or more input never gives less output;
  - a bug in an edge case (empty, zero, duplicate, boundary): the examples
    missed part of the inputs.
