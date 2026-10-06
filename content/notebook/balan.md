---
title: balan
publish: true
description: The Google OAuth app behind my homelab's Google integrations — what it
  touches, and where that data goes. Doubles as its privacy policy.
tags:
- homelab
created: 2026-10-05
---

# balan

balan is a personal Google OAuth app. It connects my own devices and agents to my own Google
account. I am its only user. It isn't a product, nobody else can sign up, and if a consent screen
sent you here, it was mine.

Google requires a home page and a privacy policy before an app like this can leave testing mode.
This page is both.

## what it does

- **Balance board → Google Health.** My [Wii Balance Board](wii-balance-board-scroller)
  writes weight readings to my own Google Health record. It can only write measurements, not read
  anything back.
- **A homelab agent's view of my Google account.** An assistant running on my own hardware can:
  - read my Gmail and create drafts. **It cannot send.** The Google credential is held by a
    small separate service that has no send function, so sending isn't available even in
    principle.
  - read my Google Drive, and edit only files it created itself or that I hand it one at a
    time through Google's file picker.
  - read my Google Calendar.

## where the data goes

- **Stored on my own machines.** Credentials and anything fetched from Google live on hardware
  I own, in my home. No third-party database, no analytics, no ads.
- **Processed by language models.** To summarise or draft, the agent sends the relevant text to
  hosted model APIs (through OpenRouter, to providers such as Anthropic and DeepSeek). That is
  the only place data leaves my hardware, and only the parts a task needs.
- **Never sold, shared, or used to train models.** Use of data from Google APIs follows the
  [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy),
  including its Limited Use requirements.

## revoking it

I can revoke balan's access at any time from
[Google Account → Third-party connections](https://myaccount.google.com/connections), and so could
anyone else who somehow authorised it. Deleting the local credentials ends access as well.

Questions: the contact address on the consent screen reaches me.
