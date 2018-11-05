#!groovy

pipeline {

  // agent defines where the pipeline will run.
  agent {  
    label {
      label "install_ibex"
    }
  }
  
  triggers {
    pollSCM('H/2 * * * *')
    upstream(upstreamProjects: 'ibex_gui_pipeline,genie_python_pipeline,	EPICS_IOC_Windows7_x64', threshold: hudson.model.Result.SUCCESS)
  }
  
  stages {  
    stage("Checkout") {
      steps {
        echo "Branch: ${env.BRANCH_NAME}"
        checkout scm
      }
    }
    
    stage("Build") {
      steps {
        bat """
            installation_and_upgrade/instrument_install_latest_build_only.bat
            """
      }
    }
  }
  
  post {
    failure {
      step([$class: 'Mailer', notifyEveryUnstableBuild: true, recipients: 'icp-buildserver@lists.isis.rl.ac.uk', sendToIndividuals: true])
    }
  }
  
  // The options directive is for configuration that applies to the whole job.
  options {
    buildDiscarder(logRotator(numToKeepStr:'5', daysToKeepStr: '7'))
    timeout(time: 90, unit: 'MINUTES')
    disableConcurrentBuilds()
  }
}
