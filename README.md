[![Autopuller Tests and Linting](https://github.com/amunchet/autopuller/actions/workflows/push-backend.yml/badge.svg)](https://github.com/amunchet/autopuller/actions/workflows/push-backend.yml)

# Github Continuous Deployment (CD) Autopuller

Find yourself just larger than single dockers, but too small for Kubernetes?  Are you using `docker-compose` in production?  Are you using Github Actions but deploying on a local server?  Autopuller is for you (and me, actually). 

What does Autopuller do?  **Autopuller watches a Github Repository for changes, then pulls and restarts the local repository's docker-compose when all actions pass.**

### Required Files
- .env: this contains the login information for github

## Assumptions
- Github Actions are being used.  Passing Github actions means deployment is allowed.
- Deployment is happening in a place where a webhook can't reach (i.e. a private server)
- Linting will have a specific name and is allowed to be deployed.  This occurs when linting happens and pushes to the repository without re-running tests.
- `Autopuller` assumes your stack can be rebuilt by docker-compose.  For my case, I expect my `frontend` docker to rebuild the frontend without manual intervention if `docker-compose up --build` is run
- You're okay with having the `autopuller` docker have access to the overall docker system (needed to restart the production dockers)
