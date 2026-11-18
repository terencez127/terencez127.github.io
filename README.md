# Journal

Requires Python 3.12 and Make. Run `make setup` once, then `make preview` and open http://127.0.0.1:8000. Restart the preview command after editing. `make publish` builds production HTML locally; it does not upload. `make check` validates production links, legacy routes and a temporary Markdown post outside the real content directory.

## Add an article

Create `content/your-slug.md` with `Title:`, `Date:` (local Pacific time), `Category:` and a stable `Slug:` on separate lines, then a blank line and the article body. Optional: `Authors:`, `Tags:`, `Summary:`. The homepage selects the newest article. Keep published slugs and the original sample article intact. Commit the Markdown, never `build/`.

## Release gate

Pull requests build and test only. The proposed publishing branch is `master`: after cutover, merging an approved PR will deploy the generated Pages artifact. Do not push this migration or change Pages settings during local review. Before merging, obtain Terence’s separate approval, record the current public revision and actual Pages source/settings, and confirm the publishing branch. Select Actions as the Pages source and enable the repository variable `PUBLISH_JOURNAL=true` only at approved cutover. The variable gates this workflow, not legacy branch-based Pages.

Verify the deployed revision, new post, `/my-super-post.html`, stylesheet, `/feeds/all.atom.xml` and `/feeds/python.atom.xml` over HTTPS. If cutover fails, disable the variable and restore the recorded snapshot and Pages settings. The legacy `make github` and Fabric commands are not part of this flow.
