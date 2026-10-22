# Framework selection and setup

Contents: selection rules · by language · machine-readable output cheat sheet · CI skeleton · cross-language tools

## Selection rules

1. Keep the project's existing runner unless it is unmaintained or blocking.
2. Choose the mainstream tool for the ecosystem (bigger community, better CI/IDE support).
3. Add the fewest dependencies that cover the strategy. One runner + one mocking approach + one E2E tool is usually enough.
4. Always configure JUnit XML + coverage output so reports can be generated.

## By language

### Python
| Need | Default | Notes |
|---|---|---|
| Unit / integration | **pytest** | `pytest-cov`, `pytest-xdist` (parallel), `pytest-randomly` (order independence), `pytest-rerunfailures` (flaky detection) |
| Mocking | `unittest.mock`, `pytest-mock`, `responses` / `respx` (HTTP) | Mock at boundaries only |
| Fixtures/data | `factory_boy`, `Faker`, pytest fixtures | |
| Property-based | `hypothesis` | Great for parsers, serializers, math |
| API | `httpx` + FastAPI `TestClient`, Django `APIClient`, Flask `test_client` | |
| DB integration | `testcontainers`, or SQLite/in-memory if schema-compatible | |
| E2E | **Playwright** (`pytest-playwright`) | |
| Mutation | `mutmut`, `cosmic-ray` | |
| Perf | `locust`, `pytest-benchmark` | |

Setup: `pip install pytest pytest-cov pytest-xdist`; configure in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers --cov=<package> --cov-report=xml:test-results/coverage.xml --junitxml=test-results/junit.xml"
markers = ["integration: needs external services", "e2e: browser tests", "smoke: critical path"]
```

### JavaScript / TypeScript
| Need | Default | Notes |
|---|---|---|
| Unit / integration | **Vitest** (Vite projects, ESM/TS-first) or **Jest** (existing/CRA/Node) | Don't mix both |
| Component | Testing Library (`@testing-library/react`, `/vue`, …) | Query by role/text, not class names |
| API | `supertest` (Express/Koa/Nest), `msw` for mocking HTTP | |
| E2E | **Playwright** (preferred) or Cypress | Playwright: multi-browser, auto-wait, parallel, trace viewer |
| Contract | Pact | |
| Mutation | Stryker | |
| Perf | k6, autocannon, Lighthouse CI | |

Jest XML: `npm i -D jest-junit` → `jest --ci --reporters=default --reporters=jest-junit --coverage --coverageReporters=lcov --coverageReporters=cobertura` (set `JEST_JUNIT_OUTPUT_DIR=test-results`).
Vitest: `vitest run --reporter=default --reporter=junit --outputFile.junit=test-results/junit.xml --coverage` (needs `@vitest/coverage-v8`).
Playwright: `reporter: [['list'], ['junit', { outputFile: 'test-results/e2e.xml' }], ['html']]` in `playwright.config.ts`; `retries: process.env.CI ? 2 : 0` helps surface flaky tests.

### Java / Kotlin
| Need | Default |
|---|---|
| Unit | JUnit 5 + AssertJ + Mockito |
| Integration | Spring Boot Test / `@DataJpaTest`, **Testcontainers** for DB/queues |
| API | REST Assured, MockMvc, WireMock |
| E2E | Playwright for Java / Selenium |
| BDD | Cucumber |
| Coverage | JaCoCo (`target/site/jacoco/jacoco.xml`) |
| Mutation | PIT (`pitest`) |
| Contract | Pact / Spring Cloud Contract |

Maven Surefire writes JUnit XML to `target/surefire-reports/`; Failsafe (`*IT.java`) for integration → `target/failsafe-reports/`. Separate unit (`mvn test`) from integration (`mvn verify`). Gradle: `build/test-results/test/*.xml`.

### Go
`testing` + `testify` (assertions), table-driven tests, `httptest`, `gomock`/`mockery`, `testcontainers-go`. Coverage: `go test ./... -coverprofile=cover.out`; convert: `gocover-cobertura < cover.out > coverage.xml`. JUnit: `go install github.com/jstemmer/go-junit-report/v2@latest` then `go test ./... -v 2>&1 | go-junit-report -set-exit-code > junit.xml`. Use `-race`. Fuzzing: native `go test -fuzz`.

### Rust
`cargo test` (unit in-module, integration in `tests/`), `proptest`, `mockall`, `wiremock`. Coverage: `cargo llvm-cov --lcov --output-path lcov.info` or `cargo tarpaulin --out Xml`. JUnit: `cargo nextest run --profile ci` (configure `junit.path`).

### C# / .NET
xUnit (or NUnit) + FluentAssertions + Moq/NSubstitute; `WebApplicationFactory` for API integration; Testcontainers; Playwright .NET. `dotnet test --logger "junit;LogFilePath=test-results/junit.xml" --collect:"XPlat Code Coverage"` (packages: `JunitXml.TestLogger`, `coverlet.collector`).

### Ruby
RSpec (+ FactoryBot, WebMock, VCR), Capybara/Playwright for E2E, SimpleCov for coverage, `rspec_junit_formatter` for XML.

### PHP
PHPUnit or Pest; Laravel's feature tests; `--log-junit test-results/junit.xml --coverage-cobertura coverage.xml`.

### Mobile
Android: JUnit + Robolectric (unit), Espresso (UI). iOS: XCTest / Swift Testing, XCUITest. Cross-platform: Detox (React Native), Maestro or Appium for E2E, Flutter `flutter test` + `integration_test`.

## Cross-language tools
- **API/contract**: Postman/Newman, Schemathesis (OpenAPI fuzzing), Pact, Dredd.
- **Load/perf**: k6, Locust, Gatling, JMeter.
- **Security**: Semgrep, Bandit (Python), `npm audit`/Snyk/Trivy (deps), OWASP ZAP (DAST). Run in CI as a separate non-flaky stage.
- **Visual regression**: Playwright screenshots, Percy, Chromatic.
- **Accessibility**: axe-core (`@axe-core/playwright`), Pa11y.
- **Test data / env**: Docker Compose or Testcontainers for services; avoid shared persistent test DBs.

## CI skeleton (GitHub Actions; adapt to the platform in use)
```yaml
name: tests
on: [push, pull_request]
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4        # or setup-python / setup-java / setup-go
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run test:unit -- --ci
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: unit-results, path: test-results/ }
  integration:
    needs: unit
    runs-on: ubuntu-latest
    services:
      postgres: { image: postgres:16, env: { POSTGRES_PASSWORD: test }, ports: ['5432:5432'] }
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run test:integration
  e2e:                                      # slower: run on main / nightly if too slow for PRs
    needs: integration
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npx playwright install --with-deps && npm run test:e2e
  report:
    needs: [unit, integration, e2e]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
      - run: python scripts/generate_report.py --junit "**/*.xml" --out test-report
```
Always upload results with `if: always()` so failures still produce artifacts.
