# Java Spring Boot

Read `java-kotlin.md` first for JUnit 5 / AssertJ / Mockito basics; this file adds Spring specifics.

## Contents
- Commands
- Choosing the test slice
- Controllers and validation
- Security
- Persistence (JPA) and transactions
- Migrations, config, wiring
- External calls, async, events, time
- Spring-specific AI failure modes
- Mutation testing

## Commands
- Maven: `mvn -q test`, full: `mvn -q verify`, single class: `mvn -q test -Dtest=OrderServiceTest`. Offline: add `-o`.
- Gradle: `./gradlew test --tests "*OrderServiceTest"`.
- Check Boot version (`spring-boot-starter-parent` / plugin): annotations differ (see below).

## Choosing the test slice (fastest that can prove the requirement)
| Need to prove | Use |
|---|---|
| Business rule in a service/domain class | Plain JUnit + Mockito, **no Spring context** (fastest, preferred for most rules) |
| Request mapping, status codes, validation, JSON shape, error format | `@WebMvcTest(Controller.class)` + `MockMvc` (or `MockMvcTester`, Spring 6.2+) |
| Repository queries, mappings, constraints | `@DataJpaTest` against a real DB via Testcontainers (`@ServiceConnection`, Boot 3.1+) |
| JSON (de)serialization contract | `@JsonTest` |
| Full wiring, security filter chain, transactions end to end | `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `TestRestTemplate`/`WebTestClient`; keep few |
| Outbound HTTP client | `MockRestServiceServer` or WireMock |

Bean mocking in slices: `@MockBean` (older) → `@MockitoBean` (Spring Framework 6.2 / Boot 3.4+). Use what the project already uses.
Keep at most one plain `contextLoads()` smoke test: it catches missing beans, circular dependencies, bad `@ConfigurationProperties`.

## Controllers and validation
- Assert status, `Content-Type`, exact JSON with `jsonPath`/`JsonAssert` strict mode, and headers (e.g. `Location` on 201).
- **Validation**: send invalid bodies (null, blank, too long, negative, bad enum) and assert 400 **and** the error body/field names. A missing `@Valid` / `@Validated` on the parameter silently disables all constraint annotations, a very common AI omission. Also test path/query param constraints (`@Validated` on the class).
- Test unknown fields, missing body (400), wrong content type (415), unsupported method (405), not found (404 with the agreed error format via `@ControllerAdvice`/`ProblemDetail`).
- Assert the service is called with the mapped arguments only if that mapping is the requirement; otherwise assert outcomes.
- DTO vs entity leakage: assert responses do **not** contain internal fields (password hash, internal ids, audit columns).
- Pagination: page size limits, sort whitelist, empty page, last page.

## Security (spring-security-test)
- `@WebMvcTest` does load security config for the controller if imported; use `@WithMockUser(roles=...)`, `jwt()`, `httpBasic()`; POST/PUT/DELETE need `.with(csrf())` unless CSRF is disabled by design.
- Table-test each endpoint × role: anonymous → 401, wrong role → 403, correct role → 2xx, **other tenant's/user's resource → 403/404 with no data**.
- `@PreAuthorize`/`@Secured` only works with `@EnableMethodSecurity` (or `@EnableGlobalMethodSecurity` in old versions) and when called **through the proxy** (self-invocation bypasses it). Test the annotated method via another bean.
- Assert actuator/H2-console/swagger endpoints are not exposed unauthenticated in prod profile.

## Persistence (JPA) and transactions
- Prefer real DB via Testcontainers; H2 hides dialect differences (JSON, locking, case sensitivity, sequences).
- Test-level `@Transactional` rolls back automatically **but** masks `LazyInitializationException`, flush-time constraint violations and commit-time behavior. Call `entityManager.flush(); entityManager.clear();` before asserting reads, and for commit-dependent behavior (events after commit, isolation) use a non-transactional test.
- `@Transactional` on private/final methods or self-invoked methods does nothing (proxy-based): test that a failure in step 2 rolls back step 1 through the public bean.
- Rollback rules: checked exceptions do not roll back by default; test with the exception types actually thrown.
- N+1: enable Hibernate statistics or `datasource-proxy`/`QuickPerf` and assert the query count for N=1 vs N=50.
- `equals/hashCode` on entities, cascade/orphanRemoval, optimistic locking (`@Version`): simulate two concurrent updates and expect `ObjectOptimisticLockingFailureException`.
- Unique/NOT NULL constraints exist in DB, not just annotations: assert the DB rejects duplicates.

## Migrations, config, wiring
- Use Flyway/Liquibase in tests against the real DB engine, with `spring.jpa.hibernate.ddl-auto=validate` (never `create`/`update` in tests: it hides missing migrations).
- `@ConfigurationProperties` with `@Validated`: test missing/invalid property fails startup (`ApplicationContextRunner`).
- Profiles: test prod-like profile beans (no dev-only permissive CORS, no debug endpoints).

## External calls, async, events, time
- Timeouts, retries, circuit breakers (Resilience4j): stub 500, timeout, slow response, malformed body; assert retry count and fallback, and that non-idempotent calls are not blindly retried.
- `@Async`, `@Scheduled`, event listeners: use Awaitility (`await().atMost(...)`), never `Thread.sleep`. `@TransactionalEventListener(AFTER_COMMIT)` only fires on commit: test in a non-rolled-back transaction.
- Inject `java.time.Clock` as a bean; `Clock.fixed` in tests. Assert time-zone handling (store UTC).
- Jackson: date/time format, `null` inclusion, unknown properties, enum casing, `BigDecimal` scale.

## Spring-specific AI failure modes (write a test for each that applies)
1. Missing `@Valid` → validation never runs.
2. Field injection / `new` inside a bean bypassing the container; wrong bean scope (stateful singleton with per-request data, race conditions).
3. `@Transactional` on wrong layer/visibility, or readOnly used on a writing method.
4. Returning JPA entities from controllers (lazy proxy serialization errors, data leak).
5. Broad `catch (Exception)` returning 200 or default; swallowed `@ControllerAdvice` mapping producing wrong status.
6. `Optional.get()`, `findById` result unchecked → 500 instead of 404.
7. Hard-coded secrets/URLs instead of properties; property names that do not exist (fails only at runtime).
8. Hallucinated Spring APIs / annotations from another Boot version: compile + run at least one real slice test per used feature.
9. Security config ordering (`permitAll` matcher before more specific rules), CSRF disabled globally without reason.
10. Using `@Autowired` mocks that hide a missing bean in production wiring → keep the `contextLoads` smoke test.

## Mutation testing
- PIT: `mvn org.pitest:pitest-maven:mutationCoverage -DtargetClasses="com.acme.orders.*" -DtargetTests="com.acme.orders.*"` (needs `pitest-junit5-plugin` in the plugin dependencies). Scope to the changed package: Spring-context tests are slow.
- Fallback: `scripts/mutate.py --file src/main/java/.../OrderService.java --build-cmd "mvn -q -o compile" --test-cmd "mvn -q -o test -Dtest=OrderServiceTest"`.
