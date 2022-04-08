pipeline {
    agent any

    options {
    //   ansiColor('xterm')
      buildDiscarder(logRotator(numToKeepStr: '20'))
      timeout(time: 30, unit: 'MINUTES')
      timestamps()
    }

    parameters {
        string(name: 'USERNAME', description: 'enter your username!')
        password(name: 'PASSWORD', description: 'enter your password!')
    }

    stages {
        stage("Encode and Store") {
            steps {
                script {
                    // String encode = "${env.USERNAME}:${env.PASSWORD}"
                    // String exit_response= sh(script: "set +x && echo ${encode}|base64", returnStdout: true)
                    // echo "${exit_response}"

                    String username = "${params.USERNAME}"
                    String password = "${params.PASSWORD}"
                    
                    //String token = "${exit_response}"
                    
                    //store-credential.groovy path might change as per your need
                    def instance = load "store-credential.groovy"
                    instance.build(username, password)
                }
            }
        }
    }
}