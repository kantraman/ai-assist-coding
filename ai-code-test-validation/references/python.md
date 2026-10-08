# Python

**Runner**: pytest (default if present); else `unittest`. Check `pyproject.toml`, `pytest.ini`, `tox.ini`, `conftest.py`.
**Run**: `pytest -q`, with coverage: `pytest --cov=<pkg> --cov-branch --cov-report=term-missing`.
**Random order/flakiness**: `pytest -p no:randomly` off; try `pytest-randomly` or run 3x.

## Idioms
- Parametrize for boundaries and decision tables: `@pytest.mark.parametrize("total,expected", [(99.99, 0), (100, 10)])`.
- Error assertions: `with pytest.raises(ValueError, match="negative"):` — always check type and message.
- Time: `freezegun` / `time-machine`, or inject a clock. Randomness: seed or inject.
- Fixtures for setup; `tmp_path` for files; `monkeypatch` for env/attrs.
- Mocking: `unittest.mock.patch` at the **point of use** (`patch("app.service.requests.get")`). Use `autospec=True` / `create_autospec` so calls to non-existent methods or wrong signatures fail. This directly catches hallucinated APIs.
- Money: assert with `Decimal`, never float equality; use `pytest.approx` only for genuine floats.
- Async: `pytest-asyncio` / `anyio`; ensure coroutines are awaited.
- HTTP APIs: FastAPI/Flask/Django test clients; `responses`/`respx`/`httpx.MockTransport` for outbound calls.
- DB: transaction-rollback fixtures or SQLite in-memory only if the dialect matches; otherwise testcontainers.

## Python-specific AI failure tests
- Mutable default arguments: call function twice, assert independence.
- Bare `except:` / `except Exception: pass`: make the dependency raise and assert propagation.
- Truthiness bugs (`if not value` treating 0 or "" as missing): test 0, "", [] explicitly.
- `is` vs `==`, integer division `/` vs `//`, string/bytes confusion, naive vs aware datetimes.
- Iterator exhaustion (generator consumed twice).

## Property-based / mutation
- Hypothesis: `@given(st.lists(st.integers()))`; add `@settings(max_examples=200)`; commit failing examples via `@example`.
- Mutation: `mutmut run` (then `mutmut results`, `mutmut show <id>`) or `cosmic-ray`. Scope to the changed module to keep runtime sane.
- Type/API sanity: `mypy`/`pyright` on generated code catches many hallucinated attributes before tests even run.

## Web frameworks
- **FastAPI**: `TestClient(app)` / `httpx.AsyncClient(transport=ASGITransport(app))`; swap dependencies with `app.dependency_overrides[get_db] = fake` (and clear it after). Test pydantic validation (422 body), response_model filtering (no leaked fields), auth dependencies (401/403), background tasks.
- **Django/DRF**: `TestCase` (transaction-wrapped) vs `TransactionTestCase` (needed for `on_commit` hooks); `self.assertNumQueries(n)` for N+1; `APIClient` with `force_authenticate`; check permissions per role and object-level permissions; `python manage.py makemigrations --check --dry-run` to catch missing migrations; test serializers' validation and `read_only`/`write_only` fields.
- **Flask**: `app.test_client()`, app factory with a test config; test error handlers and `before_request` hooks.
- **SQLAlchemy**: real DB or matching dialect; test rollback on failure, lazy-load in closed session, `session.commit()` missing after write (data not persisted).
- **Celery/queues**: eager mode for logic, but also test idempotency and retry behavior separately.
- **Pydantic v2**: `model_validate` with bad data; check `extra="forbid"` where extra fields must be rejected; strict vs lax coercion (`"5"` → 5).
