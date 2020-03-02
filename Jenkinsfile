def mensagemResult = ''
def tagName = 'brazildatacube/oauth:build-' + currentBuild.number

env.tagName = tagName

def checkoutProject() {
    stage('checkout') {
        checkout([
            $class: 'GitSCM',
            branches: [[name: '${ghprbActualCommit}']],
            doGenerateSubmoduleConfigurations: false,
            extensions: [],
            gitTool: 'Default',
            submoduleCfg: [],
            userRemoteConfigs: [[
                name: 'origin',
                refspec: '+refs/pull/*:refs/remotes/origin/pr/*',
                url: 'https://github.com/brazil-data-cube/oauth.git'
            ]]
        ])
    }
}

def prepareEnvironment() {
    stage('prepare-environment') {
        sh 'docker run --name mongo-oauth-test -p 27018:27017 -d -e MONGO_INITDB_ROOT_USERNAME=mongo -e MONGO_INITDB_ROOT_PASSWORD=mongo mongo'
        sh 'docker build --tag ${tagName} -f docker/Dockerfile .'
    }
}

def generateDocs() {
    stage('generate docs') {
        sh 'docker run --rm -i -v $(pwd):/app --name oauth_docs ${tagName} python3 setup.py build_sphinx'
    }
}

def unittest() {
    stage('unittest') {
        sh 'docker run --rm -i --name oauth_test ${tagName} bash -c ./run-test.sh'
    }
}

def notifySlack(String buildStatus = 'STARTED', String mensagem = '') {
    buildStatus = buildStatus ?: 'SUCCESS'

    def color

    if (buildStatus == 'STARTED') {
        color = '#D4DADF'
        mensagem = mensagem ?: 'Iniciado'
    } else if (buildStatus == 'SUCCESS') {
        color = '#BDFFC3'
        mensagem = mensagem ?: 'Finalizado'
    } else if (buildStatus == 'UNSTABLE') {
        color = '#FFFE89'
        mensagem = mensagem ?: 'Travado'
    } else {
        color = '#FF9FA1'
        mensagem = mensagem ?: 'Erro'
    }

    def msg = "${buildStatus}: `${env.JOB_NAME}` #${env.BUILD_NUMBER}:\n${env.BUILD_URL}\n${mensagem}"

    echo "${env}"

    slackSend(color: color, message: msg)
}

def cleanEnvironment() {
    sh 'docker stop mongo-oauth-test'
    sh 'docker rm mongo-oauth-test'
    sh 'docker rmi ${tagName} || exit 0'
}

node("ubuntu-16.04"){
    try {
        checkoutProject()
        notifySlack()

        prepareEnvironment()

        generateDocs()

        unittest()

    } catch (e) {
        currentBuild.result = 'FAILURE'
        mensagemResult = e.toString()
        throw e
    } finally {
        notifySlack(currentBuild.result, mensagemResult)
        cleanEnvironment()
    }
}