Title: A bookmark is a build test
Date: 2026-11-16 09:00
Slug: a-bookmark-is-a-build-test
Category: Showcase
Tags: publishing, pelican
Summary: A small test for a rebuilt journal: start at an old article instead of the homepage.

Start with the least impressive page on this site: [My super title]({filename}test.md), a one-sentence post from 2010. Its most useful feature is its address. Someone could have bookmarked it years ago without knowing which tool built the page, or which one would build it next.

## Start somewhere other than the front door

A new homepage can look finished while every old bookmark leads nowhere. To test a rebuild, set the homepage aside and try three ordinary reader habits:

1. Open the saved article directly. Look for its sentence, not just a successful response.
2. Follow the archive link. The old title should sit alongside the newer ones.
3. Open the site feed. A feed reader should be able to find the newest article without subscribing to a new address.

The small piece of Markdown that makes the first check possible is easy to overlook:

    Slug: my-super-post

The title is what the reader sees. The slug is what the bookmark remembers. Change the typeface, move the date, give the paragraphs more room. Leave that line alone.
