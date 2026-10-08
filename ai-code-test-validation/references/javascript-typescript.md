# JavaScript / TypeScript

**Runner**: detect from `package.json` (`jest`, `vitest`, `mocha`, `node:test`, `playwright` for e2e). Match existing config and file naming (`*.test.ts`, `__tests__`).
**Run**: `npm test` / `npx vitest run` / `npx jest --coverage`. Branch coverage: enable `--coverage` with `c8`/`istanbul`.

## Idioms
- Table tests: `test.each([...])('%s', ...)` / `it.each`.
- Error assertions: `expect(() => fn()).toThrow(ErrorClass)` and message; async: `await expect(p).rejects.toThrow(...)` (missing `await` makes the test pass vacuously — always await).
- Timers: `jest.useFakeTimers()` / `vi.useFakeTimers()`; fixed system time with `setSystemTime`.
- Mocks: `jest.fn()`/`vi.fn()`, `jest.spyOn`. Mock network with `msw` rather than mocking `fetch` per test. Reset mocks between tests (`restoreMocks`/`clearMocks` config).
- Prefer `toEqual`/`toStrictEqual` on full objects over `toBeTruthy`. `toStrictEqual` catches extra/undefined fields (extra-behavior failures).
- React/UI: Testing Library, query by role/label, assert user-visible behavior; avoid asserting implementation details or internal state. Simulate real events with `userEvent`.
- API: `supertest` against the app instance; assert status, headers, body shape, and side effects.

## JS/TS-specific AI failure tests
- Missing `await` / unhandled promise rejections (enable `--unhandled-rejections=strict` or fail on `unhandledRejection`).
- `==` vs `===`, falsy values (0, "", NaN), `NaN` comparisons, float math, `Array.sort` default lexicographic sort on numbers.
- Mutation of inputs/state (`push` vs spread), shallow copy issues.
- Date parsing/time zone (`new Date("2024-01-01")` is UTC), `Intl` and locale formatting.
- `any`-typed generated code: run `tsc --noEmit` (and strict mode) to catch hallucinated members before tests.
- Hallucinated npm packages/exports: verify the package exists in `package.json` and that the imported symbol exists; add one un-mocked test hitting each dependency.

## Property-based / mutation
- Property-based: `fast-check` (`fc.assert(fc.property(fc.array(fc.integer()), ...))`).
- Mutation: `npx stryker run` (config `stryker.conf.json`, set `mutate` to changed files, `testRunner` jest/vitest).

## Node back ends: Express / Fastify / NestJS
- Express/Fastify: export the `app` separately from `listen()`; test with `supertest` (`request(app).post(...)`) or Fastify `app.inject`. Assert status, headers, body, and side effects; test error middleware (thrown errors, async errors that Express 4 does not catch without a wrapper).
- NestJS: `Test.createTestingModule({ imports: [...] }).overrideProvider(Svc).useValue(fake).compile()`; for e2e, build the app with **the same global pipes/guards/filters as `main.ts`** (`app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true }))`), otherwise validation tests pass vacuously or never run. Test Guards (401/403), DTO validation (`class-validator`), interceptors, and exception filters.
- ORMs (Prisma/TypeORM/Sequelize): use a real DB (Testcontainers) for query semantics; test transactions roll back on failure.
- Schema validation (zod/joi/ajv): test invalid, missing, extra, wrong-type, and coercion cases.
- Type-level contracts (TS): `expectTypeOf` (vitest) / `tsd` for public types; run `tsc --noEmit` in CI.

## Front end: React / Vue / Angular
- React (Testing Library): query by role/label/text; use `await screen.findBy...` for async, `userEvent` (not `fireEvent`) for interactions; mock the network with `msw`, not component internals. Test loading, empty, error, and success states, and accessibility (`getByRole` failing is often a real a11y bug). Do not assert on state hooks or CSS class names.
- Hooks: `renderHook`; assert cleanup (timers, subscriptions, event listeners removed on unmount; no state update after unmount).
- Forms: validation messages, disabled submit during pending, double-submit prevention, server-error display.
- Angular: `TestBed`, `HttpTestingController` (`verify()` in `afterEach` to catch unexpected requests), `fakeAsync`/`tick`, component harnesses; test `OnPush` change detection and unsubscribed observables.
- Vue: `@vue/test-utils` + Vitest; assert emitted events and rendered output.
- E2E (few, critical flows): Playwright with role-based locators and auto-waiting; never fixed sleeps.
