> **⚠️ INACTIVE — This repository is no longer the active automation.**
>
> This automation has moved to AWS as of 6/15/26. The current, active repository is **[SPOT-Nudging-Serverless](https://github.com/The-SPOT-Hub/SPOT-Nudging-Serverless)**.
>
> This repo is kept for historical reference.
>
> The logic itself is unchanged — only the infrastructure that invokes it has moved.
 
---

# SPOT Nudging Bot

## What it does

This bot listens for student messages requesting SPOT sessions and posts in course channels to encourage more students to join. It increases visibility of SPOT sessions so students don't have to remember to check the SPOT channel themselves.

## Architecture

This version ran on a self-managed DigitalOcean VPS:

- Flask application served via Gunicorn
- nginx as a reverse proxy with SSL via Certbot
- Self-hosted MongoDB for event logging
- Security hardening via UFW firewall and fail2ban