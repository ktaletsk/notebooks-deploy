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
                environment name: 'BUILD_HUB', value: '0'
            }
            steps {
                script {
                    sh 'cp -r deploy/docker/notebook/stacks deploy/docker/jupyterhub'
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
            when {
                environment name: 'SKIP_BUILD', value: 'false'
            }
            agent {
                docker {
                    image 'labshare/polus-railyard:0.3.1'
                    registryUrl 'https://registry-1.docker.io/v2/'
                    registryCredentialsId 'f16c74f9-0a60-4882-b6fd-bec3b0136b84'
                    args '--network=host'
                    reuseNode true
                }
            }
            steps {
                script {
                    dir('deploy/docker/notebook/stacks') {
                        withEnv(["HOME=${env.WORKSPACE}"]) {
                            sh 'mkdir -p manifests'

                            stacks = [
                                ['Python-datascience.yaml', 'Python-dataviz.yaml'],
                                ['R.yaml'],
                                ['octave.yaml'],
                                ['java.yaml', 'scala.yaml'],
                                ['cpp.yaml'],
                                ['bash.yaml'],
                                ['tensorflow.yaml', 'pytorch.yaml', 'fastai.yaml'],
                                ['latex.yaml']
                            ]

                            // CPU-based images
                            // Image without additional stacks
                            sh 'railyard assemble -t Dockerfile.template -b base.yaml -p manifests'

                            // Images with a single additional stack
                            stacks.each {
                                sh "railyard assemble -t Dockerfile.template -b base.yaml " + it.collect{"-a " + it}.join(" ") + " -p manifests"
                            }

                            // Images with combinations of 2 additional stacks
                            [stacks, stacks].combinations().findAll{item -> item[0].join(" ") < item[1].join(" ")}.collect{it.flatten()}.each {
                                sh "railyard assemble -t Dockerfile.template -b base.yaml " + it.collect{"-a " + it}.join(" ") + " -p manifests"
                            }

                            // GPU-based images
                            // Image without additional stacks
                            sh 'railyard assemble -t Dockerfile.template -b base_gpu.yaml -p manifests'

                            // Images with a single additional stack
                            stacks.each {
                                sh "railyard assemble -t Dockerfile.template -b base_gpu.yaml " + it.collect{"-a " + it}.join(" ") + " -p manifests"
                            }

                            // Images with combinations of 2 additional stacks
                            [stacks, stacks].combinations().findAll{item -> item[0].join(" ") < item[1].join(" ")}.collect{it.flatten()}.each {
                                sh "railyard assemble -t Dockerfile.template -b base_gpu.yaml " + it.collect{"-a " + it}.join(" ") + " -p manifests"
                            }
                        }
                    }
                }
            }
        }
        stage('Build Jupyter Notebook Docker') {
            when {
                environment name: 'SKIP_BUILD', value: 'false'
            }
            steps {
                script {
                    sh """echo '{"experimental": "enabled"}' > ~/config.json"""
                    dir('deploy/docker/notebook/stacks/manifests') {
                        def files = findFiles(glob: '**/Dockerfile')
                        files.each {
                            def tag = it.path.minus(it.name).minus('/')
                            TAG_EXISTS = sh (
                                script: """docker --config ~/ manifest inspect labshare/polyglot-notebook:${tag} > /dev/null""",
                                returnStatus: true
                            ) == 0

                            if (TAG_EXISTS) {
                                println """Container image ${tag} already exists in registry. Skipping building and pushing"""
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
        stage('Deploy JupyterHub to AWS CI') {
            steps {
                // Config JSON file is stored in Jenkins and should contain sensitive environment values.
                configFileProvider([configFile(fileId: 'env-ci', targetLocation: '.env')]) {               
                    withAWS(credentials:'aws-jenkins-eks') {
                        sh "aws --region ${AWS_REGION} eks update-kubeconfig --name ${KUBERNETES_CLUSTER_NAME}"

                        sh "bash ./deploy.sh"
                    }
                }
            }
        }
        stage('Deploy JupyterHub to NCATS') {
            agent {
                node { label 'ls-api-ci.ncats' }
            }
            steps {
                configFileProvider([configFile(fileId: 'env-single-node', targetLocation: '.env')]) {
                    withKubeConfig([credentialsId: 'ncats_polus2']) {
                        sh "bash ./deploy.sh"
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                cleanWs()
                sh 'docker system prune -a -f'
            }
        }
    }
}
