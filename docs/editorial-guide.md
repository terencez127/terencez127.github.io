# Writing for *It Worked Before Lunch*

Write for the person trying to get something working, not for the agent that investigated it. Before keeping a detail, ask: **Does this help the reader decide, act, or tell whether it worked?** If it only proves how the draft was produced, leave it in the working notes.

**Open with the outcome.** Say what the reader will be able to do. Name the projects and the versions actually used once near the beginning, as test context rather than installation requirements. Say what was observed and on which platform; don't turn an earlier test into a claim about today’s release. Preserve the author’s voice. Never invent a first-person test result.

**Give the reader one working path.** Put shared prerequisites and commands in the order they’re needed. Leave out commit hashes, pinned checkouts, version-stamping flags, and version-check commands. Put links to installation instructions beside the relevant step. Use plain verbs and short code blocks. Don’t include agent names, tool transcripts, local checkout history, release approvals, or internal review checklists in the article.

**Separate choices from requirements.** Name an optional step by what it protects or enables, and say where to resume if the reader skips it. For example: “If you want only programs on this machine to reach the proxy, bind it to `127.0.0.1`. Otherwise, continue to the build step.” Keep the build command outside the optional section so either route works.

**Keep checks that change what the reader does.** Before sending a credential, it matters which service owns the port. To test memory, it matters whether a saved observation can be read back. Give the expected result and what to do if it differs. Put a short warning at the point of risk instead of appending a generic privacy disclaimer.

**End where the task ends.** Include cleanup if the reader started a service. Finish with one short line linking the projects by name to their repository roots. Don’t add a separate “Sources” section that repeats those links. Credit a specific claim or quotation where it appears.

**Final read:** Can someone skip every optional step, follow the remaining instructions, and recognize success without knowing anything about how the article was made?
