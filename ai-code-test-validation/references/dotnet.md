# .NET (C# / F#)

**Runner**: xUnit (common), NUnit, or MSTest — match the project. Run `dotnet test`; coverage `dotnet test --collect:"XPlat Code Coverage"` (coverlet).

## Idioms
- xUnit `[Theory]` + `[InlineData]`/`[MemberData]` for tables and boundaries.
- Assertions: FluentAssertions or Shouldly if present; else xUnit `Assert.Throws<T>` / `Assert.ThrowsAsync<T>` and check messages.
- Mocking: Moq / NSubstitute at boundaries only. Use `MockBehavior.Strict` where unexpected calls should fail the test.
- Time: inject `TimeProvider` (.NET 8+) or `ISystemClock`; `FakeTimeProvider` in tests.
- ASP.NET Core: `WebApplicationFactory<T>` for integration tests; assert status codes, problem-details bodies, auth (401/403).
- EF Core: SQLite in-memory is not equivalent to SQL Server for some behavior; use Testcontainers when query semantics matter.
- `decimal` for money; assert rounding (`MidpointRounding`) explicitly.

## .NET-specific AI failure tests
- `async void`, missing `await`, `.Result`/`.Wait()` deadlocks, unobserved task exceptions.
- `DateTime` vs `DateTimeOffset`, `DateTime.Now` vs `UtcNow`, culture-sensitive parsing/formatting (test with `CultureInfo.InvariantCulture` and a non-English culture).
- `IDisposable` not disposed; `IEnumerable` multiple enumeration; deferred LINQ execution surprises.
- Nullable reference handling (enable `<Nullable>`; test null inputs).

## Property-based / mutation
- FsCheck (`Prop.ForAll`, or FsCheck.Xunit `[Property]`).
- Mutation: Stryker.NET — `dotnet stryker` from the test project dir.

## ASP.NET Core specifics
- **Integration**: `WebApplicationFactory<Program>` (expose `public partial class Program {}` for minimal APIs); override services in `ConfigureTestServices` (replace `DbContext`, external clients, `TimeProvider`). Use Testcontainers (`Testcontainers.MsSql`/`PostgreSql`) for real query semantics.
- **`[ApiController]`** auto-returns 400 for invalid `ModelState`; without it, missing `ModelState.IsValid` checks let bad data through. Minimal APIs need explicit validation (FluentValidation / endpoint filters): test invalid bodies for 400/422 and the ProblemDetails shape.
- **Auth**: register a test authentication handler (`AddAuthentication("Test").AddScheme<...>`) with configurable claims; table-test endpoint × role/policy: anonymous 401, wrong role/policy 403, other tenant's resource 403/404. Check `[Authorize]` is actually present on new endpoints (reflection test for controllers missing it is a cheap guard).
- **DI lifetimes**: enable `ValidateScopes` / `ValidateOnBuild` in a test host to catch scoped-in-singleton and missing registrations; keep one host-builds smoke test.
- **EF Core**: assert `SaveChangesAsync` actually called, no tracking surprises (`AsNoTracking` writes lost), N+1 via logging/interceptor counting, migrations apply (`Database.MigrateAsync`) on the real engine, concurrency tokens (`DbUpdateConcurrencyException`).
- **HttpClient**: use `IHttpClientFactory` with a stub `HttpMessageHandler`; test timeouts, non-2xx, malformed JSON, and Polly retry/circuit behavior (with fake time).
- **Serialization**: `System.Text.Json` defaults (camelCase, enum as number, case-sensitive) vs Newtonsoft; assert the public contract; test `DateTimeOffset` and `decimal` handling.
- **Logging**: `FakeLogger<T>` (Microsoft.Extensions.Diagnostics.Testing) to assert error logging without leaking secrets.
- **Async**: `ConfigureAwait`, cancellation tokens honored (pass a cancelled token, expect `OperationCanceledException`), no `.Result`.
- Mutation: `dotnet tool install -g dotnet-stryker` then `dotnet stryker` in the test project; fallback `scripts/mutate.py --build-cmd "dotnet build -nologo -v q" --test-cmd "dotnet test --no-build -nologo -v q"` (omit `--no-build` if the test project must rebuild).
