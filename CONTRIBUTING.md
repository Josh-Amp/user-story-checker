# Contributing to User Story Checker

Thanks for your interest in improving User Story Checker. Contributions of all sizes are welcome, from fixing a typo to proposing a new check. You don't need to be a developer to help: some of the most useful contributions are example stories the checker gets wrong.

## Ways to contribute

- **Report a wrong result.** If the checker flags a good story or misses a problem in a weak one, open an issue with the story text, its acceptance criteria, what you expected and what you got.
- **Suggest a check.** Describe the problem you see in real stories, an example of it, and how a reviewer would explain the fix.
- **Improve the docs.** Clearer wording in the README, `docs/` or the skill is always welcome.
- **Submit code.** Bug fixes, new checks and items from the [Roadmap](README.md#roadmap) are good places to start.

For anything larger than a small fix, please open an issue first so we can agree on the approach before you spend time on it.

## Setting up

Requires Python 3.10 or newer.

```bash
git clone https://github.com/Josh-Amp/user-story-checker.git
cd user-story-checker

# Only needed if you're working on the MCP server
pip3 install -r requirements.txt
```

`story_checker.py` has no dependencies and runs on its own. Only `server.py` needs the `mcp` package.

## Making a change

1. Fork the repository and create a branch from `main` with a short, descriptive name (for example `fix-only-false-positive`).
2. Make your change and add or update tests in `test_story_checker.py`.
3. Run the tests:

```bash
   python3 test_story_checker.py
```

4. Try your change against the sample stories:

```bash
   python3 story_checker.py sample_stories.json
   python3 story_checker.py sample_stories.json --markdown
```

5. Update the docs that your change touches (see the checklist below).
6. Add a line to `CHANGELOG.md` describing the change.
7. Open a pull request against `main`. GitHub Actions runs the tests on every push, and they must pass before a change is merged.

## Checklist by type of change

**Changing a scoring rule or check**

- Keep `story_checker.py` free of third-party dependencies.
- Update `docs/scoring.md` so the documented rules match the code.
- If the points, the Ready threshold or a flag changes, update the tables in `README.md`.
- Add tests for a story that should trigger the check and one that shouldn't. False positives matter as much as misses.
- Mark a finding as a **problem** only if it should stop a story being Ready. Otherwise make it **advice**.

**Changing the MCP server**

- Keep the tool names (`check_story`, `check_backlog`, `review_story`) and their inputs and outputs stable. If a change would break existing callers, raise it in an issue first.
- Update the "Tools the server provides" table in `README.md` and `docs/architecture.md` if a response changes shape.
- Check that the server still works with the `mcp` versions listed under Compatibility in the README.

**Changing the Claude skill**

- Edit `skill/story-readiness/SKILL.md`, then rebuild the zip from inside the `skill` folder:

```bash
  cd skill
  zip -X -r ../story-readiness.zip story-readiness
```

- Commit both files together. A test fails if `SKILL.md` and `story-readiness.zip` drift apart.
- Keep the review sections in the same order as the tool's review (Verdict, story as submitted, Scorecard, Part by part, Going forward).

**Changing the vague-word list**

- Explain in the pull request why the word is vague in user stories, and give an example.
- Note any legitimate uses it might flag (for example a feature name), and add a test if you can.

## Writing style

The project is for business analysts, product owners and developers alike, so the docs and the review output use plain language:

- Write short sentences in the active voice.
- Explain terms like INVEST, Gherkin or MCP the first time they appear.
- Make every finding say what's wrong, why it matters and how to fix it.
- Use the same terms the code uses: Ready, Needs work, problem, advice, role, want, benefit, acceptance criteria.

## Code style

- Follow [PEP 8](https://peps.python.org/pep-0008/) and keep functions small and named for what they check.
- Prefer clear code over clever code. Someone who knows business analysis better than Python should be able to follow a rule.
- Add a short docstring to any new check that says what it flags and why.

## Commit messages

Start with a short summary line in the imperative mood (for example "Add check for criteria with no measurable value"). Add more detail in the body if it helps.

## Code of conduct

Be respectful and constructive. Critique stories and code, not people. Harassment and discriminatory language aren't tolerated in issues, pull requests or any other project space.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
