[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)


# Notebooks Deploy

## Setup

1. Clone the notebooks-deploy repository from GitHub using `git clone https://github.com/LabShare/notebooks-deploy`.
1. Install package dependencies using `npm i`.

## Development
### Running JupyterHub Locally
1. Create an .env file in your working directory. See the [sample-env](./sample-env) for an example. Docker-compose uses these environment variables to populate image and container arguments and environment variables. 
1. Build docker images using `npm run build`.
1. Start JupyterHub on `localhost:8000` using `npm start`.
1. JupyterHub is setup with DummyAuthenticator by default. Use any username or password to login.
1. To stop the running deployment use `npm run stop`.

## Deployment
### Kubernetes
1. Create a `.env` file in the root of the repository, using `sample-env` as an example.
1. Configure `kubectl` with a `kubeconfig` pointing to the correct Kubernetes cluster. Optionally, pass the location of the `kubeconfig` file in the `.env`. This value defaults to the standard `kubeconfig` location. 
1. Run the script using: `./deploy.sh`.