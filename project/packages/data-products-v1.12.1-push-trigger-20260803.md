# Data Products v1.12.1 Registered Push Trigger

Date: 2026-08-03

## Purpose

Trigger the already registered one-time Data Products v1.12.1 push publisher with a separate merge after the publisher workflow became part of `main`.

The preceding bridge merge installed the bounded `push` trigger but could not trigger newly registered workflow logic with the same push event. This package changes no source data, release assets, report semantics or publication contract. Its only purpose is to generate a subsequent merge push whose commit message activates the registered publisher.

The publisher remains responsible for exact-source double build, byte-identity verification, offline workspace verification, immutable release creation, public-download verification, receipt recording and removal of all temporary publication files.
