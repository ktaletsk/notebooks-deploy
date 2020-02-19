pipeline {
    agent {
        node { label 'aws && ci && linux && polus' }
    }
    parameters {
        booleanParam(name: 'SKIP_BUILD', defaultValue: false, description: 'Skips Docker builds')
	string(name: 'AWS_REGION', defaultValue: 'us-east-1', description: 'AWS Region to deploy')
	string(name: 'KUBERNETES_CLUSTER_NAME', defaultValue: 'kube-eks-ci-compute', description: 'Kubernetes Cluster to deploy')
    }
    environment {
        PROJECT_NAME = "labshare/notebooks-deploy"
        DOCKER_CLI_EXPERIMENTAL = "enabled"
        BUILD_HUB = """${sh (
            script: "git diff --name-only ${GIT_PREVIOUS_SUCCESSFUL_COMMIT} ${GIT_COMMIT} | grep 'jupyterhub/VERSION'",
            returnStatus: true
        )}"""
        BUILD_NOTEBOOK = """${sh (
            script: "git diff --name-only ${GIT_PREVIOUS_SUCCESSFUL_COMMIT} ${GIT_COMMIT} | grep 'notebook/VERSION'",
            returnStatus: true
        )}"""
        BUILD_DOCS = """${sh (
            script: "git diff --name-only ${GIT_PREVIOUS_SUCCESSFUL_COMMIT} ${GIT_COMMIT} | grep 'docs/VERSION'",
            returnStatus: true
        )}"""
        HUB_VERSION = readFile(file: 'deploy/docker/jupyterhub/VERSION')
        NOTEBOOK_VERSION = readFile(file: 'deploy/docker/notebook/VERSION')
        DOCS_VERSION = readFile(file: 'deploy/docker/docs/VERSION')
        WIPP_STORAGE_PVC = "wipp-pv-claim"
    }
    triggers {
        pollSCM('H/5 * * * *')
    }
    stages {
        stage('Build Version'){
            steps{
                script {
                    BUILD_VERSION_GENERATED = VersionNumber(
                        versionNumberString: 'v${BUILD_YEAR, XX}.${BUILD_MONTH, XX}${BUILD_DAY, XX}.${BUILDS_TODAY}',
                        projectStartDate:    '1970-01-01',
                        skipFailedBuilds:    true)
                    currentBuild.displayName = BUILD_VERSION_GENERATED
                    env.BUILD_VERSION = BUILD_VERSION_GENERATED
               }
            }
        }
        stage('Checkout source code') {
            steps {
                cleanWs()
                checkout scm
            }
        }
        stage('Build JupyterHub Docker') {
            when {
                environment name: 'SKIP_BUILD', value: 'false'
                // environment name: 'BUILD_HUB', value: '0'
            }
            steps {
                script {
                    sh 'cp -r deploy/tools/railyard deploy/docker/jupyterhub'
                    dir('deploy/docker/jupyterhub') {
                        docker.withRegistry('https://registry-1.docker.io/v2/', 'f16c74f9-0a60-4882-b6fd-bec3b0136b84') {
                            def image = docker.build('labshare/jupyterhub:latest', '--no-cache ./')
                            image.push()
                            image.push(env.HUB_VERSION)
                        }
                    }
                }
            }
        }
        stage('Assemble Jupyter Notebook Docker files') {
            agent {
                docker {
                    image 'python:3.7'
                    args '--network=host'
                    reuseNode true
                }
            }
            steps {
                script {
                    dir('deploy/tools/railyard') {
                        withEnv(["HOME=${env.WORKSPACE}"]) {
                            sh "pip install -r requirements.txt --user"
                            sh 'pip install . --user'
                            sh '$HOME/.local/bin/railyard assemble stacks/base.yaml manifests'
                            sh '$HOME/.local/bin/railyard assemble stacks/base.yaml stacks/Python-datascience.yaml manifests'
                            sh '$HOME/.local/bin/railyard assemble stacks/base.yaml stacks/R.yaml manifests'
                            sh '$HOME/.local/bin/railyard assemble stacks/base.yaml stacks/julia.yaml manifests'
                            sh '$HOME/.local/bin/railyard assemble stacks/base.yaml stacks/Python-datascience.yaml stacks/R.yaml stacks/julia.yaml manifests'
                            sh '$HOME/.local/bin/railyard assemble stacks/base.yaml stacks/Python-datascience.yaml stacks/Python-dataviz.yaml stacks/R.yaml stacks/java.yaml stacks/scala.yaml stacks/cpp.yaml stacks/julia.yaml stacks/octave.yaml stacks/bash.yaml manifests'
                            sh '$HOME/.local/bin/railyard assemble stacks/base_gpu.yaml manifests'
                            sh '$HOME/.local/bin/railyard assemble stacks/base_gpu.yaml stacks/Python-datascience.yaml stacks/Python-dataviz.yaml stacks/R.yaml stacks/java.yaml stacks/scala.yaml stacks/cpp.yaml stacks/julia.yaml stacks/octave.yaml stacks/bash.yaml stacks/pytorch.yaml stacks/fastai.yaml stacks/tensorflow.yaml manifests'
                            sh 'ls -la manifests/'
                        }
                    }
                }
            }
        }
        stage('Build Jupyter Notebook Docker') {
            when {
                environment name: 'SKIP_BUILD', value: 'false'
                // environment name: 'BUILD_NOTEBOOK', value: '0'
            }
            steps {
                script {
                    sh """echo '{"experimental": "enabled"}' > ~/config.json"""
                    dir('deploy/tools/railyard/manifests') {
                        def files = findFiles(glob: '**/Dockerfile')
                        files.each {
                            def tag = it.path.minus(it.name).minus('/')
                            TAG_EXISTS = sh (
                                script: """docker --config ~/ manifest inspect labshare/polyglot-notebook:${tag} > /dev/null""",
                                returnStatus: true
                            ) == 0

                            println """${TAG_EXISTS}"""

                            if (TAG_EXISTS) {
                                println """Contianer image ${tag} already exists in registry. Skipping building and pushing"""
                            }
                            else {
                                dir("""${tag}""") {
                                    docker.withRegistry('https://registry-1.docker.io/v2/', 'f16c74f9-0a60-4882-b6fd-bec3b0136b84') {
                                        println """Building container image: ${tag}..."""
                                        def image = docker.build("""labshare/polyglot-notebook:${tag}""", '--no-cache ./')
                                        println """Pushing container image: ${tag}..."""
                                        image.push()
                                    }
                                }
                                println """Removing container image: ${tag}"""
                                sh """docker rmi labshare/polyglot-notebook:${tag} -f"""
                            }
                        }
                    }
                }
            }
        }
        stage('Build Notebooks documentation') {
            when {
                environment name: 'SKIP_BUILD', value: 'false'
                environment name: 'BUILD_DOCS', value: '0'
            }
            steps {
                script {
                    sh "mv docs/* deploy/docker/docs"
                    dir('deploy/docker/docs') {
                        docker.withRegistry('https://registry-1.docker.io/v2/', 'f16c74f9-0a60-4882-b6fd-bec3b0136b84') {
                            def image = docker.build('labshare/notebook-docs:latest', '--no-cache ./')
                            image.push()
                            image.push(env.DOCS_VERSION)
                        }
                    }
                }
            }
        }
        stage('Deploy JupyterHub to Kubernetes') {
            steps {
                // Config JSON file is stored in Jenkins and should contain sensitive environment values.                
                configFileProvider([configFile(fileId: 'env-ci', targetLocation: '.env')]) {
                    withAWS(credentials:'aws-jenkins-eks') {
                        sh "aws --region ${AWS_REGION} eks update-kubeconfig --name ${KUBERNETES_CLUSTER_NAME}"
                        sh "./deploy.sh"
                    }
                }
            }
        }
    }
}
