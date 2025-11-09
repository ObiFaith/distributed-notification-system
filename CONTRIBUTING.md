# Contributing to Distributed Notification System

Thank you for considering contributing to Distributed Notification System! We welcome all kinds of contributions, including bug reports, feature requests, and code improvements.

## Table of Contents

- [Contributing to Distributed Notification System](#contributing-to-distributed-notification-system)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [1. Prerequisites](#1-prerequisites)
    - [2. Clone the Repository](#2-clone-the-repository)
    - [3. Environment Setup](#3-environment-setup)
    - [4. Start the Services](#4-start-the-services)
  - [How to Contribute](#how-to-contribute)
    - [Reporting Bugs](#reporting-bugs)
    - [Suggesting Features](#suggesting-features)
    - [Code Contributions](#code-contributions)
      - [Development Workflow](#development-workflow)
        - [Branch Naming Rules](#branch-naming-rules)
        - [Commit Message Rules](#commit-message-rules)
      - [Submitting Pull Requests](#submitting-pull-requests)
  - [Code of Conduct](#code-of-conduct)
  - [License](#license)

## Getting Started

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Node.js](https://nodejs.org/) (for NestJS services)
- [Python](https://www.python.org/downloads/) (for Flask & FastAPI services)
- [RabbitMQ Management UI](https://www.rabbitmq.com/management.html) _(optional)_

### 2. Clone the Repository

```bash
git clone https://github.com/ObiFaith/distributed-notification-system.git

cd distributed-notification-system
```

> Each developer should now navigate into their assigned service folder before making any changes.

**For example**:

```sh
cd services/api_gateway      # FastAPI developer
cd services/user_service     # Flask developer
cd services/template_service # Flask developer
cd services/email_service    # NestJS developer
cd services/push_service     # NestJS developer
```

> This ensures isolation and prevents cross-service conflicts in the mono-repo.

### 3. Environment Setup

Each service may also contain its own `.env.example` file with service-specific variables.

Duplicate `.env.example` into `.env` and configure:

```sh
cp .env.example .env
```

### 4. Start the Services

To build and start all containers (RabbitMQ, Traefik, services, monitoring):

```sh
docker-compose up --build
```

---

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on [GitHub Issues](https://github.com/ObiFaith/distributed-notification-system/issues) and include as much detail as possible. Provide steps to reproduce, expected and actual behavior, and any relevant logs.

### Suggesting Features

If you have an idea for a new feature, please open an issue on [GitHub Issues](https://github.com/ObiFaith/distributed-notification-system/issues) and describe your proposal. Explain why the feature would be useful and how it should work.

### Code Contributions

> Please make sure to have created a fork of the original repository. This is where you will work in when contributing.

#### Development Workflow

1. Create a new branch for your work:
   ```sh
   git checkout -b feat/DNS-2145-your-feature-name
   ```
   ##### Branch Naming Rules
   - You will likely work on features, bug fixes, refactors (restructuring code without changing functionality), chores on the repo (routine tasks such as updating dependencies or changing configurations), or documentation. Each of the type of update should be used as a prefix your branch name as `feat/`, `refactor/`, `fix/`, `chore/`, or `docs/`
   - For any of these updates, you will likely use a ticket or an issue. The ticket number, e.g. DNS-2145 or issue number should also be included in your branch name
   - Finally, a short description for your update should follow suit. This is often taken from the ticket title
   - All of this (except the ticket number acronym, `DNS`) should be written in lowercase
     > Thus, a typical branch should look like `feat/DNS-1234-create-login-page` or like `chore/remove-unused-variables` if your update has no corresponding ticket or issue (unlikely)
2. Make your changes, and commit them with descriptive messages:

   ```sh
   git commit -m "feat: your commit message"
   ```

   ##### Commit Message Rules

   Commit messages also follow a similar pattern. However, there is no need to add ticket number since they can be easily tracked given the branch name. Instead, use a colon, `:`, after the type of change (`feat`, `fix`, etc.), a whitespace, then your commit message. In cases where you are required to add the ticket number, you may use a the parenthesis after the type of change, like `feat(DNS-1234): your commit message`

   > Another example: `refactor: use a single state for formData` or `refactor(DNS-1234): use a single state for formData`

   > Please notice how both branch names an commit messages use the imperative tense. The imperative tense is a command or request, which makes it clear what the commit does. i.e., "fix login issue", NOT "I fixed login issue", and NOT "fixed login issue"

3. Push your branch to your forked repository:
   ```sh
   git push origin <your-branch>
   ```

#### Submitting Pull Requests

1. Ensure your branch is up to date with your remote repository:
   ```sh
   git checkout dev
   git pull origin dev
   git checkout <your-branch>
   git rebase dev
   ```
   > You should regularly update your remote repository with changes from the [default branch of the] upstream repository
2. Submit a pull request from your branch to the upstream repository.
3. In your pull request description, explain what changes you made and why.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to [email@example.com].

## License

By contributing, you agree that your contributions will be licensed under the [Apache License](LICENSE).
