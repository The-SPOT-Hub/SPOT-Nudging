# SPOT Nudging Bot

## What it does

This bot listens for student messages requesting SPOT sessions and posts in course channels to encourage more students to join. It increases visibility of SPOT sessions so students don't have to remember to check the SPOT channel themselves.

## Architecture

This version ran on a self-managed DigitalOcean VPS:

- Flask application served via Gunicorn
- nginx as a reverse proxy with SSL via Certbot
- Self-hosted MongoDB for event logging
- Security hardening via UFW firewall and fail2ban