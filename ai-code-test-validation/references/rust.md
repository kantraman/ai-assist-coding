# Rust

**Runner**: `cargo test` (unit tests in `#[cfg(test)] mod tests` beside code; integration tests in `tests/`). Coverage: `cargo llvm-cov` or `cargo tarpaulin`. Lint: `cargo clippy -- -D warnings`.

## Idioms
- Table tests via arrays of tuples and loops (include the case name in the assert message), or `rstest` if used.
- `assert_eq!` with informative messages; `#[should_panic(expected = "...")]` includes the message; prefer returning `Result` and asserting `Err(SpecificVariant)`.
- Traits at boundaries for fakes; `mockall` if the project uses it. Use `tempfile` for FS, inject time.
- Doc tests (`///` examples) are executed — add them for public API contracts.
- Property tests: `proptest` or `quickcheck`. Fuzz: `cargo fuzz` for parsers.

## Rust-specific AI failure tests
- `unwrap()`/`expect()` on fallible input paths → test that bad input returns `Err`, not panic.
- Integer overflow (debug panics vs release wrapping): test with `checked_*`, boundary values, and run tests in `--release` too.
- Off-by-one on slices/indices, UTF-8 boundary slicing on `str`.
- Blocking calls in async code; `Send`/`Sync` misuse; deadlocks with `Mutex` ordering.
- `unsafe` blocks: require a test per invariant; run under Miri where feasible (`cargo +nightly miri test`).

## Mutation
`cargo mutants` (then inspect `mutants.out/missed.txt`).
