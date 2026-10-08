# Java / Kotlin

**Runner**: JUnit 5 (Jupiter) by default; check for JUnit 4, TestNG, Kotest/Spek. Build: Maven (`mvn -q test`) or Gradle (`./gradlew test`).
**Coverage**: JaCoCo (`mvn verify` with jacoco plugin / `./gradlew jacocoTestReport`), check branch coverage.

## Idioms
- `@ParameterizedTest` with `@CsvSource`/`@MethodSource` for boundaries and decision tables.
- Assertions: AssertJ (`assertThat(x).isEqualTo(...)`, `assertThatThrownBy(...).isInstanceOf(...).hasMessageContaining(...)`) if present; else JUnit `assertThrows`.
- Mockito: `@Mock`, `@InjectMocks`; use `verify` only when the interaction is the requirement; use `verifyNoMoreInteractions` for "must not call" rules. Prefer real objects for domain classes.
- Time: inject `java.time.Clock` (`Clock.fixed`); avoid `LocalDate.now()` in tests.
- Spring: `@WebMvcTest` + `MockMvc` for controllers (slice), `@DataJpaTest` for repositories, `@SpringBootTest` sparingly. Use Testcontainers for real DB behavior.
- BigDecimal: compare with `compareTo`/AssertJ `isEqualByComparingTo`, and test scale/rounding mode explicitly.

## Java-specific AI failure tests
- `equals`/`hashCode` contract (EqualsVerifier), mutable fields in value objects.
- `null` handling, `Optional.get()` without check, unchecked casts.
- Resource leaks: try-with-resources; assert close on failure path.
- Concurrency: shared mutable state, non-thread-safe collections; run concurrent tests repeatedly (`@RepeatedTest`).
- Integer overflow, `int` vs `long`, integer division, `==` on strings/boxed types.
- Transaction boundaries: failure mid-operation rolls back.

## Property-based / mutation
- jqwik (`@Property`) for property tests.
- Mutation: PIT — `mvn org.pitest:pitest-maven:mutationCoverage` or Gradle pitest plugin; limit with `targetClasses`.
