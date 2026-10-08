# Go

**Runner**: standard `go test ./...`. Coverage: `go test -cover -coverprofile=c.out ./... && go tool cover -func=c.out`. **Always run `-race`** for concurrent code: `go test -race ./...`. Flakiness: `-count=3` (also `-shuffle=on`).

## Idioms
- Table-driven tests with subtests: `for _, tc := range cases { t.Run(tc.name, func(t *testing.T){ ... }) }`; use `t.Parallel()` carefully (capture loop var on Go < 1.22).
- Compare with `cmp.Diff` (go-cmp) or `testify/require` if already used; check `errors.Is` / `errors.As` rather than string equality when errors are typed.
- Test the package's exported behavior from `package foo_test` when possible.
- Interfaces at boundaries make fakes simple: write a small hand-rolled fake rather than a heavy mock framework, unless the project uses gomock/testify mocks.
- HTTP: `net/http/httptest` for handlers and outbound servers. Time: inject a `func() time.Time` or clock interface.
- `t.Cleanup`, `t.TempDir`, `t.Setenv`.
- Fuzzing (Go 1.18+): `func FuzzXxx(f *testing.F)` for parsers/decoders; property checks with `testing/quick` or `rapid`.

## Go-specific AI failure tests
- Ignored errors (`_ = f()`), wrapped-error loss, returning `nil` error with invalid result.
- Goroutine leaks and unbuffered channel deadlocks; missing `context` cancellation; loop-variable capture.
- Nil map writes, nil pointer/interface-holding-nil-pointer gotcha, slice aliasing (`append` sharing backing arrays).
- `defer` in loops, unclosed `resp.Body`, missing `rows.Close()`.
- Integer overflow and conversion, `time.Time` comparison with `==` instead of `Equal`.

## Mutation
`go-mutesting` or `gremlins`; otherwise manual mutation pass.
