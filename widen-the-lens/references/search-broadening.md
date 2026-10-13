# Search broadening

Use this when searching code, logs, docs, or the web and results are empty, wrong, or keep pointing to the same place.

## Table of contents
1. Why searches fail
2. Widen the query
3. Search from different angles
4. When results are too many
5. Web and documentation search

## 1. Why searches fail
- The keyword is not the word the code or docs actually use.
- The search is limited to one folder, file type, or case.
- The thing is generated, renamed, or built dynamically, so the literal text does not exist.
- The first result looked plausible, so searching stopped early.

## 2. Widen the query
Try each in turn and note which you tried:
- **Synonyms and variants**: `user` / `account` / `customer`; `delete` / `remove` / `destroy`.
- **Case and style**: `userName`, `user_name`, `UserName`, `USER_NAME`. Search case-insensitively.
- **Partial strings**: search a stable fragment of the message or name, not the full text.
- **Drop filters**: remove the folder, file-type, or date limit. Include config, tests, scripts, and docs.
- **Include hidden or generated places**: build output, vendor folders, lock files, CI config, `.env` examples.

## 3. Search from different angles
- **By error text**: search the exact error string to find where it is raised.
- **By callers**: find everything that calls the failing function, not only its definition.
- **By callees**: read what the failing function calls.
- **By tests**: tests show intended behavior and often reveal assumptions.
- **By history**: `git log -S "<text>"`, `git blame`, recent diffs, closed issues, past pull requests.
- **By similar code**: find another place that does the same job and compare line by line.
- **By data**: look at real records or sample inputs instead of the code.

## 4. When results are too many
- Add one distinguishing word at a time.
- Sort by recency or by closeness to the failing file.
- Open the top three results fully instead of skimming ten snippets.
- Write down what each result proves or does not prove before moving on.

## 5. Web and documentation search
- Search the exact error message in quotes, then without quotes.
- Add the library name and version. Old answers often do not apply to new versions.
- Prefer official docs, release notes, and the project's issue tracker over blog posts.
- Check the changelog for breaking changes around your version.
- If two sources disagree, trust the one that matches your version and test it yourself.
