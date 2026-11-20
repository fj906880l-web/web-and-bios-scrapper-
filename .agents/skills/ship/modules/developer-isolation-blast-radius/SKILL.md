---
name: developer-isolation-blast-radius
description: Enterprise security standard (SEC-PROTO-2026-04 v2.4) for Full-Stack Developer Isolation and Blast-Radius Mitigation. Provides dev container hardening (.devcontainer/devcontainer.json), microVM sandbox isolation (Docker Sandbox/Lima), egress network filtering (iptables/UFW), and 4-tier incident response containment for executing untrusted third-party code and transitive dependencies.
version: 2.4.0
---

# Full-Stack Developer Isolation & Blast-Radius Mitigation (SEC-PROTO-2026-04 v2.4)

Master operational guide and automation skill for zero-blast-radius execution of untrusted code, build processes (`npm install`, `pip install`, `cargo build`), and isolated development environments.

## Threat Model: Single-Command Host Takeover
Arbitrary zero-privilege scripts executed in default host developer environments can instantaneously exfiltrate:
1. Browser session cookies & local storage (Chrome, Firefox, Safari, Slack, Discord).
2. SSH private keys (`~/.ssh/id_rsa`, `~/.ssh/id_ed25519`).
3. Package registry tokens (`~/.npmrc`, `~/.pypirc`).
4. Master environment variables and cloud provider credentials (`~/.aws/credentials`, `~/.kube/config`).

## The 4 Fundamental Architectural Security Pillars
1. **Principle of Least Privilege (PoLP)**: Scoped directory mounts (mount only active repo, never `$HOME` or root `/`). Ephemeral read-only SSH agent socket (`${localEnv:SSH_AUTH_SOCK}:/tmp/ssh-agent.sock:ro`), NEVER private keys.
2. **Egress & Network Filtering**: Outbound network restrictions strictly allowlisting package registries (`registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`) and DNS (`1.1.1.1:53`). Arbitrary TCP/UDP blocked.
3. **Ephemeral Runtimes**: Disposable containers and MicroVMs torn down immediately upon task completion. Zero state persistence.
4. **Defense in Depth**: MicroVMs + non-root execution (`developer` UID 1000) + `--cap-drop=ALL` + `--security-opt=no-new-privileges:true` + `--pids-limit=200` + seccomp profiles.

## Tiered Isolation Ladder

| Tier Level | Tooling Ecosystem | Security Boundary | Recommended Use Case |
| :--- | :--- | :--- | :--- |
| **Level 1: Containers** | Docker, Dev Containers, Podman | Host OS Kernel sharing, filesystem isolation | Standard internal repos, trusted code. |
| **Level 2: MicroVMs** | Docker Sandbox, Lima, Colima, UTM | Dedicated virtual CPU, RAM, & Kernel | Untrusted 3rd-party repos, untested packages. |
| **Level 3: Cloud Workspaces** | GitHub Codespaces, Coder.com, VPS | Complete network & hardware separation | External vendor audits, client repos. |
| **Level 4: Secondary Hardware** | Air-Gapped Laptop (CachyOS/ThinkPad) | Physical segregation from personal data | Dedicated work-only, proprietary IP sandboxing. |
| **Level 5: Maximum Hardening** | Tails OS, Live USB Ubuntu, Air-Gapped | Zero memory persistence across reboots | Malware analysis, cryptographic audits. |

## Production Blueprint Files

### 1. Hardened `.devcontainer/devcontainer.json`
```json
{
  "name": "Hardened Full-Stack Isolation Workspace",
  "dockerFile": "Dockerfile",
  "remoteUser": "developer",
  "workspaceFolder": "/workspace",
  "workspaceMount": "source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=cached",
  "mounts": [
    "source=${localEnv:SSH_AUTH_SOCK},target=/tmp/ssh-agent.sock,type=bind,readonly"
  ],
  "containerEnv": {
    "SSH_AUTH_SOCK": "/tmp/ssh-agent.sock",
    "NODE_ENV": "development"
  },
  "runArgs": [
    "--cap-drop=ALL",
    "--security-opt=no-new-privileges:true",
    "--pids-limit=200",
    "--memory=4g",
    "--cpus=2.0"
  ],
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode"
      ]
    }
  }
}
```

### 2. Rootless `Dockerfile`
```dockerfile
FROM alpine:latest
RUN apk add --no-cache bash git curl nodejs npm python3 py3-pip shadow \
    && useradd -m -u 1000 -s /bin/bash developer
WORKDIR /workspace
USER developer
```

### 3. Strict `.devcontainer/.dockerignore`
```dockerignore
**/.git
**/.env*
**/.ssh
**/.aws
**/.kube
**/.npmrc
**/.pypirc
**/node_modules
```

## Egress Firewall Lockdown
```bash
# Execute via scripts/egress_lockdown.sh
docker network create --subnet=172.28.0.0/16 isolated-dev-net
iptables -I DOCKER-USER -s 172.28.0.0/16 -d 1.1.1.1 -p udp --dport 53 -j ACCEPT
iptables -I DOCKER-USER -s 172.28.0.0/16 -d registry.npmjs.org -p tcp --dport 443 -j ACCEPT
iptables -I DOCKER-USER -s 172.28.0.0/16 -d pypi.org -p tcp --dport 443 -j ACCEPT
iptables -I DOCKER-USER -s 172.28.0.0/16 -d files.pythonhosted.org -p tcp --dport 443 -j ACCEPT
iptables -A DOCKER-USER -s 172.28.0.0/16 -j DROP
```

## Incident Response & Containment (Dependency Poisoning)
- **P1 - CRITICAL**: Revoke all npm, PyPI, GitHub, AWS/GCP/Azure access tokens immediately.
- **P1 - CRITICAL**: Rotate all SSH keys associated with GitHub, GitLab, and remote production servers.
- **P2 - HIGH**: Force-terminate active browser and application sessions (Google, Slack, Discord, 1Password).
- **P3 - MEDIUM**: Extract container logs for forensic analysis and destroy contaminated sandbox instance.
